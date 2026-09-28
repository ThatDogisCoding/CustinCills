"""Sample weekly metrics until API sync is implemented (baseline snapshot data)."""

from dataclasses import dataclass
from datetime import date
from typing import Optional

from business_report.config import ReportingPeriod


@dataclass(frozen=True)
class WeekDashboardMetrics:
    free_trials_scheduled: Optional[int]
    show_rate: Optional[str]
    active_members: Optional[int]
    terminations: Optional[int]
    free_trials_showed: Optional[int] = None
    free_trials_sold: Optional[int] = None
    sold_rate: Optional[str] = None
    has_live_data: bool = False


# From Weekly Business Snapshot — Week of 7/27/2026 (and prior weeks in layout doc)
_SNAPSHOT: dict[date, WeekDashboardMetrics] = {
    date(2026, 7, 27): WeekDashboardMetrics(
        free_trials_scheduled=13,
        free_trials_showed=8,
        show_rate="62%",
        free_trials_sold=3,
        sold_rate="23%",
        active_members=148,
        terminations=4,
        has_live_data=True,
    ),
    date(2026, 7, 20): WeekDashboardMetrics(
        free_trials_scheduled=14,
        free_trials_showed=10,
        show_rate="71%",
        free_trials_sold=7,
        sold_rate="50%",
        active_members=149,
        terminations=2,
        has_live_data=True,
    ),
    date(2026, 7, 13): WeekDashboardMetrics(
        free_trials_scheduled=16,
        free_trials_showed=11,
        show_rate="69%",
        free_trials_sold=4,
        sold_rate="25%",
        active_members=148,
        terminations=3,
        has_live_data=True,
    ),
    date(2026, 7, 6): WeekDashboardMetrics(
        free_trials_scheduled=16,
        free_trials_showed=7,
        show_rate="44%",
        free_trials_sold=2,
        sold_rate="13%",
        active_members=148,
        terminations=2,
        has_live_data=True,
    ),
}


def metrics_for_period(period: ReportingPeriod) -> WeekDashboardMetrics:
    key = period.start
    if key in _SNAPSHOT:
        return _SNAPSHOT[key]
    return WeekDashboardMetrics(
        free_trials_scheduled=None,
        show_rate=None,
        active_members=None,
        terminations=None,
        has_live_data=False,
    )


def display_value(value: Optional[int], placeholder: str = "—") -> str:
    if value is None:
        return placeholder
    return str(value)
