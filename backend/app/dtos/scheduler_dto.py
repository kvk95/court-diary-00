from datetime import date, datetime
from typing import Optional

from app.dtos.base.base_data import BaseInData


class NotificationLogCreate(BaseInData):
    user_id: str
    hearing_id: Optional[str]
    channel_code: str
    type_code: str
    ref_date: Optional[date] = None
    scheduled_at: datetime
    status_code: str = "SENT"