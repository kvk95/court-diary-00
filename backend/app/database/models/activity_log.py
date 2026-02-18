"""activity_log"""

from sqlalchemy import ForeignKey, BigInteger, DateTime, JSON, String
from sqlalchemy.orm import relationship, backref
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql import func, text
from datetime import datetime
from typing import Any, Optional

from app.database.models.base.base_model import BaseModel

class ActivityLog(BaseModel):
    __tablename__ = 'activity_log'

    # log_id : BIGINT
    log_id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True, nullable=False)

    # chamber_id : BIGINT
    chamber_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("chambers.chamber_id"), nullable=False)

    # user_id : BIGINT
    user_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("users.user_id"), nullable=False)

    # action_type : VARCHAR(50) COLLATE "utf8mb4_unicode_ci"
    action_type: Mapped[str] = mapped_column(String(50), nullable=False)

    # entity_type : VARCHAR(50) COLLATE "utf8mb4_unicode_ci"
    entity_type: Mapped[str] = mapped_column(String(50), nullable=False)

    # entity_id : BIGINT
    entity_id: Mapped[Optional[int]] = mapped_column(BigInteger)

    # old_values : JSON
    old_values: Mapped[Optional[Any]] = mapped_column(JSON, default=[])

    # new_values : JSON
    new_values: Mapped[Optional[Any]] = mapped_column(JSON, default=[])

    # ip_address : VARCHAR(45) COLLATE "utf8mb4_unicode_ci"
    ip_address: Mapped[Optional[str]] = mapped_column(String(45))

    # user_agent : VARCHAR(255) COLLATE "utf8mb4_unicode_ci"
    user_agent: Mapped[Optional[str]] = mapped_column(String(255))

    # created_date : TIMESTAMP
    created_date: Mapped[Optional[datetime]] = mapped_column(DateTime, server_default=func.current_timestamp())

    # FORWARD RELATIONSHIPS ------------------------------------------------------------
    # A forward relationship is defined in the table that contains the foreign key.

    # activity_log.chamber_id -> chambers.chamber_id
    activity_log_chamber_id_chambers = relationship(
        "Chambers",
        foreign_keys=[chamber_id], 
        backref=backref("activity_log_chamber_id_chamberss", cascade="all, delete-orphan")
    )

    # activity_log.user_id -> users.user_id
    activity_log_user_id_users = relationship(
        "Users",
        foreign_keys=[user_id], 
        backref=backref("activity_log_user_id_userss", cascade="all, delete-orphan")
    )

    # FORWARD RELATIONSHIPS ------------------------------------------------------------

