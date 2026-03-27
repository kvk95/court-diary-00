"""case_aors"""

from sqlalchemy import ForeignKey, Boolean, CHAR, Date, DateTime, Text
from sqlalchemy.orm import relationship, backref
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql import func, text
from datetime import date, datetime
from typing import Any, Optional

from app.database.models.base.base_model import BaseModel

class CaseAors(BaseModel):
    __tablename__ = 'case_aors'

    # case_aor_id : CHAR(36) COLLATE "utf8mb4_unicode_ci"
    case_aor_id: Mapped[str] = mapped_column(CHAR(36), primary_key=True, nullable=False)

    # case_id : CHAR(36) COLLATE "utf8mb4_unicode_ci"
    case_id: Mapped[str] = mapped_column(CHAR(36), ForeignKey("cases.case_id", ondelete="CASCADE"), nullable=False)

    # user_id : CHAR(36) COLLATE "utf8mb4_unicode_ci"
    user_id: Mapped[str] = mapped_column(CHAR(36), ForeignKey("users.user_id", ondelete="CASCADE"), nullable=False)

    # chamber_id : CHAR(36) COLLATE "utf8mb4_unicode_ci"
    chamber_id: Mapped[str] = mapped_column(CHAR(36), ForeignKey("chamber.chamber_id", ondelete="CASCADE"), nullable=False)

    # primary_ind : TINYINT
    primary_ind: Mapped[Optional[bool]] = mapped_column(Boolean, default=False)

    # appointment_date : DATE
    appointment_date: Mapped[Optional[date]] = mapped_column(Date)

    # withdrawal_date : DATE
    withdrawal_date: Mapped[Optional[date]] = mapped_column(Date)

    # status_code : CHAR(4) COLLATE "utf8mb4_unicode_ci"
    status_code: Mapped[Optional[str]] = mapped_column(CHAR(4), default='CSAC')

    # notes : TEXT COLLATE "utf8mb4_unicode_ci"
    notes: Mapped[Optional[str]] = mapped_column(Text)

    # created_date : TIMESTAMP
    created_date: Mapped[Optional[datetime]] = mapped_column(DateTime, server_default=func.current_timestamp())

    # created_by : CHAR(36) COLLATE "utf8mb4_unicode_ci"
    created_by: Mapped[Optional[str]] = mapped_column(CHAR(36), ForeignKey("users.user_id", ondelete="SET NULL"))

    # FORWARD RELATIONSHIPS ------------------------------------------------------------
    # A forward relationship is defined in the table that contains the foreign key.

    # case_aors.case_id -> cases.case_id
    case_aors_case_id_cases = relationship(
        "Cases",
        foreign_keys=[case_id], 
        backref=backref("case_aors_case_id_casess", cascade="all, delete-orphan")
    )

    # case_aors.user_id -> users.user_id
    case_aors_user_id_users = relationship(
        "Users",
        foreign_keys=[user_id], 
        backref=backref("case_aors_user_id_userss", cascade="all, delete-orphan")
    )

    # case_aors.chamber_id -> chamber.chamber_id
    case_aors_chamber_id_chamber = relationship(
        "Chamber",
        foreign_keys=[chamber_id], 
        backref=backref("case_aors_chamber_id_chambers", cascade="all, delete-orphan")
    )

    # case_aors.created_by -> users.user_id
    case_aors_created_by_users = relationship(
        "Users",
        foreign_keys=[created_by], 
        backref=backref("case_aors_created_by_userss", cascade="all, delete-orphan")
    )

    # FORWARD RELATIONSHIPS ------------------------------------------------------------

