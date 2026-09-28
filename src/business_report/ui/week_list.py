from dataclasses import dataclass
from datetime import date

from business_report.config import ReportingPeriod
from business_report.util.dates import reporting_period_for_week_offset


@dataclass(frozen=True)
class WeekListEntry:
    period: ReportingPeriod
    title: str
    subtitle: str


def _format_day(d: date) -> str:
    return f"{d.strftime('%b')} {d.day}"


def format_week_entry(period: ReportingPeriod) -> WeekListEntry:
    start, end = period.start, period.end
    title = f"Week of {_format_day(start)}"
    subtitle = f"({_format_day(start)} - {_format_day(end)})"
    return WeekListEntry(period=period, title=title, subtitle=subtitle)


def recent_weeks(count: int = 12) -> list[WeekListEntry]:
    """Most recent week first (offset 0, -1, -2, ...)."""
    entries: list[WeekListEntry] = []
    for offset in range(count):
        period = reporting_period_for_week_offset(-offset)
        entries.append(format_week_entry(period))
    return entries
