"""cases"""

from sqlalchemy import ForeignKey, Boolean, CHAR, Date, DateTime, Integer, String, Text
from sqlalchemy.orm import relationship, backref
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql import func, text
from datetime import date, datetime
from typing import Any, Optional

from app.database.models.base.base_model import BaseModel
from app.database.models.base.timestampmixin import TimestampMixin

class Cases(BaseModel, TimestampMixin):
    __tablename__ = 'cases'

    # case_id : CHAR(36) COLLATE "utf8mb4_unicode_ci"
    case_id: Mapped[str] = mapped_column(CHAR(36), primary_key=True, nullable=False)

    # chamber_id : CHAR(36) COLLATE "utf8mb4_unicode_ci"
    chamber_id: Mapped[str] = mapped_column(CHAR(36), ForeignKey("chamber.chamber_id", ondelete="CASCADE"), nullable=False)

    # case_number : VARCHAR(120) COLLATE "utf8mb4_unicode_ci"
    case_number: Mapped[str] = mapped_column(String(120), nullable=False)

    # court_id : INTEGER
    court_id: Mapped[int] = mapped_column(Integer, ForeignKey("refm_courts.court_id", ondelete="RESTRICT"), nullable=False)

    # case_type_code : CHAR(4) COLLATE "utf8mb4_unicode_ci"
    case_type_code: Mapped[Optional[str]] = mapped_column(CHAR(4), ForeignKey("refm_case_types.code", ondelete="RESTRICT"))

    # filing_year : INTEGER
    filing_year: Mapped[Optional[int]] = mapped_column(Integer)

    # petitioner : TEXT COLLATE "utf8mb4_unicode_ci"
    petitioner: Mapped[str] = mapped_column(Text, nullable=False)

    # respondent : TEXT COLLATE "utf8mb4_unicode_ci"
    respondent: Mapped[str] = mapped_column(Text, nullable=False)

    # aor_user_id : CHAR(36) COLLATE "utf8mb4_unicode_ci"
    aor_user_id: Mapped[Optional[str]] = mapped_column(CHAR(36), ForeignKey("users.user_id", ondelete="SET NULL"))

    # case_summary : TEXT COLLATE "utf8mb4_unicode_ci"
    case_summary: Mapped[Optional[str]] = mapped_column(Text)

    # status_code : CHAR(4) COLLATE "utf8mb4_unicode_ci"
    status_code: Mapped[Optional[str]] = mapped_column(CHAR(4), ForeignKey("refm_case_status.code", ondelete="RESTRICT"), default='AC')

    # next_hearing_date : DATE
    next_hearing_date: Mapped[Optional[date]] = mapped_column(Date)

    # last_hearing_date : DATE
    last_hearing_date: Mapped[Optional[date]] = mapped_column(Date)

    # deleted_ind : TINYINT
    deleted_ind: Mapped[Optional[bool]] = mapped_column(Boolean, default=False)

    # deleted_date : TIMESTAMP
    deleted_date: Mapped[Optional[datetime]] = mapped_column(DateTime)

    # deleted_by : CHAR(36) COLLATE "utf8mb4_unicode_ci"
    deleted_by: Mapped[Optional[str]] = mapped_column(CHAR(36))

    # created_by : CHAR(36) COLLATE "utf8mb4_unicode_ci"
    created_by: Mapped[Optional[str]] = mapped_column(CHAR(36))

    # updated_by : CHAR(36) COLLATE "utf8mb4_unicode_ci"
    updated_by: Mapped[Optional[str]] = mapped_column(CHAR(36))

    # FORWARD RELATIONSHIPS ------------------------------------------------------------
    # A forward relationship is defined in the table that contains the foreign key.

    # cases.chamber_id -> chamber.chamber_id
    cases_chamber_id_chamber = relationship(
        "Chamber",
        foreign_keys=[chamber_id], 
        backref=backref("cases_chamber_id_chambers", cascade="all, delete-orphan")
    )

    # cases.court_id -> refm_courts.court_id
    cases_court_id_refm_courts = relationship(
        "RefmCourts",
        foreign_keys=[court_id], 
        backref=backref("cases_court_id_refm_courtss", cascade="all, delete-orphan")
    )

    # cases.case_type_code -> refm_case_types.code
    cases_case_type_code_refm_case_types = relationship(
        "RefmCaseTypes",
        foreign_keys=[case_type_code], 
        backref=backref("cases_case_type_code_refm_case_typess", cascade="all, delete-orphan")
    )

    # cases.aor_user_id -> users.user_id
    cases_aor_user_id_users = relationship(
        "Users",
        foreign_keys=[aor_user_id], 
        backref=backref("cases_aor_user_id_userss", cascade="all, delete-orphan")
    )

    # cases.status_code -> refm_case_status.code
    cases_status_code_refm_case_status = relationship(
        "RefmCaseStatus",
        foreign_keys=[status_code], 
        backref=backref("cases_status_code_refm_case_statuss", cascade="all, delete-orphan")
    )

    # FORWARD RELATIONSHIPS ------------------------------------------------------------

