import sys
import time
import types

from business_report.services.browser_session import BrowserSession, MindbodyLoginSession


def _install_fake_playwright(monkeypatch, calls):
    class FakeContext:
        def new_page(self):
            calls.append("new_page")

        def close(self):
            calls.append("context.close")

    class FakeBrowser:
        def new_context(self):
            calls.append("new_context")
            return FakeContext()

        def close(self):
            calls.append("browser.close")

    class FakeChromium:
        def launch(self, *, headless):
            calls.append(("launch", headless))
            return FakeBrowser()

    class FakePlaywright:
        chromium = FakeChromium()

        def __enter__(self):
            return self

        def __exit__(self, *exc_info):
            calls.append("playwright.stop")

    sync_api = types.ModuleType("playwright.sync_api")
    sync_api.Error = RuntimeError
    sync_api.sync_playwright = FakePlaywright
    monkeypatch.setitem(sys.modules, "playwright", types.ModuleType("playwright"))
    monkeypatch.setitem(sys.modules, "playwright.sync_api", sync_api)


def test_browser_session_starts_blank_browser_and_closes_on_stop(monkeypatch):
    calls = []
    _install_fake_playwright(monkeypatch, calls)
    session = BrowserSession(headless=False)

    session.start()
    ready_event = session.events.get(timeout=2)
    while ready_event.kind != "ready":
        ready_event = session.events.get(timeout=2)

    assert "visible mode" in ready_event.message
    assert ("launch", False) in calls
    assert "new_page" in calls
    assert session.is_running

    session.stop()
    deadline = time.monotonic() + 2
    while session.is_running and time.monotonic() < deadline:
        time.sleep(0.01)

    assert not session.is_running
    remaining_events = []
    while not session.events.empty():
        remaining_events.append(session.events.get_nowait())
    assert any(event.kind == "finished" for event in remaining_events)
    assert "context.close" in calls
    assert "browser.close" in calls
    assert "playwright.stop" in calls


def test_browser_session_reports_missing_playwright(monkeypatch):
    monkeypatch.setitem(sys.modules, "playwright", None)
    session = BrowserSession(headless=True)

    session.start()
    events = [session.events.get(timeout=2), session.events.get(timeout=2)]

    assert events[0].kind == "error"
    assert "Playwright is not installed" in events[0].message
    assert events[1].kind == "finished"


def _install_fake_mindbody_playwright(monkeypatch, *, login_succeeds):
    submitted = {"value": False}

    class FakeLocator:
        def __init__(self, kind):
            self.kind = kind

        @property
        def first(self):
            return self

        def wait_for(self, *, state, timeout):
            assert state == "visible"
            assert timeout > 0

        def fill(self, value):
            assert value

        def click(self):
            submitted["value"] = True

        def is_visible(self):
            if self.kind == "otp":
                return False
            if self.kind == "alert":
                return submitted["value"] and not login_succeeds
            if self.kind in ("email", "password", "signin"):
                return not submitted["value"] or not login_succeeds
            return False

    class FakePage:
        url = "https://signin.mindbodyonline.com/"

        def goto(self, url, *, wait_until, timeout):
            assert url.startswith("https://")
            assert wait_until == "domcontentloaded"
            assert timeout > 0

        def get_by_label(self, label):
            assert "email or username" in label.pattern.lower()
            return FakeLocator("email")

        def locator(self, selector):
            if selector == 'input[type="password"]':
                return FakeLocator("password")
            if selector.startswith('input[autocomplete="one-time-code"]'):
                return FakeLocator("otp")
            if selector == '[role="alert"]':
                return FakeLocator("alert")
            raise AssertionError(f"Unexpected selector: {selector}")

        def get_by_role(self, role, *, name):
            assert role == "button"
            assert "sign in" in name.pattern.lower()
            locator = FakeLocator("signin")
            original_click = locator.click

            def click():
                original_click()
                if login_succeeds:
                    self.url = "https://clients.mindbodyonline.com/"

            locator.click = click
            return locator

    class FakeBrowser:
        def new_page(self):
            return FakePage()

        def close(self):
            pass

    class FakeChromium:
        def launch(self, *, headless):
            assert headless is False
            return FakeBrowser()

    class FakePlaywright:
        chromium = FakeChromium()

        def __enter__(self):
            return self

        def __exit__(self, *exc_info):
            pass

    sync_api = types.ModuleType("playwright.sync_api")
    sync_api.Error = RuntimeError
    sync_api.sync_playwright = FakePlaywright
    monkeypatch.setitem(sys.modules, "playwright", types.ModuleType("playwright"))
    monkeypatch.setitem(sys.modules, "playwright.sync_api", sync_api)


def _collect_until(session, expected_kind):
    events = []
    deadline = time.monotonic() + 2
    while time.monotonic() < deadline:
        event = session.events.get(timeout=2)
        events.append(event)
        if event.kind == expected_kind:
            return events
    raise AssertionError(f"Did not receive {expected_kind} event")


def test_mindbody_login_session_reports_success_without_logging_credentials(monkeypatch):
    _install_fake_mindbody_playwright(monkeypatch, login_succeeds=True)
    session = MindbodyLoginSession(
        headless=False,
        login_url="https://signin.mindbodyonline.com/",
        email="private@example.test",
        password="private-password",
    )

    session.start()
    events = _collect_until(session, "done")
    assert any("succeeded" in event.message for event in events)
    assert all("private" not in event.message for event in events)

    session.stop()
    session._thread.join(timeout=2)
    assert not session.is_running


def test_mindbody_login_session_reports_login_error(monkeypatch):
    _install_fake_mindbody_playwright(monkeypatch, login_succeeds=False)
    session = MindbodyLoginSession(
        headless=False,
        login_url="https://signin.mindbodyonline.com/",
        email="private@example.test",
        password="private-password",
    )

    session.start()
    events = _collect_until(session, "error")
    assert "Check the login credentials in .env" in events[-1].message
    assert "private" not in events[-1].message

    session._thread.join(timeout=2)
    assert not session.is_running
