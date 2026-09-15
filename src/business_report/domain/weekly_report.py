from datetime import date
from typing import Optional

from pydantic import BaseModel, Field

from business_report.domain.at_risk import AtRiskMember
from business_report.domain.follow_up import FollowUp
from business_report.domain.free_trial import FreeTrial
from business_report.domain.member import Member


class WeeklyReportMetrics(BaseModel):
    """Executive summary metrics for one reporting period."""

    period_start: date
    period_end: date

    free_trials_scheduled: int = 0
    free_trials_showed: int = 0
    free_trials_sold: int = 0
    active_members: int = 0
    terminations: int = 0
    new_members: int = 0

    @property
    def show_percentage(self) -> Optional[float]:
        if self.free_trials_scheduled == 0:
            return None
        return round(self.free_trials_showed / self.free_trials_scheduled * 100, 1)

    @property
    def sold_percentage(self) -> Optional[float]:
        if self.free_trials_scheduled == 0:
            return None
        return round(self.free_trials_sold / self.free_trials_scheduled * 100, 1)


class WeeklyReport(BaseModel):
    """Full weekly report payload before Excel export."""

    metrics: WeeklyReportMetrics
    free_trials: list[FreeTrial] = Field(default_factory=list)
    terminations: list[Member] = Field(default_factory=list)
    new_members: list[Member] = Field(default_factory=list)
    at_risk_members: list[AtRiskMember] = Field(default_factory=list)
    four_week_follow_up: list[Member] = Field(default_factory=list)
    follow_ups_needed: list[FollowUp] = Field(default_factory=list)
    validation_warnings: list[str] = Field(default_factory=list)
    validation_errors: list[str] = Field(default_factory=list)
