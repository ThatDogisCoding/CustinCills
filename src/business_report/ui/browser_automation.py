"""Browser automation window for testing Mindbody staff login with Playwright."""

from __future__ import annotations

import tkinter as tk
from queue import Empty
from tkinter import ttk

from business_report.config import get_settings
from business_report.services.browser_session import MindbodyLoginSession

# Re-use brand palette from the main app
COLOR_BG = "#E8E8E8"
COLOR_PANEL = "#FFFFFF"
COLOR_RED = "#E31837"
COLOR_RED_ACTIVE = "#C41230"
COLOR_TEXT = "#1A1A1A"
COLOR_MUTED = "#6B7280"
COLOR_BORDER = "#D1D5DB"
COLOR_GREEN = "#16A34A"
COLOR_AMBER = "#D97706"
FONT = "Segoe UI"


class BrowserAutomationWindow(tk.Toplevel):
    """Pop-up window for managing Playwright browser automation tasks."""

    WIDTH = 820
    HEIGHT = 640

    def __init__(self, parent: tk.Tk) -> None:
        super().__init__(parent)
        self.title("Browser Automation — Mindbody Login Test")
        self.geometry(f"{self.WIDTH}x{self.HEIGHT}")
        self.minsize(700, 520)
        self.configure(bg=COLOR_BG)
        self.resizable(True, True)

        # Prevent multiple instances
        self.transient(parent)
        self.grab_set()

        self._session: MindbodyLoginSession | None = None
        self._poll_after_id: str | None = None
        self._close_requested = False
        self._session_failed = False
        self._stopping = False
        self.protocol("WM_DELETE_WINDOW", self._on_close)
        parent.bind("<Destroy>", self._on_parent_destroy, add="+")

        self._build_ui()

    # ── UI construction ──────────────────────────────────────────────

    def _build_ui(self) -> None:
        self._build_header()
        self._build_target_panel()
        self._build_log_panel()
        self._build_footer()

    def _build_header(self) -> None:
        header = tk.Frame(self, bg=COLOR_PANEL, pady=14, padx=24)
        header.pack(fill="x")

        tk.Label(
            header,
            text="🌐",
            font=(FONT, 20),
            bg=COLOR_PANEL,
        ).pack(side="left", padx=(0, 10))

        title_block = tk.Frame(header, bg=COLOR_PANEL)
        title_block.pack(side="left", fill="x", expand=True)

        tk.Label(
            title_block,
            text="BROWSER AUTOMATION",
            font=(FONT, 14, "bold"),
            fg=COLOR_RED,
            bg=COLOR_PANEL,
            anchor="w",
        ).pack(fill="x")

        tk.Label(
            title_block,
            text="Test the Mindbody staff login with Playwright.",
            font=(FONT, 10),
            fg=COLOR_MUTED,
            bg=COLOR_PANEL,
            anchor="w",
        ).pack(fill="x")

        self.status_indicator = tk.Label(
            header,
            text="● Idle",
            font=(FONT, 10, "bold"),
            fg=COLOR_MUTED,
            bg=COLOR_PANEL,
        )
        self.status_indicator.pack(side="right")

    def _build_target_panel(self) -> None:
        wrapper = tk.Frame(self, bg=COLOR_BG, padx=24, pady=(12, 0))
        wrapper.pack(fill="x")

        panel = tk.Frame(
            wrapper,
            bg=COLOR_PANEL,
            padx=20,
            pady=16,
            highlightthickness=1,
            highlightbackground=COLOR_BORDER,
        )
        panel.pack(fill="x")

        tk.Label(
            panel,
            text="MINDBODY LOGIN TARGET",
            font=(FONT, 10, "bold"),
            fg=COLOR_TEXT,
            bg=COLOR_PANEL,
            anchor="w",
        ).pack(fill="x", pady=(0, 12))

        tk.Label(
            panel,
            text="Check that the Mindbody staff credentials in .env can sign in.",
            font=(FONT, 10),
            fg=COLOR_MUTED,
            bg=COLOR_PANEL,
            anchor="w",
        ).pack(fill="x", pady=(0, 12))

        self.run_btn = tk.Button(
            panel,
            text="▶  TEST MINDBODY LOGIN",
            font=(FONT, 13, "bold"),
            fg="white",
            bg=COLOR_RED,
            activebackground=COLOR_RED_ACTIVE,
            activeforeground="white",
            relief="flat",
            cursor="hand2",
            padx=18,
            pady=12,
            command=self._on_run,
        )
        self.run_btn.pack(fill="x", pady=(0, 12))

        options_row = tk.Frame(panel, bg=COLOR_PANEL)
        options_row.pack(fill="x")
        tk.Label(
            options_row,
            text="Headless mode:",
            font=(FONT, 10),
            fg=COLOR_MUTED,
            bg=COLOR_PANEL,
        ).pack(side="left")

        self.headless_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(
            options_row,
            variable=self.headless_var,
        ).pack(side="left", padx=(6, 20))

        self.stop_btn = tk.Button(
            options_row,
            text="■  Stop",
            font=(FONT, 11, "bold"),
            fg="white",
            bg=COLOR_MUTED,
            activebackground="#4B5563",
            activeforeground="white",
            relief="flat",
            cursor="hand2",
            padx=18,
            pady=8,
            state="disabled",
            command=self._on_stop,
        )
        self.stop_btn.pack(side="right")

    def _build_log_panel(self) -> None:
        wrapper = tk.Frame(self, bg=COLOR_BG, padx=24, pady=12)
        wrapper.pack(fill="both", expand=True)

        panel = tk.Frame(
            wrapper,
            bg=COLOR_PANEL,
            padx=16,
            pady=12,
            highlightthickness=1,
            highlightbackground=COLOR_BORDER,
        )
        panel.pack(fill="both", expand=True)

        header_row = tk.Frame(panel, bg=COLOR_PANEL)
        header_row.pack(fill="x", pady=(0, 8))

        tk.Label(
            header_row,
            text="ACTIVITY LOG",
            font=(FONT, 10, "bold"),
            fg=COLOR_TEXT,
            bg=COLOR_PANEL,
            anchor="w",
        ).pack(side="left")

        tk.Button(
            header_row,
            text="Clear",
            font=(FONT, 9),
            fg=COLOR_MUTED,
            bg=COLOR_PANEL,
            bd=0,
            cursor="hand2",
            command=self._clear_log,
        ).pack(side="right")

        self.log_text = tk.Text(
            panel,
            font=("Consolas", 10),
            bg="#1E1E1E",
            fg="#D4D4D4",
            insertbackground="#D4D4D4",
            relief="flat",
            wrap="word",
            state="disabled",
            height=10,
        )
        self.log_text.pack(fill="both", expand=True)

        # Configure colored tags for log messages
        self.log_text.tag_configure("info", foreground="#D4D4D4")
        self.log_text.tag_configure("success", foreground=COLOR_GREEN)
        self.log_text.tag_configure("warning", foreground=COLOR_AMBER)
        self.log_text.tag_configure("error", foreground="#EF4444")
        self.log_text.tag_configure("header", foreground=COLOR_RED, font=("Consolas", 10, "bold"))

        self._log("Ready. Click TEST MINDBODY LOGIN to check the staff sign-in.", "info")

    def _build_footer(self) -> None:
        footer = tk.Frame(self, bg=COLOR_BG, padx=24, pady=(0, 14))
        footer.pack(fill="x")

        tk.Label(
            footer,
            text="Login credentials are read from .env. A visible browser is used by default.",
            font=(FONT, 9),
            fg=COLOR_MUTED,
            bg=COLOR_BG,
            anchor="w",
        ).pack(side="left")

        tk.Button(
            footer,
            text="Close",
            font=(FONT, 10),
            fg=COLOR_TEXT,
            bg=COLOR_PANEL,
            relief="flat",
            cursor="hand2",
            padx=16,
            pady=6,
            command=self._on_close,
        ).pack(side="right")

    # ── Actions ──────────────────────────────────────────────────────

    def _on_run(self) -> None:
        if self._session is not None and self._session.is_running:
            return

        settings = get_settings()
        if not all(
            (
                settings.mindbody_login_url,
                settings.mindbody_login_email,
                settings.mindbody_login_password,
            )
        ):
            self._session_failed = True
            self._log(
                "Mindbody login settings are incomplete. Set "
                "MINDBODY_LOGIN_URL, MINDBODY_LOGIN_EMAIL, and "
                "MINDBODY_LOGIN_PASSWORD in .env.",
                "error",
            )
            self.status_indicator.configure(text="● Error", fg="#EF4444")
            return

        headless = self.headless_var.get()
        self._session = MindbodyLoginSession(
            headless=headless,
            login_url=settings.mindbody_login_url,
            email=settings.mindbody_login_email,
            password=settings.mindbody_login_password,
        )
        self._session_failed = False
        self._stopping = False
        self.run_btn.configure(state="disabled")
        self.stop_btn.configure(state="normal", bg="#EF4444")
        self.status_indicator.configure(text="● Starting", fg=COLOR_AMBER)

        self._log("", "info")
        mode = "headless" if headless else "visible"
        self._log(f"═══ Testing Mindbody login ({mode}) ═══", "header")
        self._log("Opening the configured Mindbody sign-in page...", "info")
        self._log("", "info")
        try:
            self._session.start()
        except RuntimeError as exc:
            self._session_failed = True
            self._log(f"Could not start browser session: {exc}", "error")
            self._reset_controls()
            return
        self._schedule_session_poll()

    def _on_stop(self) -> None:
        if self._session is None or not self._session.is_running:
            return
        self._stopping = True
        self._log("Stopping browser session...", "warning")
        self.stop_btn.configure(state="disabled")
        self.status_indicator.configure(text="● Stopping", fg=COLOR_AMBER)
        self._session.stop()

    def _reset_controls(self) -> None:
        self.run_btn.configure(state="disabled" if self._close_requested else "normal")
        self.stop_btn.configure(state="disabled", bg=COLOR_MUTED)
        status = "● Error" if self._session_failed else "● Idle"
        color = "#EF4444" if self._session_failed else COLOR_MUTED
        self.status_indicator.configure(text=status, fg=color)
        if self._close_requested:
            self.destroy()

    def _schedule_session_poll(self) -> None:
        if self._poll_after_id is None:
            self._poll_after_id = self.after(100, self._poll_session)

    def _poll_session(self) -> None:
        self._poll_after_id = None
        session = self._session
        if session is None:
            return

        while True:
            try:
                event = session.events.get_nowait()
            except Empty:
                break
            if event.kind == "error":
                self._session_failed = True
                self._log(event.message, "error")
                if not self._stopping:
                    self.status_indicator.configure(text="● Error", fg="#EF4444")
            elif event.kind == "done":
                if not self._stopping:
                    self.status_indicator.configure(text="● Done", fg=COLOR_GREEN)
                self._log(event.message, "success")
            elif event.kind == "verification":
                if not self._stopping:
                    self.status_indicator.configure(text="● Verify", fg=COLOR_AMBER)
                self._log(event.message, "warning")
            elif event.kind == "working":
                if not self._stopping:
                    self.status_indicator.configure(text="● Working", fg=COLOR_AMBER)
                self._log(event.message, "info")
            elif event.kind == "finished":
                self._log(event.message, "info")
            else:
                self._log(event.message, "info")

        if not session.is_running:
            self._session = None
            self._reset_controls()
            return
        self._schedule_session_poll()

    def _on_close(self) -> None:
        self._close_requested = True
        if self._session is not None and self._session.is_running:
            self._stopping = True
            self._log("Closing browser before closing this window...", "warning")
            self.run_btn.configure(state="disabled")
            self.stop_btn.configure(state="disabled")
            self.status_indicator.configure(text="● Stopping", fg=COLOR_AMBER)
            self._session.stop()
            self._schedule_session_poll()
            return
        self.destroy()

    def _on_parent_destroy(self, event: tk.Event) -> None:
        if event.widget is self.master and self._session is not None:
            self._session.stop()

    # ── Logging helpers ──────────────────────────────────────────────

    def _log(self, message: str, tag: str = "info") -> None:
        self.log_text.configure(state="normal")
        self.log_text.insert("end", message + "\n", tag)
        self.log_text.see("end")
        self.log_text.configure(state="disabled")

    def _clear_log(self) -> None:
        self.log_text.configure(state="normal")
        self.log_text.delete("1.0", "end")
        self.log_text.configure(state="disabled")
        self._log("Log cleared.", "info")
