"""Playwright browser session lifecycle."""

from __future__ import annotations

import queue
import re
import threading
from dataclasses import dataclass
from urllib.parse import urlparse


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


class MindbodyLoginSession:
    """Use Playwright to test a Mindbody staff login."""

    SITE_PICKER_URL = "https://clients.mindbodyonline.com/launch"

    def __init__(
        self,
        *,
        headless: bool,
        login_url: str,
        email: str,
        password: str,
    ) -> None:
        self.headless = headless
        self.login_url = login_url
        self.email = email
        self.password = password
        self.events: queue.Queue[BrowserSessionEvent] = queue.Queue()
        self._stop_requested = threading.Event()
        self._thread: threading.Thread | None = None

    def start(self) -> None:
        if self._thread is not None:
            raise RuntimeError("A Mindbody login session can only be started once.")

        self._thread = threading.Thread(
            target=self._run,
            name="mindbody-playwright-login",
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
            self._emit("finished", "Mindbody login test ended.")
            return

        if not self.login_url or not self.email or not self.password:
            self._emit(
                "error",
                "Mindbody login settings are incomplete. Set "
                "MINDBODY_LOGIN_URL, MINDBODY_LOGIN_EMAIL, and "
                "MINDBODY_LOGIN_PASSWORD in .env.",
            )
            self._emit("finished", "Mindbody login test ended.")
            return

        try:
            with sync_playwright() as playwright:
                self._emit("working", "Launching Chromium for Mindbody sign-in...")
                browser = playwright.chromium.launch(
                    headless=self.headless,
                    args=["--deny-permission-prompts"],
                )
                try:
                    page = browser.new_page()
                    page.goto(
                        self.SITE_PICKER_URL,
                        wait_until="domcontentloaded",
                        timeout=45_000,
                    )
                    self._dismiss_location_prompt(page)
                    self._accept_cookie_banner(page)
                    self._select_business_site(page)
                    email_input = page.get_by_label(
                        re.compile(r"email or username", re.IGNORECASE)
                    )
                    password_input = page.locator('input[type="password"]').first
                    email_input.wait_for(state="visible", timeout=30_000)
                    password_input.wait_for(state="visible", timeout=30_000)
                    email_input.fill(self.email)
                    password_input.fill(self.password)
                    page.get_by_role(
                        "button", name=re.compile(r"^sign in$", re.IGNORECASE)
                    ).click()
                    self._emit("working", "Credentials submitted; checking Mindbody response...")
                    if self._wait_for_login_result(page, email_input, password_input):
                        self._stop_requested.wait()
                finally:
                    browser.close()
        except PlaywrightError as exc:
            self._emit(
                "error",
                f"Mindbody login test failed: {exc}. Check the login page, "
                "Playwright browser installation, and .env credentials.",
            )
        finally:
            self._emit("finished", "Mindbody login test ended.")

    def _dismiss_location_prompt(self, page) -> None:
        # Chromium's permission prompt is browser chrome, not a page dialog.
        # The launch flag denies it without granting location access.
        self._emit("working", "Location permission prompts are blocked.")

    def _accept_cookie_banner(self, page) -> None:
        accept_button = page.get_by_role(
            "button",
            name=re.compile(r"^ok$", re.IGNORECASE),
        )
        if accept_button.is_visible():
            accept_button.click()
            self._emit("working", "Accepted the Mindbody cookie banner.")

    def _select_business_site(self, page) -> None:
        search_input = page.get_by_placeholder(
            re.compile(r"Mindbody site name or site ID", re.IGNORECASE)
        ).first
        search_input.wait_for(state="visible", timeout=30_000)

        self._emit("working", "Mindbody is asking for a business site; searching Redline...")
        search_input.fill("Redline")
        page.get_by_role(
            "button", name=re.compile(r"^search$", re.IGNORECASE)
        ).click()

        site_name = page.get_by_text(
            re.compile(
                r"0045\s+Redline Athletics\s*[-\u2013\u2014]\s*Bowie",
                re.IGNORECASE,
            )
        ).first
        site_name.wait_for(state="visible", timeout=30_000)
        site_row = site_name.locator(
            "xpath=ancestor::*[.//button[normalize-space()='Select']][1]"
        )
        site_row.get_by_role(
            "button", name=re.compile(r"^select$", re.IGNORECASE)
        ).click()
        self._emit(
            "working",
            "Selected 0045 Redline Athletics - Bowie; waiting for staff sign-in...",
        )

    def _wait_for_login_result(self, page, email_input, password_input) -> bool:
        challenge_reported = False
        remaining = 45.0

        while remaining > 0 and not self._stop_requested.is_set():
            otp_input = page.locator(
                'input[autocomplete="one-time-code"], input[name*="otp"]'
            ).first
            if otp_input.is_visible():
                if not challenge_reported:
                    self._emit(
                        "verification",
                        "Mindbody requires additional verification. Complete it in "
                        "the browser window.",
                    )
                    challenge_reported = True
            else:
                email_visible = email_input.is_visible()
                password_visible = password_input.is_visible()
                page_url = urlparse(page.url)
                login_host = urlparse(self.login_url).hostname
                login_path = urlparse(self.login_url).path.rstrip("/")
                login_button_visible = page.get_by_role(
                    "button", name=re.compile(r"^sign in$", re.IGNORECASE)
                ).is_visible()
                alert = page.locator('[role="alert"]').first
                if alert.is_visible():
                    self._emit(
                        "error",
                        "Mindbody displayed a sign-in error. Check the login "
                        "credentials in .env.",
                    )
                    return False

                if (
                    not email_visible
                    and not password_visible
                    and not login_button_visible
                    and (
                        page_url.hostname != login_host
                        or page_url.path.rstrip("/") != login_path
                    )
                ):
                    self._emit("done", "Mindbody sign-in succeeded.")
                    return True

            if self._stop_requested.wait(0.5):
                return False
            remaining -= 0.5

        if not self._stop_requested.is_set():
            self._emit(
                "error",
                "Mindbody did not confirm sign-in within 45 seconds. Check the "
                "browser for a verification prompt or sign-in error.",
            )
        return False
