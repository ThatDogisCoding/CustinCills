import sys
import time
import types

from business_report.services.browser_session import BrowserSession


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
