"""email_link"""

from sqlalchemy import ForeignKey, Boolean, CHAR, DateTime, String
from sqlalchemy.orm import relationship, backref
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql import func, text
from datetime import datetime
from typing import Any, Optional

from app.database.models.base.base_model import BaseModel

class EmailLink(BaseModel):
    __tablename__ = 'email_link'

    # link_id : CHAR(36) COLLATE "utf8mb4_unicode_ci"
    link_id: Mapped[str] = mapped_column(CHAR(36), primary_key=True, nullable=False)

    # user_id : CHAR(36) COLLATE "utf8mb4_unicode_ci"
    user_id: Mapped[str] = mapped_column(CHAR(36), ForeignKey("users.user_id", ondelete="CASCADE"), nullable=False)

    # recipient_email : VARCHAR(120) COLLATE "utf8mb4_unicode_ci"
    recipient_email: Mapped[str] = mapped_column(String(120), nullable=False)

    # template_code : CHAR(4) COLLATE "utf8mb4_unicode_ci"
    template_code: Mapped[str] = mapped_column(CHAR(4), ForeignKey("refm_email_templates.code", ondelete="RESTRICT"), nullable=False)

    # link_url : VARCHAR(1000) COLLATE "utf8mb4_unicode_ci"
    link_url: Mapped[Optional[str]] = mapped_column(String(1000))

    # is_used : TINYINT
    is_used: Mapped[Optional[bool]] = mapped_column(Boolean, default=False)

    # expiry_date : TIMESTAMP
    expiry_date: Mapped[Optional[datetime]] = mapped_column(DateTime)

    # created_date : TIMESTAMP
    created_date: Mapped[Optional[datetime]] = mapped_column(DateTime, server_default=func.current_timestamp())

    # FORWARD RELATIONSHIPS ------------------------------------------------------------
    # A forward relationship is defined in the table that contains the foreign key.

    # email_link.user_id -> users.user_id
    email_link_user_id_users = relationship(
        "Users",
        foreign_keys=[user_id], 
        backref=backref("email_link_user_id_userss", cascade="all, delete-orphan")
    )

    # email_link.template_code -> refm_email_templates.code
    email_link_template_code_refm_email_templates = relationship(
        "RefmEmailTemplates",
        foreign_keys=[template_code], 
        backref=backref("email_link_template_code_refm_email_templatess", cascade="all, delete-orphan")
    )

    # FORWARD RELATIONSHIPS ------------------------------------------------------------

