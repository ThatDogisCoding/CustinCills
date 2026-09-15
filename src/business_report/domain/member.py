from datetime import date
from enum import Enum
from typing import Optional

from pydantic import BaseModel, EmailStr, Field


class NaoStatus(str, Enum):
    YES = "Yes"
    NO = "No"
    UNKNOWN = "Unknown"


class Member(BaseModel):
    """Normalized member record (PDF §7)."""

    member_id: Optional[str] = None
    first_name: str = ""
    last_name: str = ""
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    membership_type: Optional[str] = None
    membership_status: Optional[str] = None
    join_date: Optional[date] = None
    termination_date: Optional[date] = None
    termination_reason: Optional[str] = None
    nao_status: NaoStatus = NaoStatus.UNKNOWN
    demotu_completed: Optional[bool] = None
    source_system: str = Field(description="mindbody, gohighlevel, or axle")

    @property
    def full_name(self) -> str:
        return f"{self.first_name} {self.last_name}".strip()
