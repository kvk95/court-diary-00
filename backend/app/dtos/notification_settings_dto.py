# app/dtos/notification_settings_dto.py

from typing import Optional
from app.dtos.base.base_data import BaseRecordData, BaseInData


class NotificationSettingsOut(BaseRecordData):
    email_enabled_ind: bool
    sms_enabled_ind: bool
    whatsapp_enabled_ind: bool

    email_summary_frequency_code: str
    sms_summary_frequency_code: str
    whatsapp_summary_frequency_code: str

    email_remind_before: int
    sms_remind_before: int
    whatsapp_remind_before: int


class NotificationSettingsEdit(BaseInData):
    email_enabled_ind: Optional[bool] = None
    sms_enabled_ind: Optional[bool] = None
    whatsapp_enabled_ind: Optional[bool] = None

    email_summary_frequency_code: Optional[str] = None
    sms_summary_frequency_code: Optional[str] = None
    whatsapp_summary_frequency_code: Optional[str] = None

    email_remind_before: Optional[int] = None
    sms_remind_before: Optional[int] = None
    whatsapp_remind_before: Optional[int] = None