"""chamber_dto.py — DTOs for Chamber / Settings module"""

from datetime import date, datetime
from typing import Optional

from pydantic import EmailStr, field_validator

from app.dtos.base.base_data import BaseInData, BaseRecordData


# ---------------------------------------------------------------------------
# OUT
# ---------------------------------------------------------------------------

class ChamberOut(BaseRecordData):
    """Full chamber detail returned by GET and after edit."""

    chamber_id: str
    chamber_name: str
    email: Optional[str] = None
    phone: Optional[str] = None
    address_line1: Optional[str] = None
    address_line2: Optional[str] = None
    city: Optional[str] = None
    state_code: Optional[str] = None
    postal_code: Optional[str] = None
    country_code: Optional[str] = None
    plan_code: Optional[str] = None
    subscription_start: Optional[date] = None
    subscription_end: Optional[date] = None
    status_ind: bool = True
    created_date: Optional[datetime] = None
    updated_date: Optional[datetime] = None


# ---------------------------------------------------------------------------
# IN — Edit
# ---------------------------------------------------------------------------

class ChamberEdit(BaseInData):
    """
    Payload accepted by PUT /settings/chamber/{chamber_id}/edit.

    plan_code, subscription_start, subscription_end, status_ind are
    managed by the billing/subscription module and are intentionally
    excluded from this DTO.
    """

    chamber_name: Optional[str] = None
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    address_line1: Optional[str] = None
    address_line2: Optional[str] = None
    city: Optional[str] = None
    state_code: Optional[str] = None
    postal_code: Optional[str] = None
    country_code: Optional[str] = None

    @field_validator("chamber_name")
    @classmethod
    def name_not_blank(cls, v: Optional[str]) -> Optional[str]:
        if v is not None and not v.strip():
            raise ValueError("chamber_name must not be blank")
        return v.strip() if v else v

    @field_validator("phone")
    @classmethod
    def phone_stripped(cls, v: Optional[str]) -> Optional[str]:
        return v.strip() if v else v