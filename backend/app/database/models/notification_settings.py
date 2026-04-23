"""notification_settings"""

from sqlalchemy import ForeignKey, Boolean, CHAR, Integer
from sqlalchemy.orm import relationship, backref
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql import func, text
from typing import Any, Optional

from app.database.models.base.base_model import BaseModel
from app.database.models.base.timestampmixin import TimestampMixin

class NotificationSettings(BaseModel, TimestampMixin):
    __tablename__ = 'notification_settings'

    # notification_id : INTEGER
    notification_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True, nullable=False)

    # user_id : CHAR(36) COLLATE "utf8mb4_unicode_ci"
    user_id: Mapped[str] = mapped_column(CHAR(36), ForeignKey("users.user_id", ondelete="CASCADE"), nullable=False)

    # email_enabled_ind : TINYINT
    email_enabled_ind: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    # sms_enabled_ind : TINYINT
    sms_enabled_ind: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    # whatsapp_enabled_ind : TINYINT
    whatsapp_enabled_ind: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    # email_summary_frequency_code : CHAR(4) COLLATE "utf8mb4_unicode_ci"
    email_summary_frequency_code: Mapped[str] = mapped_column(CHAR(4), ForeignKey("refm_email_summary_frequency.code", ondelete="RESTRICT"), default='SFDL', nullable=False)

    # sms_summary_frequency_code : CHAR(4) COLLATE "utf8mb4_unicode_ci"
    sms_summary_frequency_code: Mapped[str] = mapped_column(CHAR(4), ForeignKey("refm_email_summary_frequency.code", ondelete="RESTRICT"), default='SFDL', nullable=False)

    # whatsapp_summary_frequency_code : CHAR(4) COLLATE "utf8mb4_unicode_ci"
    whatsapp_summary_frequency_code: Mapped[str] = mapped_column(CHAR(4), ForeignKey("refm_email_summary_frequency.code", ondelete="RESTRICT"), default='SFDL', nullable=False)

    # email_remind_before : INTEGER
    email_remind_before: Mapped[Optional[int]] = mapped_column(Integer, default=30)

    # sms_remind_before : INTEGER
    sms_remind_before: Mapped[Optional[int]] = mapped_column(Integer, default=30)

    # whatsapp_remind_before : INTEGER
    whatsapp_remind_before: Mapped[Optional[int]] = mapped_column(Integer, default=30)

    # status_ind : TINYINT
    status_ind: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    # created_by : CHAR(36) COLLATE "utf8mb4_unicode_ci"
    created_by: Mapped[Optional[str]] = mapped_column(CHAR(36), ForeignKey("users.user_id", ondelete="SET NULL"))

    # updated_by : CHAR(36) COLLATE "utf8mb4_unicode_ci"
    updated_by: Mapped[Optional[str]] = mapped_column(CHAR(36), ForeignKey("users.user_id", ondelete="SET NULL"))

    # FORWARD RELATIONSHIPS ------------------------------------------------------------
    # A forward relationship is defined in the table that contains the foreign key.

    # notification_settings.user_id -> users.user_id
    notification_settings_user_id_users = relationship(
        "Users",
        foreign_keys=[user_id], 
        backref=backref("notification_settings_user_id_userss", cascade="all, delete-orphan")
    )

    # notification_settings.email_summary_frequency_code -> refm_email_summary_frequency.code
    notification_settings_email_summary_frequency_code_refm_email_summary_frequency = relationship(
        "RefmEmailSummaryFrequency",
        foreign_keys=[email_summary_frequency_code], 
        backref=backref("notification_settings_email_summary_frequency_code_refm_email_summary_frequencys", cascade="all, delete-orphan")
    )

    # notification_settings.sms_summary_frequency_code -> refm_email_summary_frequency.code
    notification_settings_sms_summary_frequency_code_refm_email_summary_frequency = relationship(
        "RefmEmailSummaryFrequency",
        foreign_keys=[sms_summary_frequency_code], 
        backref=backref("notification_settings_sms_summary_frequency_code_refm_email_summary_frequencys", cascade="all, delete-orphan")
    )

    # notification_settings.whatsapp_summary_frequency_code -> refm_email_summary_frequency.code
    notification_settings_whatsapp_summary_frequency_code_refm_email_summary_frequency = relationship(
        "RefmEmailSummaryFrequency",
        foreign_keys=[whatsapp_summary_frequency_code], 
        backref=backref("notification_settings_whatsapp_summary_frequency_code_refm_email_summary_frequencys", cascade="all, delete-orphan")
    )

    # notification_settings.created_by -> users.user_id
    notification_settings_created_by_users = relationship(
        "Users",
        foreign_keys=[created_by], 
        backref=backref("notification_settings_created_by_userss", cascade="all, delete-orphan")
    )

    # notification_settings.updated_by -> users.user_id
    notification_settings_updated_by_users = relationship(
        "Users",
        foreign_keys=[updated_by], 
        backref=backref("notification_settings_updated_by_userss", cascade="all, delete-orphan")
    )

    # FORWARD RELATIONSHIPS ------------------------------------------------------------

