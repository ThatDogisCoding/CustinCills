from datetime import date
from enum import Enum
from typing import Optional

from pydantic import BaseModel

from business_report.domain.member import Member


class FollowUpStatus(str, Enum):
    NOT_STARTED = "NOT_STARTED"
    IN_PROGRESS = "IN_PROGRESS"
    COMPLETED = "COMPLETED"
    LEFT_VM = "LEFT_VM"
    NO_RESPONSE = "NO_RESPONSE"
    SCHEDULED = "SCHEDULED"
    RESOLVED = "RESOLVED"


class FollowUp(BaseModel):
    """Follow-up task (PDF §7)."""

    member: Member
    reason: str
    assigned_to: Optional[str] = None
    due_date: Optional[date] = None
    status: FollowUpStatus = FollowUpStatus.NOT_STARTED
    last_contact_date: Optional[date] = None
    contact_method: Optional[str] = None
    notes: Optional[str] = None
