from typing import Optional, List, Dict, Any
from pydantic import BaseModel, EmailStr


# =============================================================================
# LOGIN / AUTH DTOs
# =============================================================================

class LoginRequest(BaseModel):
    """
    Login request payload.
    chamber_id is optional - if not provided, user's primary chamber is used.
    """
    email: EmailStr
    password: str
    chamber_id: Optional[int] = None  # ✅ NEW: Optional chamber selection
    remember_me: bool = False
    # Optional: MFA / 2FA fields for future
    mfa_code: Optional[str] = None
    device_id: Optional[str] = None
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None


class RefreshRequest(BaseModel):
    """Refresh token request."""
    refresh_token: str


class TokenOut(BaseModel):
    """Token response with user context."""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    user_details: Optional[Dict[str, Any]] = None
    expires_in: int = 3600  # seconds


# =============================================================================
# USER CONTEXT DTOs
# =============================================================================

class CurrentUserContext(BaseModel):
    """
    Current user context stored in request scope.
    Used for authorization checks and audit logging.
    """
    user_id: int
    chamber_id: int  
    email: str
    first_name: str
    last_name: Optional[str] = None
    status_ind: bool = True
    is_email_verified: bool = False
    # Optional: Add more fields as needed
    # role_id: Optional[int] = None
    # role_code: Optional[str] = None


class UserProfileOut(BaseModel):
    """User profile response (for UI)."""
    user_id: int
    first_name: str
    last_name: Optional[str]
    email: str
    phone: Optional[str]
    image: Optional[str] = "/assets/images/avatar/none.png"
    chamber_id: int  # ✅ Changed from company_id
    chamber_name: Optional[str] = None
    role: Optional[Dict[str, Any]] = None
    profile: Optional[Dict[str, Any]] = None
    permissions: List[Dict[str, Any]] = []


class UserChamberContext(BaseModel):
    """
    User's chamber membership context.
    For users who belong to multiple chambers.
    """
    link_id: int
    chamber_id: int
    chamber_name: str
    is_primary: bool
    role_override: Optional[str] = None
    joined_date: str
    can_switch: bool = True


class UserContextWithChambers(BaseModel):
    """
    Complete user context including all chamber memberships.
    Returned at login for multi-chamber users.
    """
    user: Dict[str, Any]
    profile: Dict[str, Any]
    permissions: List[Dict[str, Any]]
    current_chamber_id: int  # ✅ Changed from company_id
    chambers: List[UserChamberContext] = []  # All chambers user belongs to