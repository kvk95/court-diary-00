"""activity_log"""

from sqlalchemy import ForeignKey, CHAR, Date, DateTime, JSON, String
from sqlalchemy.orm import relationship, backref
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql import func, text
from datetime import date, datetime
from typing import Any, Optional

from app.database.models.base.base_model import BaseModel

class ActivityLog(BaseModel):
    __tablename__ = 'activity_log'

    # id : CHAR(36) COLLATE "utf8mb4_unicode_ci"
    id: Mapped[str] = mapped_column(CHAR(36), primary_key=True, nullable=False)

    # chamber_id : CHAR(36) COLLATE "utf8mb4_unicode_ci"
    chamber_id: Mapped[str] = mapped_column(CHAR(36), ForeignKey("chamber.chamber_id", ondelete="CASCADE"), nullable=False)

    # user_id : CHAR(36) COLLATE "utf8mb4_unicode_ci"
    user_id: Mapped[Optional[str]] = mapped_column(CHAR(36), ForeignKey("users.user_id", ondelete="SET NULL"))

    # timestamp : DATETIME
    timestamp: Mapped[date] = mapped_column(Date, nullable=False)

    # action : VARCHAR(255) COLLATE "utf8mb4_unicode_ci"
    action: Mapped[str] = mapped_column(String(255), nullable=False)

    # target : VARCHAR(255) COLLATE "utf8mb4_unicode_ci"
    target: Mapped[Optional[str]] = mapped_column(String(255))

    # metadata_json : JSON
    metadata_json: Mapped[Optional[Any]] = mapped_column(JSON, default=[])

    # ip_address : VARCHAR(45) COLLATE "utf8mb4_unicode_ci"
    ip_address: Mapped[Optional[str]] = mapped_column(String(45))

    # created_date : TIMESTAMP
    created_date: Mapped[Optional[datetime]] = mapped_column(DateTime, server_default=func.current_timestamp())

    # created_by : CHAR(36) COLLATE "utf8mb4_unicode_ci"
    created_by: Mapped[Optional[str]] = mapped_column(CHAR(36), ForeignKey("users.user_id", ondelete="SET NULL"))

    # FORWARD RELATIONSHIPS ------------------------------------------------------------
    # A forward relationship is defined in the table that contains the foreign key.

    # activity_log.chamber_id -> chamber.chamber_id
    activity_log_chamber_id_chamber = relationship(
        "Chamber",
        foreign_keys=[chamber_id], 
        backref=backref("activity_log_chamber_id_chambers", cascade="all, delete-orphan")
    )

    # activity_log.user_id -> users.user_id
    activity_log_user_id_users = relationship(
        "Users",
        foreign_keys=[user_id], 
        backref=backref("activity_log_user_id_userss", cascade="all, delete-orphan")
    )

    # activity_log.created_by -> users.user_id
    activity_log_created_by_users = relationship(
        "Users",
        foreign_keys=[created_by], 
        backref=backref("activity_log_created_by_userss", cascade="all, delete-orphan")
    )

    # FORWARD RELATIONSHIPS ------------------------------------------------------------

