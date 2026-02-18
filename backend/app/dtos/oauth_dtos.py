from typing import Optional, Dict, Any
from dataclasses import dataclass
from .base.base_data import BaseInData, BaseRecordData


@dataclass(frozen=True)
class CurrentUserContext:
    user_id: int
    company_id: int
    store_id: int
    email: str
    first_name: Optional[str]
    last_name: Optional[str]
    status_ind: bool | None
    is_email_verified: bool


class LoginRequest(BaseInData):
    email: str
    password: str
    company_id: Optional[int] = None
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None


class RefreshRequest(BaseInData):
    refresh_token: str


class UserDetails(BaseRecordData):
    user_id: int
    company_id: Optional[int] = None
    email: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None

    model_config = {"from_attributes": True}


class TokenOut(BaseRecordData):
    access_token: str
    refresh_token: Optional[str] = None
    token_type: str = "bearer"
    user_details: Dict[str, Any] | None = None
