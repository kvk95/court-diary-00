"""db_call_log"""

from sqlalchemy import ForeignKey, BigInteger, DOUBLE, Date, DateTime, JSON, String
from sqlalchemy.dialects.mysql import LONGTEXT
from sqlalchemy.orm import relationship, backref
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql import func, text
from datetime import date, datetime
from typing import Any, Optional

from app.database.models.base.base_model import BaseModel

class DbCallLog(BaseModel):
    __tablename__ = 'db_call_log'

    # id : BIGINT
    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True, nullable=False)

    # chamber_id : BIGINT
    chamber_id: Mapped[Optional[int]] = mapped_column(BigInteger, ForeignKey("chamber.chamber_id", ondelete="SET NULL"))

    # user_id : BIGINT
    user_id: Mapped[Optional[int]] = mapped_column(BigInteger, ForeignKey("users.user_id", ondelete="SET NULL"))

    # timestamp : DATETIME
    timestamp: Mapped[date] = mapped_column(Date, nullable=False)

    # duration_ms : DOUBLE
    duration_ms: Mapped[float] = mapped_column(DOUBLE, nullable=False)

    # raw_query : LONGTEXT
    raw_query: Mapped[str] = mapped_column(LONGTEXT, nullable=False)

    # params : JSON
    params: Mapped[Optional[Any]] = mapped_column(JSON, default=[])

    # final_query : LONGTEXT
    final_query: Mapped[Optional[str]] = mapped_column(LONGTEXT)

    # repo : VARCHAR(255) COLLATE "utf8mb4_unicode_ci"
    repo: Mapped[Optional[str]] = mapped_column(String(255))

    # error : LONGTEXT
    error: Mapped[Optional[str]] = mapped_column(LONGTEXT)

    # metadata_json : JSON
    metadata_json: Mapped[Optional[Any]] = mapped_column(JSON, default=[])

    # created_date : TIMESTAMP
    created_date: Mapped[Optional[datetime]] = mapped_column(DateTime, server_default=func.current_timestamp())

    # created_by : BIGINT
    created_by: Mapped[Optional[int]] = mapped_column(BigInteger, ForeignKey("users.user_id", ondelete="SET NULL"))

    # FORWARD RELATIONSHIPS ------------------------------------------------------------
    # A forward relationship is defined in the table that contains the foreign key.

    # db_call_log.chamber_id -> chamber.chamber_id
    db_call_log_chamber_id_chamber = relationship(
        "Chamber",
        foreign_keys=[chamber_id], 
        backref=backref("db_call_log_chamber_id_chambers", cascade="all, delete-orphan")
    )

    # db_call_log.user_id -> users.user_id
    db_call_log_user_id_users = relationship(
        "Users",
        foreign_keys=[user_id], 
        backref=backref("db_call_log_user_id_userss", cascade="all, delete-orphan")
    )

    # db_call_log.created_by -> users.user_id
    db_call_log_created_by_users = relationship(
        "Users",
        foreign_keys=[created_by], 
        backref=backref("db_call_log_created_by_userss", cascade="all, delete-orphan")
    )

    # FORWARD RELATIONSHIPS ------------------------------------------------------------

