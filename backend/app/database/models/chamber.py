"""chamber"""

from sqlalchemy import ForeignKey, Boolean, CHAR, Date, DateTime, String
from sqlalchemy.orm import relationship, backref
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql import func, text
from datetime import date, datetime
from typing import Any, Optional

from app.database.models.base.base_model import BaseModel
from app.database.models.base.timestampmixin import TimestampMixin

class Chamber(BaseModel, TimestampMixin):
    __tablename__ = 'chamber'

    # chamber_id : CHAR(36) COLLATE "utf8mb4_unicode_ci"
    chamber_id: Mapped[str] = mapped_column(CHAR(36), primary_key=True, nullable=False)

    # chamber_name : VARCHAR(150) COLLATE "utf8mb4_unicode_ci"
    chamber_name: Mapped[str] = mapped_column(String(150), nullable=False)

    # email : VARCHAR(120) COLLATE "utf8mb4_unicode_ci"
    email: Mapped[Optional[str]] = mapped_column(String(120))

    # phone : VARCHAR(20) COLLATE "utf8mb4_unicode_ci"
    phone: Mapped[Optional[str]] = mapped_column(String(20))

    # address_line1 : VARCHAR(255) COLLATE "utf8mb4_unicode_ci"
    address_line1: Mapped[Optional[str]] = mapped_column(String(255))

    # address_line2 : VARCHAR(255) COLLATE "utf8mb4_unicode_ci"
    address_line2: Mapped[Optional[str]] = mapped_column(String(255))

    # city : VARCHAR(80) COLLATE "utf8mb4_unicode_ci"
    city: Mapped[Optional[str]] = mapped_column(String(80))

    # state_code : CHAR(4) COLLATE "utf8mb4_unicode_ci"
    state_code: Mapped[Optional[str]] = mapped_column(CHAR(4), ForeignKey("refm_states.code", ondelete="RESTRICT"), default='TN')

    # postal_code : VARCHAR(12) COLLATE "utf8mb4_unicode_ci"
    postal_code: Mapped[Optional[str]] = mapped_column(String(12))

    # country_code : CHAR(2) COLLATE "utf8mb4_unicode_ci"
    country_code: Mapped[Optional[str]] = mapped_column(CHAR(2), ForeignKey("refm_countries.code", ondelete="RESTRICT"), default='IN')

    # plan_code : CHAR(4) COLLATE "utf8mb4_unicode_ci"
    plan_code: Mapped[Optional[str]] = mapped_column(CHAR(4), ForeignKey("refm_plan_types.code", ondelete="RESTRICT"), default='FREE')

    # subscription_start : DATE
    subscription_start: Mapped[Optional[date]] = mapped_column(Date)

    # subscription_end : DATE
    subscription_end: Mapped[Optional[date]] = mapped_column(Date)

    # status_ind : TINYINT
    status_ind: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    # deleted_ind : TINYINT
    deleted_ind: Mapped[Optional[bool]] = mapped_column(Boolean, default=False)

    # deleted_date : TIMESTAMP
    deleted_date: Mapped[Optional[datetime]] = mapped_column(DateTime)

    # deleted_by : CHAR(36) COLLATE "utf8mb4_unicode_ci"
    deleted_by: Mapped[Optional[str]] = mapped_column(CHAR(36), ForeignKey("users.user_id", ondelete="SET NULL"))

    # created_by : CHAR(36) COLLATE "utf8mb4_unicode_ci"
    created_by: Mapped[Optional[str]] = mapped_column(CHAR(36), ForeignKey("users.user_id", ondelete="SET NULL"))

    # updated_by : CHAR(36) COLLATE "utf8mb4_unicode_ci"
    updated_by: Mapped[Optional[str]] = mapped_column(CHAR(36), ForeignKey("users.user_id", ondelete="SET NULL"))

    # FORWARD RELATIONSHIPS ------------------------------------------------------------
    # A forward relationship is defined in the table that contains the foreign key.

    # chamber.state_code -> refm_states.code
    chamber_state_code_refm_states = relationship(
        "RefmStates",
        foreign_keys=[state_code], 
        backref=backref("chamber_state_code_refm_statess", cascade="all, delete-orphan")
    )

    # chamber.country_code -> refm_countries.code
    chamber_country_code_refm_countries = relationship(
        "RefmCountries",
        foreign_keys=[country_code], 
        backref=backref("chamber_country_code_refm_countriess", cascade="all, delete-orphan")
    )

    # chamber.plan_code -> refm_plan_types.code
    chamber_plan_code_refm_plan_types = relationship(
        "RefmPlanTypes",
        foreign_keys=[plan_code], 
        backref=backref("chamber_plan_code_refm_plan_typess", cascade="all, delete-orphan")
    )

    # chamber.deleted_by -> users.user_id
    chamber_deleted_by_users = relationship(
        "Users",
        foreign_keys=[deleted_by], 
        backref=backref("chamber_deleted_by_userss", cascade="all, delete-orphan")
    )

    # chamber.created_by -> users.user_id
    chamber_created_by_users = relationship(
        "Users",
        foreign_keys=[created_by], 
        backref=backref("chamber_created_by_userss", cascade="all, delete-orphan")
    )

    # chamber.updated_by -> users.user_id
    chamber_updated_by_users = relationship(
        "Users",
        foreign_keys=[updated_by], 
        backref=backref("chamber_updated_by_userss", cascade="all, delete-orphan")
    )

    # FORWARD RELATIONSHIPS ------------------------------------------------------------

