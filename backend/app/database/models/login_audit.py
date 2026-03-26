"""login_audit"""

from sqlalchemy import ForeignKey, CHAR, DateTime, String, Text
from sqlalchemy.orm import relationship, backref
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql import func, text
from datetime import datetime
from typing import Any, Optional

from app.database.models.base.base_model import BaseModel

class LoginAudit(BaseModel):
    __tablename__ = 'login_audit'

    # login_id : CHAR(36) COLLATE "utf8mb4_unicode_ci"
    login_id: Mapped[str] = mapped_column(CHAR(36), primary_key=True, nullable=False)

    # user_id : CHAR(36) COLLATE "utf8mb4_unicode_ci"
    user_id: Mapped[Optional[str]] = mapped_column(CHAR(36), ForeignKey("users.user_id", ondelete="SET NULL"))

    # chamber_id : CHAR(36) COLLATE "utf8mb4_unicode_ci"
    chamber_id: Mapped[str] = mapped_column(CHAR(36), ForeignKey("chamber.chamber_id", ondelete="CASCADE"), nullable=False)

    # email : VARCHAR(120) COLLATE "utf8mb4_unicode_ci"
    email: Mapped[Optional[str]] = mapped_column(String(120))

    # status_code : CHAR(2) COLLATE "utf8mb4_unicode_ci"
    status_code: Mapped[Optional[str]] = mapped_column(CHAR(2), ForeignKey("refm_login_status.code", ondelete="SET NULL"))

    # failure_reason : VARCHAR(255) COLLATE "utf8mb4_unicode_ci"
    failure_reason: Mapped[Optional[str]] = mapped_column(String(255))

    # login_time : TIMESTAMP
    login_time: Mapped[Optional[datetime]] = mapped_column(DateTime, server_default=func.current_timestamp())

    # ip_address : VARCHAR(45) COLLATE "utf8mb4_unicode_ci"
    ip_address: Mapped[Optional[str]] = mapped_column(String(45))

    # user_agent : TEXT COLLATE "utf8mb4_unicode_ci"
    user_agent: Mapped[Optional[str]] = mapped_column(Text)

    # FORWARD RELATIONSHIPS ------------------------------------------------------------
    # A forward relationship is defined in the table that contains the foreign key.

    # login_audit.user_id -> users.user_id
    login_audit_user_id_users = relationship(
        "Users",
        foreign_keys=[user_id], 
        backref=backref("login_audit_user_id_userss", cascade="all, delete-orphan")
    )

    # login_audit.chamber_id -> chamber.chamber_id
    login_audit_chamber_id_chamber = relationship(
        "Chamber",
        foreign_keys=[chamber_id], 
        backref=backref("login_audit_chamber_id_chambers", cascade="all, delete-orphan")
    )

    # login_audit.status_code -> refm_login_status.code
    login_audit_status_code_refm_login_status = relationship(
        "RefmLoginStatus",
        foreign_keys=[status_code], 
        backref=backref("login_audit_status_code_refm_login_statuss", cascade="all, delete-orphan")
    )

    # FORWARD RELATIONSHIPS ------------------------------------------------------------

