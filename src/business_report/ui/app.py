"""Redline Athletics weekly data review dashboard (Tkinter)."""

from __future__ import annotations

import json
import os
import subprocess
import sys
import tkinter as tk
from pathlib import Path
from tkinter import filedialog, messagebox, ttk

from dotenv import load_dotenv

from business_report.config import ReportingPeriod, get_settings
from business_report.ui.demo_metrics import display_value, metrics_for_period
from business_report.ui.week_list import WeekListEntry, recent_weeks

# Brand palette (from Redline mockup)
COLOR_BG = "#E8E8E8"
COLOR_PANEL = "#FFFFFF"
COLOR_RED = "#E31837"
COLOR_RED_ACTIVE = "#C41230"
COLOR_TEXT = "#1A1A1A"
COLOR_MUTED = "#6B7280"
COLOR_BORDER = "#D1D5DB"
COLOR_CARD = "#F3F4F6"
FONT = "Segoe UI"


class RedlineDashboardApp(tk.Tk):
    WINDOW_WIDTH = 1320
    WINDOW_HEIGHT = 880
    MIN_WIDTH = 1100
    MIN_HEIGHT = 720

    def __init__(self) -> None:
        super().__init__()
        load_dotenv()
        self.settings = get_settings()
        self.settings.ensure_output_dir()

        self.title("Redline Athletics — Weekly Business Snapshot")
        self.geometry(f"{self.WINDOW_WIDTH}x{self.WINDOW_HEIGHT}")
        self.minsize(self.MIN_WIDTH, self.MIN_HEIGHT)
        self.configure(bg=COLOR_BG)

        self.week_entries = recent_weeks(14)
        self.selected_index = 0
        self.week_buttons: list[tk.Frame] = []
        self.metric_value_labels: list[tk.Label] = []

        self._user_display = os.getenv("APP_USER_NAME", "John Doe")
        self._user_initials = self._initials(self._user_display)

        self._build_header()
        self._build_body()
        self.select_week(0)

    @staticmethod
    def _initials(name: str) -> str:
        parts = [p for p in name.split() if p]
        if not parts:
            return "?"
        if len(parts) == 1:
            return parts[0][:2].upper()
        return (parts[0][0] + parts[-1][0]).upper()

    def _build_header(self) -> None:
        header = tk.Frame(self, bg=COLOR_BG, pady=16)
        header.pack(fill="x", padx=28, pady=(12, 0))

        left = tk.Frame(header, bg=COLOR_BG, width=200)
        left.pack(side="left")

        center = tk.Frame(header, bg=COLOR_BG)
        center.pack(side="left", expand=True)

        logo_row = tk.Frame(center, bg=COLOR_BG)
        logo_row.pack()
        tk.Label(
            logo_row,
            text="▶▶",
            font=(FONT, 22, "bold"),
            fg=COLOR_RED,
            bg=COLOR_BG,
        ).pack(side="left", padx=(0, 8))
        tk.Label(
            logo_row,
            text="REDLINE",
            font=(FONT, 26, "bold"),
            fg=COLOR_TEXT,
            bg=COLOR_BG,
        ).pack(side="left")
        tk.Label(
            logo_row,
            text="ATHLETICS",
            font=(FONT, 26, "bold"),
            fg=COLOR_RED,
            bg=COLOR_BG,
        ).pack(side="left", padx=(6, 0))

        user = tk.Frame(header, bg=COLOR_BG)
        user.pack(side="right")

        avatar = tk.Label(
            user,
            text=self._user_initials,
            font=(FONT, 11, "bold"),
            fg="white",
            bg=COLOR_RED,
            width=3,
            height=1,
        )
        avatar.pack(side="left", padx=(0, 10))
        tk.Label(
            user,
            text=self._user_display,
            font=(FONT, 11),
            fg=COLOR_MUTED,
            bg=COLOR_BG,
        ).pack(side="left", padx=(0, 8))
        tk.Button(
            user,
            text="⚙",
            font=(FONT, 14),
            fg=COLOR_MUTED,
            bg=COLOR_BG,
            bd=0,
            cursor="hand2",
            command=self._on_settings,
        ).pack(side="left")

    def _build_body(self) -> None:
        body = tk.Frame(self, bg=COLOR_BG)
        body.pack(fill="both", expand=True, padx=28, pady=20)

        self.sidebar = tk.Frame(body, bg=COLOR_PANEL, highlightthickness=1, highlightbackground=COLOR_BORDER)
        self.sidebar.pack(side="left", fill="y", padx=(0, 16))
        self.sidebar.pack_propagate(False)
        self.sidebar.configure(width=320)

        self.main_panel = tk.Frame(body, bg=COLOR_PANEL, highlightthickness=1, highlightbackground=COLOR_BORDER)
        self.main_panel.pack(side="left", fill="both", expand=True)

        self._build_sidebar()
        self._build_main_panel()

    def _build_sidebar(self) -> None:
        pad = tk.Frame(self.sidebar, bg=COLOR_PANEL, padx=20, pady=22)
        pad.pack(fill="both", expand=True)

        tk.Label(
            pad,
            text="WEEKLY REVIEWS",
            font=(FONT, 13, "bold"),
            fg=COLOR_TEXT,
            bg=COLOR_PANEL,
            anchor="w",
        ).pack(fill="x")
        tk.Label(
            pad,
            text="Browse performance summaries by week.",
            font=(FONT, 10),
            fg=COLOR_MUTED,
            bg=COLOR_PANEL,
            anchor="w",
            wraplength=260,
            justify="left",
        ).pack(fill="x", pady=(6, 16))

        canvas = tk.Canvas(pad, bg=COLOR_PANEL, highlightthickness=0, bd=0)
        scrollbar = ttk.Scrollbar(pad, orient="vertical", command=canvas.yview)
        self.week_list_frame = tk.Frame(canvas, bg=COLOR_PANEL)

        self.week_list_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all")),
        )
        canvas.create_window((0, 0), window=self.week_list_frame, anchor="nw", width=268)
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        for i, entry in enumerate(self.week_entries):
            self.week_buttons.append(self._create_week_row(self.week_list_frame, entry, i))

    def _create_week_row(self, parent: tk.Frame, entry: WeekListEntry, index: int) -> tk.Frame:
        row = tk.Frame(parent, bg=COLOR_PANEL, cursor="hand2")
        row.pack(fill="x", pady=5)

        inner = tk.Frame(row, bg=COLOR_PANEL, padx=14, pady=12, highlightthickness=1, highlightbackground=COLOR_BORDER)
        inner.pack(fill="x")
        inner.bind("<Button-1>", lambda _e, idx=index: self.select_week(idx))
        row.bind("<Button-1>", lambda _e, idx=index: self.select_week(idx))

        title = tk.Label(
            inner,
            text=entry.title,
            font=(FONT, 11, "bold"),
            fg=COLOR_TEXT,
            bg=COLOR_PANEL,
            anchor="w",
        )
        title.pack(fill="x")
        title.bind("<Button-1>", lambda _e, idx=index: self.select_week(idx))

        sub = tk.Label(
            inner,
            text=entry.subtitle,
            font=(FONT, 9),
            fg=COLOR_MUTED,
            bg=COLOR_PANEL,
            anchor="w",
        )
        sub.pack(fill="x", pady=(2, 0))
        sub.bind("<Button-1>", lambda _e, idx=index: self.select_week(idx))

        chevron = tk.Label(inner, text="›", font=(FONT, 16, "bold"), fg=COLOR_MUTED, bg=COLOR_PANEL)
        chevron.place(relx=1.0, rely=0.5, anchor="e")
        chevron.bind("<Button-1>", lambda _e, idx=index: self.select_week(idx))

        row._inner = inner  # type: ignore[attr-defined]
        row._title = title  # type: ignore[attr-defined]
        row._sub = sub  # type: ignore[attr-defined]
        row._chevron = chevron  # type: ignore[attr-defined]
        return row

    def _build_main_panel(self) -> None:
        content = tk.Frame(self.main_panel, bg=COLOR_PANEL, padx=36, pady=32)
        content.pack(fill="both", expand=True)

        tk.Label(
            content,
            text="WEEKLY DATA REVIEW",
            font=(FONT, 11, "bold"),
            fg=COLOR_RED,
            bg=COLOR_PANEL,
            anchor="w",
        ).pack(fill="x")

        self.period_title = tk.Label(
            content,
            text="",
            font=(FONT, 28, "bold"),
            fg=COLOR_TEXT,
            bg=COLOR_PANEL,
            anchor="w",
        )
        self.period_title.pack(fill="x", pady=(8, 6))

        self.period_description = tk.Label(
            content,
            text="A clean summary of business performance for the selected week "
            "(Mindbody, GoHighLevel, and Axle).",
            font=(FONT, 11),
            fg=COLOR_MUTED,
            bg=COLOR_PANEL,
            anchor="w",
            wraplength=820,
            justify="left",
        )
        self.period_description.pack(fill="x", pady=(0, 28))

        grid = tk.Frame(content, bg=COLOR_PANEL)
        grid.pack(fill="x")
        grid.columnconfigure(0, weight=1)
        grid.columnconfigure(1, weight=1)

        self.metric_value_labels = []
        cards = [
            ("FREE TRIALS SCHEDULED", "Scheduled trials this week (GoHighLevel)."),
            ("SHOW RATE", "Showed ÷ scheduled for the week."),
            ("ACTIVE MEMBERS", "Total active members (Mindbody)."),
            ("TERMINATIONS", "Members terminated during the week."),
        ]
        for i, (title, subtitle) in enumerate(cards):
            r, c = divmod(i, 2)
            card, value_lbl = self._metric_card(grid, title, subtitle)
            card.grid(row=r, column=c, sticky="nsew", padx=(0, 12 if c == 0 else 0), pady=(0, 14))
            self.metric_value_labels.append(value_lbl)

        tk.Frame(content, bg=COLOR_BORDER, height=1).pack(fill="x", pady=(24, 20))

        actions = tk.Frame(content, bg=COLOR_PANEL)
        actions.pack(fill="x")
        actions.columnconfigure(0, weight=1)
        actions.columnconfigure(1, weight=1)

        self._action_button(actions, "Edit Spreadsheet", self._on_edit_spreadsheet).grid(
            row=0, column=0, sticky="ew", padx=(0, 10)
        )
        self._action_button(actions, "Export Data", self._on_export_data).grid(
            row=0, column=1, sticky="ew", padx=(10, 0)
        )

        self.data_status = tk.Label(
            content,
            text="",
            font=(FONT, 9),
            fg=COLOR_MUTED,
            bg=COLOR_PANEL,
            anchor="w",
        )
        self.data_status.pack(fill="x", pady=(16, 0))

    def _metric_card(self, parent: tk.Frame, title: str, subtitle: str) -> tuple[tk.Frame, tk.Label]:
        card = tk.Frame(parent, bg=COLOR_CARD, padx=22, pady=20)
        tk.Label(
            card,
            text=title,
            font=(FONT, 9, "bold"),
            fg=COLOR_RED,
            bg=COLOR_CARD,
            anchor="w",
        ).pack(fill="x")
        value = tk.Label(
            card,
            text="—",
            font=(FONT, 32, "bold"),
            fg=COLOR_TEXT,
            bg=COLOR_CARD,
            anchor="w",
        )
        value.pack(fill="x", pady=(10, 8))
        tk.Label(
            card,
            text=subtitle,
            font=(FONT, 10),
            fg=COLOR_MUTED,
            bg=COLOR_CARD,
            anchor="w",
            wraplength=360,
            justify="left",
        ).pack(fill="x")
        return card, value

    def _action_button(self, parent: tk.Frame, text: str, command) -> tk.Button:
        btn = tk.Button(
            parent,
            text=text,
            font=(FONT, 12, "bold"),
            fg="white",
            bg=COLOR_RED,
            activebackground=COLOR_RED_ACTIVE,
            activeforeground="white",
            relief="flat",
            cursor="hand2",
            padx=20,
            pady=14,
            command=command,
        )
        return btn

    def select_week(self, index: int) -> None:
        self.selected_index = index
        for i, row in enumerate(self.week_buttons):
            active = i == index
            bg = COLOR_RED if active else COLOR_PANEL
            fg_title = "white" if active else COLOR_TEXT
            fg_sub = "#FECACA" if active else COLOR_MUTED
            fg_chev = "white" if active else COLOR_MUTED
            border = COLOR_RED if active else COLOR_BORDER

            inner = row._inner  # type: ignore[attr-defined]
            inner.configure(bg=bg, highlightbackground=border)
            row._title.configure(bg=bg, fg=fg_title)  # type: ignore[attr-defined]
            row._sub.configure(bg=bg, fg=fg_sub)  # type: ignore[attr-defined]
            row._chevron.configure(bg=bg, fg=fg_chev)  # type: ignore[attr-defined]

        entry = self.week_entries[index]
        self._refresh_metrics(entry.period)

    def _refresh_metrics(self, period: ReportingPeriod) -> None:
        start, end = period.start, period.end
        self.period_title.configure(text=f"Week of {start.strftime('%b')} {start.day} - {end.strftime('%b')} {end.day}")

        metrics = metrics_for_period(period)
        values = [
            display_value(metrics.free_trials_scheduled),
            metrics.show_rate or "—",
            display_value(metrics.active_members),
            display_value(metrics.terminations),
        ]
        for label, text in zip(self.metric_value_labels, values):
            label.configure(text=text)

        if metrics.has_live_data:
            self.data_status.configure(
                text="Showing baseline snapshot data for this week. Live API sync will replace this in a later phase."
            )
        else:
            self.data_status.configure(
                text="No snapshot data for this week yet. Connect Mindbody, GoHighLevel, and Axle to populate metrics."
            )

    def _spreadsheet_path(self, period: ReportingPeriod) -> Path:
        name = f"Weekly Business Snapshot_{period.start.year} - Week of {period.start.month}_{period.start.day}_{period.start.year}.xlsx"
        return self.settings.output_dir / name

    def _on_edit_spreadsheet(self) -> None:
        period = self.week_entries[self.selected_index].period
        path = self._spreadsheet_path(period)
        if path.is_file():
            self._open_path(path)
            return
        messagebox.showinfo(
            "Spreadsheet not found",
            f"No workbook saved yet for this week.\n\nExpected path:\n{path}\n\n"
            "Excel generation will create this file in a future phase.",
        )

    def _on_export_data(self) -> None:
        period = self.week_entries[self.selected_index].period
        metrics = metrics_for_period(period)
        payload = {
            "period_start": period.start.isoformat(),
            "period_end": period.end.isoformat(),
            "metrics": {
                "free_trials_scheduled": metrics.free_trials_scheduled,
                "show_rate": metrics.show_rate,
                "active_members": metrics.active_members,
                "terminations": metrics.terminations,
                "free_trials_showed": metrics.free_trials_showed,
                "free_trials_sold": metrics.free_trials_sold,
                "sold_rate": metrics.sold_rate,
            },
        }
        default_name = f"weekly_snapshot_{period.start.isoformat()}.json"
        dest = filedialog.asksaveasfilename(
            title="Export weekly data",
            defaultextension=".json",
            initialfile=default_name,
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")],
        )
        if not dest:
            return
        Path(dest).write_text(json.dumps(payload, indent=2), encoding="utf-8")
        messagebox.showinfo("Export complete", f"Saved to:\n{dest}")

    def _on_settings(self) -> None:
        messagebox.showinfo(
            "Settings",
            "API credentials are configured in your .env file.\n"
            "Set APP_USER_NAME to change the displayed profile name.",
        )

    @staticmethod
    def _open_path(path: Path) -> None:
        try:
            if sys.platform == "win32":
                os.startfile(path)  # type: ignore[attr-defined]
            elif sys.platform == "darwin":
                subprocess.run(["open", str(path)], check=False)
            else:
                subprocess.run(["xdg-open", str(path)], check=False)
        except OSError as exc:
            messagebox.showerror("Open failed", str(exc))


def run_app() -> None:
    app = RedlineDashboardApp()
    app.mainloop()
