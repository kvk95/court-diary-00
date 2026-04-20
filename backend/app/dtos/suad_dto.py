# app\dtos\superadmin_dto.py


from datetime import datetime
from typing import List, Optional

from app.dtos.base.base_data import BaseRecordData


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


class SuperAdminDashboardOut(BaseRecordData):

    top_chambers: List[TopChamberItem]


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