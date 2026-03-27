# app/dtos/users_dto.py

from datetime import datetime
from typing import Optional, List
from pydantic import EmailStr, field_validator
from app.dtos.base.base_data import BaseInData, BaseRecordData
from app.dtos.roles_dto import RoleOut
from app.dtos.role_permissions_dto import RolePermissionModuleOut


# =============================================================================
# USER PROFILE & THEME DTOs
# =============================================================================

class UserFullThemeOut(BaseRecordData):
    """User profile theme settings"""
    header_color: str = "0 0% 100%"
    sidebar_color: str = "0 0% 100%"
    primary_color: str = "32.4 99% 63%"
    font_family: str = "Nunito, sans-serif"


class UserProfileOut(BaseRecordData):
    """Profile section in user output"""
    theme: UserFullThemeOut


# =============================================================================
# USER OUTPUT DTO (Unified for ALL endpoints)
# =============================================================================

class UserOut(BaseRecordData):
    """
    Full user output with profile, permissions, and chamber info.
    Used for login, /me, /{user_id}, and /paged endpoints.
    """
    user_id: str
    full_name: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    email: EmailStr
    phone: Optional[str] = None
    role: Optional[RoleOut] = None
    active_ind: bool = True
    image: Optional[str] = None
    created_date: Optional[datetime] = None
    chamber_name: Optional[str] = None
    profile: Optional[UserProfileOut] = None
    permissions: List[RolePermissionModuleOut] = []
    chamber_id: Optional[str] = None


# =============================================================================
# USER INPUT DTOs
# =============================================================================

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


class UserStatusToggle(BaseInData):
    """Toggle a user's active/inactive status."""
    user_id: str
    status_ind: bool


# =============================================================================
# DELETION REQUEST DTOs
# =============================================================================

class DeletionRequestOut(BaseRecordData):
    request_id: int
    request_no: str
    user_id: str
    user_email: Optional[str] = None
    user_name: Optional[str] = None
    request_date: Optional[datetime] = None
    status_code: Optional[str] = None
    notes: Optional[str] = None
    created_by: Optional[int] = None


class DeletionRejectPayload(BaseInData):
    notes: Optional[str] = None

class UserStatsOut(BaseInData):
    """User management statistics for dashboard."""
    total_users: int = 0
    active_users: int = 0
    total_roles: int = 0
    pending_invites: int = 0