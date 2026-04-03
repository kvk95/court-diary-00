"""exception_log"""

from sqlalchemy import ForeignKey, CHAR, Date, DateTime, JSON, String
from sqlalchemy.dialects.mysql import LONGTEXT
from sqlalchemy.orm import relationship, backref
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql import func, text
from datetime import date, datetime
from typing import Any, Optional

from app.database.models.base.base_model import BaseModel

class ExceptionLog(BaseModel):
    __tablename__ = 'exception_log'

    # id : CHAR(36) COLLATE "utf8mb4_unicode_ci"
    id: Mapped[str] = mapped_column(CHAR(36), primary_key=True, nullable=False)

    # timestamp : DATETIME
    timestamp: Mapped[date] = mapped_column(Date, nullable=False)

    # exception_type : VARCHAR(255) COLLATE "utf8mb4_unicode_ci"
    exception_type: Mapped[str] = mapped_column(String(255), nullable=False)

    # message : LONGTEXT
    message: Mapped[Optional[str]] = mapped_column(LONGTEXT)

    # stacktrace : LONGTEXT
    stacktrace: Mapped[Optional[str]] = mapped_column(LONGTEXT)

    # path : VARCHAR(500) COLLATE "utf8mb4_unicode_ci"
    path: Mapped[Optional[str]] = mapped_column(String(500))

    # method : VARCHAR(10) COLLATE "utf8mb4_unicode_ci"
    method: Mapped[Optional[str]] = mapped_column(String(10))

    # query_params : JSON
    query_params: Mapped[Optional[Any]] = mapped_column(JSON, default=[])

    # request_body : LONGTEXT
    request_body: Mapped[Optional[str]] = mapped_column(LONGTEXT)

    # headers : JSON
    headers: Mapped[Optional[Any]] = mapped_column(JSON, default=[])

    # error_code : VARCHAR(50) COLLATE "utf8mb4_unicode_ci"
    error_code: Mapped[Optional[str]] = mapped_column(String(50))

    # metadata_json : JSON
    metadata_json: Mapped[Optional[Any]] = mapped_column(JSON, default=[])

    # actor_user_id : CHAR(36) COLLATE "utf8mb4_unicode_ci"
    actor_user_id: Mapped[Optional[str]] = mapped_column(CHAR(36), ForeignKey("users.user_id", ondelete="SET NULL"))

    # actor_chamber_id : CHAR(36) COLLATE "utf8mb4_unicode_ci"
    actor_chamber_id: Mapped[Optional[str]] = mapped_column(CHAR(36), ForeignKey("chamber.chamber_id", ondelete="SET NULL"))

    # created_date : TIMESTAMP
    created_date: Mapped[Optional[datetime]] = mapped_column(DateTime, server_default=func.current_timestamp())

    # FORWARD RELATIONSHIPS ------------------------------------------------------------
    # A forward relationship is defined in the table that contains the foreign key.

    # exception_log.actor_user_id -> users.user_id
    exception_log_actor_user_id_users = relationship(
        "Users",
        foreign_keys=[actor_user_id], 
        backref=backref("exception_log_actor_user_id_userss", cascade="all, delete-orphan")
    )

    # exception_log.actor_chamber_id -> chamber.chamber_id
    exception_log_actor_chamber_id_chamber = relationship(
        "Chamber",
        foreign_keys=[actor_chamber_id], 
        backref=backref("exception_log_actor_chamber_id_chambers", cascade="all, delete-orphan")
    )

    # FORWARD RELATIONSHIPS ------------------------------------------------------------

