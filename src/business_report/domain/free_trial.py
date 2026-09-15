from datetime import date
from typing import Optional

from pydantic import BaseModel, EmailStr


class FreeTrial(BaseModel):
    """Free trial record from GoHighLevel (PDF §7)."""

    contact_id: str
    name: str = ""
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    trial_date: Optional[date] = None
    scheduled_date: Optional[date] = None
    scheduled: bool = False
    showed: bool = False
    sold: bool = False
    assigned_staff: Optional[str] = None
    status: Optional[str] = None
    pipeline_stage: Optional[str] = None
    tags: list[str] = []
