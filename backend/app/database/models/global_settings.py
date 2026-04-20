"""global_settings"""

from sqlalchemy import ForeignKey, Boolean, CHAR, DateTime, Integer, String, Text
from sqlalchemy.orm import relationship, backref
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql import func, text
from datetime import datetime
from typing import Any, Optional

from app.database.models.base.base_model import BaseModel
from app.database.models.base.timestampmixin import TimestampMixin

class GlobalSettings(BaseModel, TimestampMixin):
    __tablename__ = 'global_settings'

    # settings_id : TINYINT
    settings_id: Mapped[bool] = mapped_column(Boolean, primary_key=True, default=True, nullable=False)

    # platform_name : VARCHAR(150) COLLATE "utf8mb4_unicode_ci"
    platform_name: Mapped[str] = mapped_column(String(150), nullable=False)

    # company_name : VARCHAR(150) COLLATE "utf8mb4_unicode_ci"
    company_name: Mapped[str] = mapped_column(String(150), nullable=False)

    # support_email : VARCHAR(150) COLLATE "utf8mb4_unicode_ci"
    support_email: Mapped[str] = mapped_column(String(150), nullable=False)

    # primary_color : VARCHAR(20) COLLATE "utf8mb4_unicode_ci"
    primary_color: Mapped[str] = mapped_column(String(20), nullable=False)

    # smtp_host : VARCHAR(255) COLLATE "utf8mb4_unicode_ci"
    smtp_host: Mapped[Optional[str]] = mapped_column(String(255))

    # smtp_user_name : VARCHAR(255) COLLATE "utf8mb4_unicode_ci"
    smtp_user_name: Mapped[Optional[str]] = mapped_column(String(255))

    # smtp_password : VARCHAR(255) COLLATE "utf8mb4_unicode_ci"
    smtp_password: Mapped[Optional[str]] = mapped_column(String(255))

    # smtp_use_tls : TINYINT
    smtp_use_tls: Mapped[Optional[bool]] = mapped_column(Boolean, default=True)

    # smtp_port : INTEGER
    smtp_port: Mapped[Optional[int]] = mapped_column(Integer)

    # sms_provider : VARCHAR(100) COLLATE "utf8mb4_unicode_ci"
    sms_provider: Mapped[Optional[str]] = mapped_column(String(100))

    # sms_api_key : TEXT COLLATE "utf8mb4_unicode_ci"
    sms_api_key: Mapped[Optional[str]] = mapped_column(Text)

    # maintenance_enabled : TINYINT
    maintenance_enabled: Mapped[Optional[bool]] = mapped_column(Boolean, default=False)

    # maintenance_start : TIMESTAMP
    maintenance_start: Mapped[Optional[datetime]] = mapped_column(DateTime)

    # maintenance_end : TIMESTAMP
    maintenance_end: Mapped[Optional[datetime]] = mapped_column(DateTime)

    # allow_user_registration : TINYINT
    allow_user_registration: Mapped[Optional[bool]] = mapped_column(Boolean, default=True)

    # enable_case_collaboration : TINYINT
    enable_case_collaboration: Mapped[Optional[bool]] = mapped_column(Boolean, default=True)

    # enable_reports_module : TINYINT
    enable_reports_module: Mapped[Optional[bool]] = mapped_column(Boolean, default=True)

    # enable_api_rate_limit : TINYINT
    enable_api_rate_limit: Mapped[Optional[bool]] = mapped_column(Boolean, default=True)

    # created_by : CHAR(36) COLLATE "utf8mb4_unicode_ci"
    created_by: Mapped[Optional[str]] = mapped_column(CHAR(36), ForeignKey("users.user_id", ondelete="SET NULL"))

    # updated_by : CHAR(36) COLLATE "utf8mb4_unicode_ci"
    updated_by: Mapped[Optional[str]] = mapped_column(CHAR(36), ForeignKey("users.user_id", ondelete="SET NULL"))

    # FORWARD RELATIONSHIPS ------------------------------------------------------------
    # A forward relationship is defined in the table that contains the foreign key.

    # global_settings.created_by -> users.user_id
    global_settings_created_by_users = relationship(
        "Users",
        foreign_keys=[created_by], 
        backref=backref("global_settings_created_by_userss", cascade="all, delete-orphan")
    )

    # global_settings.updated_by -> users.user_id
    global_settings_updated_by_users = relationship(
        "Users",
        foreign_keys=[updated_by], 
        backref=backref("global_settings_updated_by_userss", cascade="all, delete-orphan")
    )

    # FORWARD RELATIONSHIPS ------------------------------------------------------------

