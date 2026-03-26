"""email_log"""

from sqlalchemy import ForeignKey, Boolean, CHAR, Date, DateTime, JSON, String, Text
from sqlalchemy.orm import relationship, backref
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql import func, text
from datetime import date, datetime
from typing import Any, Optional

from app.database.models.base.base_model import BaseModel

class EmailLog(BaseModel):
    __tablename__ = 'email_log'

    # email_id : CHAR(36) COLLATE "utf8mb4_unicode_ci"
    email_id: Mapped[str] = mapped_column(CHAR(36), primary_key=True, nullable=False)

    # chamber_id : CHAR(36) COLLATE "utf8mb4_unicode_ci"
    chamber_id: Mapped[str] = mapped_column(CHAR(36), ForeignKey("chamber.chamber_id", ondelete="CASCADE"), nullable=False)

    # user_id : CHAR(36) COLLATE "utf8mb4_unicode_ci"
    user_id: Mapped[Optional[str]] = mapped_column(CHAR(36), ForeignKey("users.user_id", ondelete="SET NULL"))

    # template_code : CHAR(30) COLLATE "utf8mb4_unicode_ci"
    template_code: Mapped[Optional[str]] = mapped_column(CHAR(30), ForeignKey("refm_email_templates.code", ondelete="SET NULL"))

    # recipient_email : VARCHAR(255) COLLATE "utf8mb4_unicode_ci"
    recipient_email: Mapped[str] = mapped_column(String(255), nullable=False)

    # recipient_name : VARCHAR(120) COLLATE "utf8mb4_unicode_ci"
    recipient_name: Mapped[Optional[str]] = mapped_column(String(120))

    # subject : VARCHAR(500) COLLATE "utf8mb4_unicode_ci"
    subject: Mapped[Optional[str]] = mapped_column(String(500))

    # body_preview : TEXT COLLATE "utf8mb4_unicode_ci"
    body_preview: Mapped[Optional[str]] = mapped_column(Text)

    # status_code : CHAR(2) COLLATE "utf8mb4_unicode_ci"
    status_code: Mapped[Optional[str]] = mapped_column(CHAR(2), ForeignKey("refm_email_status.code", ondelete="SET NULL"), default='P')

    # sent_at : DATETIME
    sent_at: Mapped[Optional[date]] = mapped_column(Date)

    # delivered_at : DATETIME
    delivered_at: Mapped[Optional[date]] = mapped_column(Date)

    # opened_at : DATETIME
    opened_at: Mapped[Optional[date]] = mapped_column(Date)

    # error_message : TEXT COLLATE "utf8mb4_unicode_ci"
    error_message: Mapped[Optional[str]] = mapped_column(Text)

    # retry_count : TINYINT
    retry_count: Mapped[Optional[bool]] = mapped_column(Boolean, default=False)

    # next_retry_at : DATETIME
    next_retry_at: Mapped[Optional[date]] = mapped_column(Date)

    # metadata_json : JSON
    metadata_json: Mapped[Optional[Any]] = mapped_column(JSON, default=[])

    # created_date : TIMESTAMP
    created_date: Mapped[Optional[datetime]] = mapped_column(DateTime, server_default=func.current_timestamp())

    # created_by : CHAR(36) COLLATE "utf8mb4_unicode_ci"
    created_by: Mapped[Optional[str]] = mapped_column(CHAR(36))

    # FORWARD RELATIONSHIPS ------------------------------------------------------------
    # A forward relationship is defined in the table that contains the foreign key.

    # email_log.chamber_id -> chamber.chamber_id
    email_log_chamber_id_chamber = relationship(
        "Chamber",
        foreign_keys=[chamber_id], 
        backref=backref("email_log_chamber_id_chambers", cascade="all, delete-orphan")
    )

    # email_log.user_id -> users.user_id
    email_log_user_id_users = relationship(
        "Users",
        foreign_keys=[user_id], 
        backref=backref("email_log_user_id_userss", cascade="all, delete-orphan")
    )

    # email_log.template_code -> refm_email_templates.code
    email_log_template_code_refm_email_templates = relationship(
        "RefmEmailTemplates",
        foreign_keys=[template_code], 
        backref=backref("email_log_template_code_refm_email_templatess", cascade="all, delete-orphan")
    )

    # email_log.status_code -> refm_email_status.code
    email_log_status_code_refm_email_status = relationship(
        "RefmEmailStatus",
        foreign_keys=[status_code], 
        backref=backref("email_log_status_code_refm_email_statuss", cascade="all, delete-orphan")
    )

    # FORWARD RELATIONSHIPS ------------------------------------------------------------

