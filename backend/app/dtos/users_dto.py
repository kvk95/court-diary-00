# app/dtos/users_dto.py

from datetime import datetime
from typing import Optional, List
from pydantic import EmailStr
from app.dtos.base.base_data import BaseInData, BaseRecordData
from app.dtos.roles_dto import RoleOut
from app.dtos.role_permissions_dto import RolePermissionModuleOut


# =============================================================================
# USER PROFILE & THEME DTOs
# =============================================================================

class ImageInfoOut(BaseRecordData):    
    image_id: Optional[str]
    image_data: Optional[str]

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

class UserBasicInfoOut(ImageInfoOut):
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
    advocate_ind: bool
    active_ind: bool = True

class UserOut(UserBasicInfoOut):
    """
    Full user output with profile, permissions, and chamber info.
    Used for login, /me, /{user_id}, and /paged endpoints.
    """
    super_admin_ind: bool
    role: Optional[RoleOut] = None
    created_date: Optional[datetime] = None
    chamber_name: Optional[str] = None
    profile: Optional[UserProfileOut] = None
    permissions: List[RolePermissionModuleOut] = []
    chamber_id: Optional[str] = None
    last_login_time: Optional[datetime] = None


# =============================================================================
# USER INPUT DTOs
# =============================================================================

class UserPasswordIn(BaseInData):
    password: Optional[str] = None

class UserEmailIn(BaseInData):    
    email: Optional[str] = None

class UserCreateBasic(UserEmailIn,UserPasswordIn):
    first_name: Optional[str] = None
    last_name: Optional[str] = None

class UserCreateoAuth(UserCreateBasic):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    image_data: Optional[str]

class UserCreate(UserCreateBasic):
    phone: Optional[str] = None
    status_ind: bool = True
    advocate_ind: bool
    role_id: Optional[int] = None
    image_data: Optional[str]


class UserEdit(UserCreate):
    pass


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