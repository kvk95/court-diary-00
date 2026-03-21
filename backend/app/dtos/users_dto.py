from datetime import datetime
from typing import Optional

from pydantic import EmailStr, field_validator

from app.dtos.base.base_data import BaseInData, BaseRecordData


# ─────────────────────────────────────────────────────────────────────────────
# USER DTOs
# ─────────────────────────────────────────────────────────────────────────────

class UserOut(BaseRecordData):
    user_id: int
    full_name: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    email: EmailStr
    phone: Optional[str] = None
    role_id: Optional[int] = None
    role_name: Optional[str] = None
    status_ind: bool = True
    image: Optional[str] = None
    created_date: Optional[datetime] = None


class UserCreate(BaseInData):
    email: str
    first_name: str
    last_name: Optional[str] = None
    phone: Optional[str] = None
    password: str
    status_ind: bool = True
    role_id: Optional[int] = None

    @field_validator("email")
    @classmethod
    def email_not_empty(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("Email is required")
        return v.strip().lower()

    @field_validator("first_name")
    @classmethod
    def first_name_not_empty(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("First name is required")
        return v.strip()


class UserEdit(BaseInData):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    phone: Optional[str] = None
    status_ind: Optional[bool] = None
    role_id: Optional[int] = None
    # Email and password are separate dedicated endpoints for security


class UserStatusToggle(BaseInData):
    """Toggle a user's active/inactive status."""
    user_id: int
    status_ind: bool


# ─────────────────────────────────────────────────────────────────────────────
# DELETION REQUEST DTOs
# ─────────────────────────────────────────────────────────────────────────────

class DeletionRequestOut(BaseRecordData):
    request_id: int
    request_no: str
    user_id: int
    user_email: Optional[str] = None
    user_name: Optional[str] = None
    request_date: Optional[datetime] = None
    status_code: Optional[str] = None
    notes: Optional[str] = None
    created_by: Optional[int] = None


class DeletionRejectPayload(BaseInData):
    notes: Optional[str] = None
