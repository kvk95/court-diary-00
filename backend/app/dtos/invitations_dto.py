"""invitations_dto.py — DTOs for User Invitations"""

from datetime import date, datetime
from typing import Optional

from pydantic import field_validator

from app.dtos.base.base_data import BaseInData, BaseRecordData


class InvitationOut(BaseRecordData):
    invitation_id: str
    email: str
    role_id: Optional[int] = None
    role_name: Optional[str] = None
    status_code: Optional[str] = None
    invited_date: Optional[datetime] = None
    expires_date: Optional[date] = None
    message: Optional[str] = None
    invited_by_name: Optional[str] = None


class InvitationCreate(BaseInData):
    email: str
    role_id: Optional[int] = None
    expires_days: int = 30
    message: Optional[str] = None

    @field_validator("email")
    @classmethod
    def email_not_empty(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("Email is required")
        return v.strip().lower()


class InvitationResend(BaseInData):
    invitation_id: str

class InvitationRevoke(BaseInData):
    invitation_id: str
