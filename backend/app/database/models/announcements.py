"""announcements"""

from sqlalchemy import ForeignKey, Boolean, CHAR, DateTime, String, Text
from sqlalchemy.orm import relationship, backref
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql import func, text
from datetime import datetime
from typing import Any, Optional

from app.database.models.base.base_model import BaseModel
from app.database.models.base.timestampmixin import TimestampMixin

class Announcements(BaseModel, TimestampMixin):
    __tablename__ = 'announcements'

    # announcement_id : CHAR(36) COLLATE "utf8mb4_unicode_ci"
    announcement_id: Mapped[str] = mapped_column(CHAR(36), primary_key=True, nullable=False)

    # title : VARCHAR(255) COLLATE "utf8mb4_unicode_ci"
    title: Mapped[str] = mapped_column(String(255), nullable=False)

    # content : TEXT COLLATE "utf8mb4_unicode_ci"
    content: Mapped[str] = mapped_column(Text, nullable=False)

    # type_code : VARCHAR(20) COLLATE "utf8mb4_unicode_ci"
    type_code: Mapped[str] = mapped_column(String(20), ForeignKey("refm_announcement_type.code", ondelete="RESTRICT"), nullable=False)

    # audience_code : VARCHAR(20) COLLATE "utf8mb4_unicode_ci"
    audience_code: Mapped[str] = mapped_column(String(20), ForeignKey("refm_announcement_audience.code", ondelete="RESTRICT"), nullable=False)

    # status_code : VARCHAR(20) COLLATE "utf8mb4_unicode_ci"
    status_code: Mapped[str] = mapped_column(String(20), ForeignKey("refm_announcement_status.code", ondelete="RESTRICT"), nullable=False)

    # scheduled_at : TIMESTAMP
    scheduled_at: Mapped[Optional[datetime]] = mapped_column(DateTime)

    # expires_at : TIMESTAMP
    expires_at: Mapped[Optional[datetime]] = mapped_column(DateTime)

    # created_by : CHAR(36) COLLATE "utf8mb4_unicode_ci"
    created_by: Mapped[Optional[str]] = mapped_column(CHAR(36), ForeignKey("users.user_id", ondelete="SET NULL"))

    # updated_by : CHAR(36) COLLATE "utf8mb4_unicode_ci"
    updated_by: Mapped[Optional[str]] = mapped_column(CHAR(36), ForeignKey("users.user_id", ondelete="SET NULL"))

    # deleted_ind : TINYINT
    deleted_ind: Mapped[Optional[bool]] = mapped_column(Boolean, default=False)

    # deleted_date : TIMESTAMP
    deleted_date: Mapped[Optional[datetime]] = mapped_column(DateTime)

    # deleted_by : CHAR(36) COLLATE "utf8mb4_unicode_ci"
    deleted_by: Mapped[Optional[str]] = mapped_column(CHAR(36), ForeignKey("users.user_id", ondelete="SET NULL"))

    # FORWARD RELATIONSHIPS ------------------------------------------------------------
    # A forward relationship is defined in the table that contains the foreign key.

    # announcements.type_code -> refm_announcement_type.code
    announcements_type_code_refm_announcement_type = relationship(
        "RefmAnnouncementType",
        foreign_keys=[type_code], 
        backref=backref("announcements_type_code_refm_announcement_types", cascade="all, delete-orphan")
    )

    # announcements.audience_code -> refm_announcement_audience.code
    announcements_audience_code_refm_announcement_audience = relationship(
        "RefmAnnouncementAudience",
        foreign_keys=[audience_code], 
        backref=backref("announcements_audience_code_refm_announcement_audiences", cascade="all, delete-orphan")
    )

    # announcements.status_code -> refm_announcement_status.code
    announcements_status_code_refm_announcement_status = relationship(
        "RefmAnnouncementStatus",
        foreign_keys=[status_code], 
        backref=backref("announcements_status_code_refm_announcement_statuss", cascade="all, delete-orphan")
    )

    # announcements.created_by -> users.user_id
    announcements_created_by_users = relationship(
        "Users",
        foreign_keys=[created_by], 
        backref=backref("announcements_created_by_userss", cascade="all, delete-orphan")
    )

    # announcements.updated_by -> users.user_id
    announcements_updated_by_users = relationship(
        "Users",
        foreign_keys=[updated_by], 
        backref=backref("announcements_updated_by_userss", cascade="all, delete-orphan")
    )

    # announcements.deleted_by -> users.user_id
    announcements_deleted_by_users = relationship(
        "Users",
        foreign_keys=[deleted_by], 
        backref=backref("announcements_deleted_by_userss", cascade="all, delete-orphan")
    )

    # FORWARD RELATIONSHIPS ------------------------------------------------------------

