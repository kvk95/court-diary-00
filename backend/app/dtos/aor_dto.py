"""aor_dto.py — DTOs for Case AOR (Advocate on Record) module"""

from datetime import date, datetime
from typing import Optional

from pydantic import field_validator

from app.dtos.base.base_data import BaseInData
from app.dtos.users_dto import ImageInfoOut


# ─────────────────────────────────────────────────────────────────────────────
# AOR status codes:  AC=Active  WD=Withdrawn  SU=Substituted
# ─────────────────────────────────────────────────────────────────────────────

class AorOut(ImageInfoOut):
    case_aor_id: str
    case_id: str
    user_id: str
    chamber_id: str
    advocate_name: str    
    primary_ind: bool = False
    appointment_date: Optional[date] = None
    withdrawal_date: Optional[date] = None
    status_code: str 
    status_description: Optional[str] = None
    notes: Optional[str] = None    
    created_date: Optional[datetime] = None


class AorCreate(BaseInData):
    case_id: str
    user_id: str                 # must be a chamber member
    primary_ind: bool = False
    appointment_date: Optional[date] = None
    notes: Optional[str] = None


class AorEdit(BaseInData):
    case_aor_id: str
    primary_ind: Optional[bool] = None
    status_code: Optional[str] = None      # AC | WD | SU
    appointment_date: Optional[date] = None
    withdrawal_date: Optional[date] = None
    notes: Optional[str] = None

    @field_validator("status_code")
    @classmethod
    def valid_status(cls, v: Optional[str]) -> Optional[str]:
        if v is not None and v not in ("AC", "WD", "SU"):
            raise ValueError("status_code must be AC, WD, or SU")
        return v


class AorWithdraw(BaseInData):
    case_aor_id: str
    withdrawal_date: Optional[date] = None
    notes: Optional[str] = None
