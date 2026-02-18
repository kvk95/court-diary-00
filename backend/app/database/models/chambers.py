"""chambers"""

from sqlalchemy import ForeignKey, BigInteger, Boolean, CHAR, Date, DateTime, String
from sqlalchemy.orm import relationship, backref
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql import func, text
from datetime import date, datetime
from typing import Any, Optional

from app.database.models.base.base_model import BaseModel
from app.database.models.base.timestampmixin import TimestampMixin

class Chambers(BaseModel, TimestampMixin):
    __tablename__ = 'chambers'

    # chamber_id : BIGINT
    chamber_id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True, nullable=False)

    # chamber_name : VARCHAR(150) COLLATE "utf8mb4_unicode_ci"
    chamber_name: Mapped[str] = mapped_column(String(150), nullable=False)

    # email : VARCHAR(100) COLLATE "utf8mb4_unicode_ci"
    email: Mapped[Optional[str]] = mapped_column(String(100))

    # phone : VARCHAR(20) COLLATE "utf8mb4_unicode_ci"
    phone: Mapped[Optional[str]] = mapped_column(String(20))

    # address_line1 : VARCHAR(255) COLLATE "utf8mb4_unicode_ci"
    address_line1: Mapped[Optional[str]] = mapped_column(String(255))

    # address_line2 : VARCHAR(255) COLLATE "utf8mb4_unicode_ci"
    address_line2: Mapped[Optional[str]] = mapped_column(String(255))

    # city : VARCHAR(50) COLLATE "utf8mb4_unicode_ci"
    city: Mapped[Optional[str]] = mapped_column(String(50))

    # state_code : CHAR(2) COLLATE "utf8mb4_unicode_ci"
    state_code: Mapped[Optional[str]] = mapped_column(CHAR(2), ForeignKey("refm_states.state_code"), default='TN')

    # postal_code : VARCHAR(10) COLLATE "utf8mb4_unicode_ci"
    postal_code: Mapped[Optional[str]] = mapped_column(String(10))

    # country_code : CHAR(2) COLLATE "utf8mb4_unicode_ci"
    country_code: Mapped[Optional[str]] = mapped_column(CHAR(2), ForeignKey("refm_countries.country_code"), default='IN')

    # plan_code : CHAR(2) COLLATE "utf8mb4_unicode_ci"
    plan_code: Mapped[Optional[str]] = mapped_column(CHAR(2), ForeignKey("refm_plan_types.plan_code"), default='FR')

    # subscription_start : DATE
    subscription_start: Mapped[Optional[date]] = mapped_column(Date)

    # subscription_end : DATE
    subscription_end: Mapped[Optional[date]] = mapped_column(Date)

    # is_active : TINYINT
    is_active: Mapped[Optional[bool]] = mapped_column(Boolean, default=True)

    # is_deleted : TINYINT
    is_deleted: Mapped[Optional[bool]] = mapped_column(Boolean, default=False)

    # deleted_date : TIMESTAMP
    deleted_date: Mapped[Optional[datetime]] = mapped_column(DateTime)

    # created_by : BIGINT
    created_by: Mapped[Optional[int]] = mapped_column(BigInteger)

    # updated_by : BIGINT
    updated_by: Mapped[Optional[int]] = mapped_column(BigInteger)

    # FORWARD RELATIONSHIPS ------------------------------------------------------------
    # A forward relationship is defined in the table that contains the foreign key.

    # chambers.state_code -> refm_states.state_code
    chambers_state_code_refm_states = relationship(
        "RefmStates",
        foreign_keys=[state_code], 
        backref=backref("chambers_state_code_refm_statess", cascade="all, delete-orphan")
    )

    # chambers.country_code -> refm_countries.country_code
    chambers_country_code_refm_countries = relationship(
        "RefmCountries",
        foreign_keys=[country_code], 
        backref=backref("chambers_country_code_refm_countriess", cascade="all, delete-orphan")
    )

    # chambers.plan_code -> refm_plan_types.plan_code
    chambers_plan_code_refm_plan_types = relationship(
        "RefmPlanTypes",
        foreign_keys=[plan_code], 
        backref=backref("chambers_plan_code_refm_plan_typess", cascade="all, delete-orphan")
    )

    # FORWARD RELATIONSHIPS ------------------------------------------------------------

