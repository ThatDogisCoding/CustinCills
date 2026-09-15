from datetime import date, datetime, timedelta
from typing import Optional
from zoneinfo import ZoneInfo

from business_report.config import ReportingPeriod, Settings, WeekStartDay, get_settings


def _weekday_index(day: WeekStartDay) -> int:
    return 0 if day == WeekStartDay.MONDAY else 6


def reporting_period_for_date(
    reference: date,
    week_start_day: WeekStartDay = WeekStartDay.MONDAY,
) -> ReportingPeriod:
    """Return the reporting week containing reference (inclusive start/end)."""
    target_weekday = _weekday_index(week_start_day)
    days_since_start = (reference.weekday() - target_weekday) % 7
    start = reference - timedelta(days=days_since_start)
    end = start + timedelta(days=6)
    return ReportingPeriod(start=start, end=end)


def current_reporting_period(settings: Optional[Settings] = None) -> ReportingPeriod:
    settings = settings or get_settings()
    tz = ZoneInfo(settings.business_timezone)
    today = datetime.now(tz).date()
    return reporting_period_for_date(today, settings.report_week_start_day)


def reporting_period_for_week_offset(
    offset: int,
    settings: Optional[Settings] = None,
) -> ReportingPeriod:
    """Return reporting period offset from current week (0=current, -1=previous)."""
    current = current_reporting_period(settings)
    start = current.start + timedelta(weeks=offset)
    end = current.end + timedelta(weeks=offset)
    return ReportingPeriod(start=start, end=end)


def parse_reporting_period(
    week: str,
    settings: Optional[Settings] = None,
) -> ReportingPeriod:
    """
    Parse a week selector:
      - current
      - previous / prev / last
      - YYYY-MM-DD (any date within the desired week)
    """
    normalized = week.strip().lower()
    if normalized in {"current", "this"}:
        return current_reporting_period(settings)
    if normalized in {"previous", "prev", "last"}:
        return reporting_period_for_week_offset(-1, settings)

    try:
        reference = date.fromisoformat(normalized)
    except ValueError as exc:
        raise ValueError(
            f"Invalid week value {week!r}. Use current, previous, or YYYY-MM-DD."
        ) from exc

    settings = settings or get_settings()
    return reporting_period_for_date(reference, settings.report_week_start_day)
