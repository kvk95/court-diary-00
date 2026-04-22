# app\dtos\superadmin_dto.py


from datetime import datetime
from typing import Optional


from app.dtos.base.base_data import BaseInData, BaseRecordData


class TopChamberItem(BaseRecordData):
    rank: int
    chamber_id: str
    chamber_name: str
    users_count: int
    cases_count: int
    plan: str

class SuperAdminDashboardStats(BaseRecordData):
    total_chambers: int
    total_users: int
    active_cases: int
    active_subscriptions: int
    monthly_revenue: float
    system_health: float

class ChamberStatsOut(BaseRecordData):
    total: int
    active: int
    trial: int
    suspended: int

class ChamberItem(BaseRecordData):
    chamber_id: str
    chamber_name: str
    owner_name: str

    users_count: int
    cases_count: int
    clients_count: int

    plan: str
    status: str
    joined_date: datetime

class UserStatsOut(BaseRecordData):
    total: int
    active: int
    new_this_month: int

class UserItem(BaseRecordData):
    user_id: str
    full_name: str
    email: str

    chamber_name: Optional[str]
    role_name: Optional[str]

    status: str
    last_login: Optional[datetime]
    image_id: Optional[str]
    image_data: Optional[str]

class GlobalSettingsBasic(BaseRecordData):
    # branding
    platform_name: str
    company_name: str
    support_email: str
    primary_color: str

class GlobalSettingsOut(GlobalSettingsBasic):
    # smtp
    smtp_host: Optional[str]
    smtp_user_name: Optional[str]
    smtp_password: Optional[str]
    smtp_use_tls: Optional[bool]
    smtp_port: Optional[int]

    # sms
    sms_provider: Optional[str]
    sms_api_key: Optional[str]

    # maintenance
    maintenance_enabled: bool
    maintenance_start: Optional[datetime]
    maintenance_end: Optional[datetime]

    # feature flags
    allow_user_registration: bool
    enable_case_collaboration: bool
    enable_reports_module: bool
    enable_api_rate_limit: bool

class GlobalSettingsEdit(BaseInData):
    platform_name: Optional[str] = None
    company_name: Optional[str] = None
    support_email: Optional[str] = None
    primary_color: Optional[str] = None

    smtp_host: Optional[str] = None
    smtp_user_name: Optional[str] = None
    smtp_password: Optional[str] = None
    smtp_use_tls: Optional[bool] = None
    smtp_port: Optional[int] = None

    sms_provider: Optional[str] = None
    sms_api_key: Optional[str] = None

    maintenance_enabled: Optional[bool] = None
    maintenance_start: Optional[datetime] = None
    maintenance_end: Optional[datetime] = None

    allow_user_registration: Optional[bool] = None
    enable_case_collaboration: Optional[bool] = None
    enable_reports_module: Optional[bool] = None
    enable_api_rate_limit: Optional[bool] = None

class AnnouncementOut(BaseRecordData):
    announcement_id: str

    title: str
    content: str

    type_code: str
    audience_code: str
    status_code: str

    scheduled_at: Optional[datetime]
    expires_at: Optional[datetime]

    created_date: datetime

class AnnouncementCreate(BaseInData):
    title: str
    content: str

    type_code: str
    audience_code: str

    scheduled_at: Optional[datetime] = None
    expires_at: Optional[datetime] = None

    publish_now: Optional[bool] = False

class AnnouncementBaseIn(BaseRecordData):
    announcement_id: str

class AnnouncementUpdate(AnnouncementBaseIn):
    title: Optional[str] = None
    content: Optional[str] = None

    type_code: Optional[str] = None
    audience_code: Optional[str] = None

    scheduled_at: Optional[datetime] = None
    expires_at: Optional[datetime] = None

    publish_now: Optional[bool] = None

class SecurityRoleItem(BaseRecordData):
    role_id: int
    role_code: str
    role_name: str
    description: Optional[str]
    system_ind: bool
    admin_ind: bool
    status_ind: bool
    chambers_count: int

class SecurityRoleStats(BaseRecordData):
    total_roles: int
    default_roles: int
    protected_roles: int

class SecurityRoleCreate(BaseInData):
    role_code: str
    role_name: str
    description: Optional[str]
    admin_ind: Optional[bool] = False
    system_ind: Optional[bool] = False

class SecurityRoleBaseIn(BaseRecordData):
    role_id: int

class SecurityRoleUpdate(SecurityRoleBaseIn):
    role_name: Optional[str]
    description: Optional[str]
    status_ind: Optional[bool]