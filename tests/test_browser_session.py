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


def _install_fake_mindbody_playwright(
    monkeypatch, *, login_succeeds, site_picker=True, cookie_banner=True
):
    submitted = {"value": False}
    picker = {"visible": site_picker, "searched": False, "selected": False}
    cookies = {"visible": cookie_banner, "dismissed": False}

    class FakeLocator:
        def __init__(self, kind):
            self.kind = kind

        @property
        def first(self):
            return self

        def wait_for(self, *, state, timeout):
            assert state in ("visible", "hidden")
            assert timeout > 0
            if self.kind == "cookie_ok":
                if state == "visible" and not cookies["visible"]:
                    raise TimeoutError("Cookie button not present")
                if state == "hidden" and cookies["visible"]:
                    raise TimeoutError("Cookie banner did not close")
            if self.kind == "site_search":
                assert picker["visible"]
            if self.kind == "site_name":
                assert picker["searched"]
            if self.kind == "email":
                assert not site_picker or picker["selected"]

        def fill(self, value):
            assert value
            if self.kind == "site_search":
                assert value == "Redline"

        def click(self):
            if self.kind == "signin":
                submitted["value"] = True
            if self.kind == "search":
                picker["searched"] = True
            if self.kind == "select":
                picker["selected"] = True
                picker["visible"] = False
            if self.kind == "cookie_ok":
                cookies["dismissed"] = True
                cookies["visible"] = False

        def is_visible(self):
            if self.kind == "cookie_ok":
                return cookies["visible"]
            if self.kind == "site_search":
                return picker["visible"]
            if self.kind == "site_name":
                return picker["searched"] and not picker["selected"]
            if self.kind == "otp":
                return False
            if self.kind == "alert":
                return submitted["value"] and not login_succeeds and picker["selected"] == site_picker
            if self.kind in ("email", "password", "signin"):
                return (
                    (not site_picker or picker["selected"])
                    and (not submitted["value"] or not login_succeeds)
                )
            if self.kind == "search":
                return picker["visible"]
            return False

        def locator(self, selector):
            if selector == "#truste-consent-button":
                return FakeLocator("cookie_ok")
            assert selector.startswith("xpath=ancestor::")
            return self

        def get_by_role(self, role, *, name):
            assert role == "button"
            assert "select" in name.pattern.lower()
            return FakeLocator("select")

    class FakePage:
        url = "https://signin.mindbodyonline.com/"

        def goto(self, url, *, wait_until, timeout):
            assert url == "https://clients.mindbodyonline.com/launch"
            assert wait_until == "domcontentloaded"
            assert timeout > 0

        def get_by_label(self, label):
            assert "email or username" in label.pattern.lower()
            return FakeLocator("email")

        def get_by_text(self, text):
            assert "0045" in text.pattern
            assert "bowie" in text.pattern.lower()
            return FakeLocator("site_name")

        def locator(self, selector):
            if selector == 'input.MuiInputBase-input[aria-invalid="false"][type="text"]':
                return FakeLocator("site_search")
            if selector == "#truste-consent-button":
                return FakeLocator("cookie_ok")
            if selector == 'input[type="password"]':
                return FakeLocator("password")
            if selector.startswith('input[autocomplete="one-time-code"]'):
                return FakeLocator("otp")
            if selector == '[role="alert"]':
                return FakeLocator("alert")
            raise AssertionError(f"Unexpected selector: {selector}")

        def get_by_role(self, role, *, name):
            assert role == "button"
            if "ok" in name.pattern.lower():
                return FakeLocator("cookie_ok")
            if "search" in name.pattern.lower():
                return FakeLocator("search")
            if "select" in name.pattern.lower():
                return FakeLocator("select")
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
        def launch(self, *, headless, args):
            assert headless is False
            assert "--deny-permission-prompts" in args
            return FakeBrowser()

    class FakePlaywright:
        chromium = FakeChromium()

        def __enter__(self):
            return self

        def __exit__(self, *exc_info):
            pass

    sync_api = types.ModuleType("playwright.sync_api")
    sync_api.Error = RuntimeError
    sync_api.TimeoutError = TimeoutError
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
    assert any("Accepted the Mindbody cookie banner" in event.message for event in events)
    assert all("private" not in event.message for event in events)

    session.stop()
    session._thread.join(timeout=2)
    assert not session.is_running


def test_mindbody_login_session_selects_bowie_site_before_sign_in(monkeypatch):
    _install_fake_mindbody_playwright(
        monkeypatch, login_succeeds=True, site_picker=True
    )
    session = MindbodyLoginSession(
        headless=False,
        login_url="https://signin.mindbodyonline.com/",
        email="private@example.test",
        password="private-password",
    )

    session.start()
    events = _collect_until(session, "done")
    messages = [event.message for event in events]
    assert any("searching Redline" in message for message in messages)
    assert any("0045 Redline Athletics - Bowie" in message for message in messages)

    session.stop()
    session._thread.join(timeout=2)
    assert not session.is_running


def test_mindbody_login_session_skips_missing_cookie_banner(monkeypatch):
    _install_fake_mindbody_playwright(
        monkeypatch, login_succeeds=True, cookie_banner=False
    )
    session = MindbodyLoginSession(
        headless=False,
        login_url="https://signin.mindbodyonline.com/",
        email="private@example.test",
        password="private-password",
    )

    session.start()
    events = _collect_until(session, "done")
    assert not any("cookie banner" in event.message for event in events)

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
