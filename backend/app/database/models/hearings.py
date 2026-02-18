"""hearings"""

from sqlalchemy import ForeignKey, BigInteger, Boolean, CHAR, Date, DateTime, String, Text
from sqlalchemy.orm import relationship, backref
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql import func, text
from datetime import date, datetime
from typing import Any, Optional

from app.database.models.base.base_model import BaseModel
from app.database.models.base.timestampmixin import TimestampMixin

class Hearings(BaseModel, TimestampMixin):
    __tablename__ = 'hearings'

    # hearing_id : BIGINT
    hearing_id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True, nullable=False)

    # chamber_id : BIGINT
    chamber_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("chambers.chamber_id", ondelete="CASCADE"), nullable=False)

    # case_id : BIGINT
    case_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("cases.case_id", ondelete="CASCADE"), nullable=False)

    # hearing_date : DATE
    hearing_date: Mapped[date] = mapped_column(Date, nullable=False)

    # status_code : CHAR(4) COLLATE "utf8mb4_unicode_ci"
    status_code: Mapped[Optional[str]] = mapped_column(CHAR(4), ForeignKey("refm_hearing_status.code", ondelete="RESTRICT"), default='UP')

    # purpose : VARCHAR(255) COLLATE "utf8mb4_unicode_ci"
    purpose: Mapped[Optional[str]] = mapped_column(String(255))

    # notes : TEXT COLLATE "utf8mb4_unicode_ci"
    notes: Mapped[Optional[str]] = mapped_column(Text)

    # order_details : TEXT COLLATE "utf8mb4_unicode_ci"
    order_details: Mapped[Optional[str]] = mapped_column(Text)

    # next_hearing_date : DATE
    next_hearing_date: Mapped[Optional[date]] = mapped_column(Date)

    # is_deleted : TINYINT
    is_deleted: Mapped[Optional[bool]] = mapped_column(Boolean, default=False)

    # deleted_date : TIMESTAMP
    deleted_date: Mapped[Optional[datetime]] = mapped_column(DateTime)

    # deleted_by : BIGINT
    deleted_by: Mapped[Optional[int]] = mapped_column(BigInteger)

    # created_by : BIGINT
    created_by: Mapped[Optional[int]] = mapped_column(BigInteger)

    # updated_by : BIGINT
    updated_by: Mapped[Optional[int]] = mapped_column(BigInteger)

    # FORWARD RELATIONSHIPS ------------------------------------------------------------
    # A forward relationship is defined in the table that contains the foreign key.

    # hearings.chamber_id -> chambers.chamber_id
    hearings_chamber_id_chambers = relationship(
        "Chambers",
        foreign_keys=[chamber_id], 
        backref=backref("hearings_chamber_id_chamberss", cascade="all, delete-orphan")
    )

    # hearings.case_id -> cases.case_id
    hearings_case_id_cases = relationship(
        "Cases",
        foreign_keys=[case_id], 
        backref=backref("hearings_case_id_casess", cascade="all, delete-orphan")
    )

    # hearings.status_code -> refm_hearing_status.code
    hearings_status_code_refm_hearing_status = relationship(
        "RefmHearingStatus",
        foreign_keys=[status_code], 
        backref=backref("hearings_status_code_refm_hearing_statuss", cascade="all, delete-orphan")
    )

    # FORWARD RELATIONSHIPS ------------------------------------------------------------

