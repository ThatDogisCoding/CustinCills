from datetime import date
from typing import Optional

from pydantic import BaseModel

from business_report.domain.member import Member


class AtRiskMember(BaseModel):
    """At-risk member from Axle (PDF §7)."""

    member: Member
    risk_reason: Optional[str] = None
    follow_up_date: Optional[date] = None
    follow_up_status: Optional[str] = None
    business_comment: Optional[str] = None
    member_experience: Optional[str] = None
