"""aor_dto.py — DTOs for Case AOR (Advocate on Record) module"""

from datetime import date, datetime
from typing import Optional

from pydantic import field_validator

from app.dtos.base.base_data import BaseInData, BaseRecordData


# ─────────────────────────────────────────────────────────────────────────────
# AOR status codes:  AC=Active  WD=Withdrawn  SU=Substituted
# ─────────────────────────────────────────────────────────────────────────────

class AorOut(BaseRecordData):
    case_aor_id: int
    case_id: int
    user_id: int
    advocate_name: str           # first_name + last_name of the user
    is_primary: bool = False
    status_code: str = "AC"
    status_description: Optional[str] = None
    appointment_date: Optional[date] = None
    withdrawal_date: Optional[date] = None
    notes: Optional[str] = None
    created_date: Optional[datetime] = None


class AorCreate(BaseInData):
    case_id: int
    user_id: int                 # must be a chamber member
    is_primary: bool = False
    appointment_date: Optional[date] = None
    notes: Optional[str] = None


class AorEdit(BaseInData):
    case_aor_id: int
    is_primary: Optional[bool] = None
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
    case_aor_id: int
    withdrawal_date: Optional[date] = None
    notes: Optional[str] = None
