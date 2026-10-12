"""Playwright browser session lifecycle."""

from __future__ import annotations

import queue
import threading
from dataclasses import dataclass


@dataclass(frozen=True)
class BrowserSessionEvent:
    """An event emitted by a browser session worker."""

    kind: str
    message: str


class BrowserSession:
    """Own a Playwright browser in a worker thread until stopped."""

    def __init__(self, *, headless: bool) -> None:
        self.headless = headless
        self.events: queue.Queue[BrowserSessionEvent] = queue.Queue()
        self._stop_requested = threading.Event()
        self._thread: threading.Thread | None = None

    def start(self) -> None:
        if self._thread is not None:
            raise RuntimeError("A browser session can only be started once.")

        self._thread = threading.Thread(
            target=self._run,
            name="playwright-browser-session",
        )
        self._thread.start()

    def stop(self) -> None:
        self._stop_requested.set()

    @property
    def is_running(self) -> bool:
        return self._thread is not None and self._thread.is_alive()

    def _emit(self, kind: str, message: str) -> None:
        self.events.put(BrowserSessionEvent(kind=kind, message=message))

    def _run(self) -> None:
        try:
            from playwright.sync_api import Error as PlaywrightError
            from playwright.sync_api import sync_playwright
        except ImportError:
            self._emit(
                "error",
                'Playwright is not installed. Install it with '
                '`py -m pip install -e ".[browser]"`.',
            )
            self._emit("finished", "Browser session ended.")
            return

        try:
            with sync_playwright() as playwright:
                self._emit("log", "Starting Chromium...")
                browser = playwright.chromium.launch(headless=self.headless)
                try:
                    context = browser.new_context()
                    try:
                        context.new_page()
                        mode = "headless" if self.headless else "visible"
                        self._emit(
                            "ready",
                            f"Chromium started in {mode} mode with a blank tab.",
                        )
                        self._stop_requested.wait()
                    finally:
                        context.close()
                finally:
                    browser.close()
        except PlaywrightError as exc:
            self._emit("error", f"Could not start or stop Chromium: {exc}")
        finally:
            self._emit("finished", "Browser session ended.")
