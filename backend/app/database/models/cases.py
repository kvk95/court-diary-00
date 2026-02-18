"""cases"""

from sqlalchemy import ForeignKey, BigInteger, Boolean, CHAR, Date, DateTime, Integer, String, Text
from sqlalchemy.orm import relationship, backref
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql import func, text
from datetime import date, datetime
from typing import Any, Optional

from app.database.models.base.base_model import BaseModel
from app.database.models.base.timestampmixin import TimestampMixin

class Cases(BaseModel, TimestampMixin):
    __tablename__ = 'cases'

    # case_id : BIGINT
    case_id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True, nullable=False)

    # chamber_id : BIGINT
    chamber_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("chambers.chamber_id"), nullable=False)

    # case_number : VARCHAR(100) COLLATE "utf8mb4_unicode_ci"
    case_number: Mapped[str] = mapped_column(String(100), nullable=False)

    # court_id : INTEGER
    court_id: Mapped[int] = mapped_column(Integer, ForeignKey("refm_courts.court_id"), nullable=False)

    # type_code : CHAR(3) COLLATE "utf8mb4_unicode_ci"
    type_code: Mapped[Optional[str]] = mapped_column(CHAR(3), ForeignKey("refm_case_types.type_code"))

    # filing_year : INTEGER
    filing_year: Mapped[Optional[int]] = mapped_column(Integer)

    # petitioner : TEXT COLLATE "utf8mb4_unicode_ci"
    petitioner: Mapped[str] = mapped_column(Text, nullable=False)

    # respondent : TEXT COLLATE "utf8mb4_unicode_ci"
    respondent: Mapped[str] = mapped_column(Text, nullable=False)

    # aor_user_id : BIGINT
    aor_user_id: Mapped[Optional[int]] = mapped_column(BigInteger, ForeignKey("users.user_id"))

    # case_summary : TEXT COLLATE "utf8mb4_unicode_ci"
    case_summary: Mapped[Optional[str]] = mapped_column(Text)

    # status_code : CHAR(2) COLLATE "utf8mb4_unicode_ci"
    status_code: Mapped[Optional[str]] = mapped_column(CHAR(2), ForeignKey("refm_case_status.status_code"), default='AC')

    # next_hearing_date : DATE
    next_hearing_date: Mapped[Optional[date]] = mapped_column(Date)

    # last_hearing_date : DATE
    last_hearing_date: Mapped[Optional[date]] = mapped_column(Date)

    # is_deleted : TINYINT
    is_deleted: Mapped[Optional[bool]] = mapped_column(Boolean, default=False)

    # deleted_date : TIMESTAMP
    deleted_date: Mapped[Optional[datetime]] = mapped_column(DateTime)

    # created_by : BIGINT
    created_by: Mapped[Optional[int]] = mapped_column(BigInteger)

    # updated_by : BIGINT
    updated_by: Mapped[Optional[int]] = mapped_column(BigInteger)

    # deleted_by : BIGINT
    deleted_by: Mapped[Optional[int]] = mapped_column(BigInteger)

    # FORWARD RELATIONSHIPS ------------------------------------------------------------
    # A forward relationship is defined in the table that contains the foreign key.

    # cases.chamber_id -> chambers.chamber_id
    cases_chamber_id_chambers = relationship(
        "Chambers",
        foreign_keys=[chamber_id], 
        backref=backref("cases_chamber_id_chamberss", cascade="all, delete-orphan")
    )

    # cases.court_id -> refm_courts.court_id
    cases_court_id_refm_courts = relationship(
        "RefmCourts",
        foreign_keys=[court_id], 
        backref=backref("cases_court_id_refm_courtss", cascade="all, delete-orphan")
    )

    # cases.type_code -> refm_case_types.type_code
    cases_type_code_refm_case_types = relationship(
        "RefmCaseTypes",
        foreign_keys=[type_code], 
        backref=backref("cases_type_code_refm_case_typess", cascade="all, delete-orphan")
    )

    # cases.aor_user_id -> users.user_id
    cases_aor_user_id_users = relationship(
        "Users",
        foreign_keys=[aor_user_id], 
        backref=backref("cases_aor_user_id_userss", cascade="all, delete-orphan")
    )

    # cases.status_code -> refm_case_status.status_code
    cases_status_code_refm_case_status = relationship(
        "RefmCaseStatus",
        foreign_keys=[status_code], 
        backref=backref("cases_status_code_refm_case_statuss", cascade="all, delete-orphan")
    )

    # FORWARD RELATIONSHIPS ------------------------------------------------------------

