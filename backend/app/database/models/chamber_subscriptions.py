"""chamber_subscriptions"""

from sqlalchemy import ForeignKey, CHAR, Date, Numeric
from sqlalchemy.orm import relationship, backref
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql import func, text
from datetime import date
from typing import Any, Optional

from app.database.models.base.base_model import BaseModel
from app.database.models.base.timestampmixin import TimestampMixin

class ChamberSubscriptions(BaseModel, TimestampMixin):
    __tablename__ = 'chamber_subscriptions'

    # subscription_id : CHAR(36) COLLATE "utf8mb4_unicode_ci"
    subscription_id: Mapped[str] = mapped_column(CHAR(36), primary_key=True, nullable=False)

    # chamber_id : CHAR(36) COLLATE "utf8mb4_unicode_ci"
    chamber_id: Mapped[str] = mapped_column(CHAR(36), ForeignKey("chamber.chamber_id", ondelete="CASCADE"), nullable=False)

    # plan_code : CHAR(4) COLLATE "utf8mb4_unicode_ci"
    plan_code: Mapped[str] = mapped_column(CHAR(4), ForeignKey("refm_plan_types.code", ondelete="RESTRICT"), nullable=False)

    # billing_cycle : CHAR(4) COLLATE "utf8mb4_unicode_ci"
    billing_cycle: Mapped[str] = mapped_column(CHAR(4), ForeignKey("refm_billing_cycle.code", ondelete="RESTRICT"), nullable=False)

    # start_date : DATE
    start_date: Mapped[date] = mapped_column(Date, nullable=False)

    # end_date : DATE
    end_date: Mapped[Optional[date]] = mapped_column(Date)

    # next_renewal_date : DATE
    next_renewal_date: Mapped[Optional[date]] = mapped_column(Date)

    # status_code : CHAR(4) COLLATE "utf8mb4_unicode_ci"
    status_code: Mapped[str] = mapped_column(CHAR(4), ForeignKey("refm_subscription_status.code", ondelete="RESTRICT"), nullable=False)

    # price_amt : DECIMAL(12, 2)
    price_amt: Mapped[float] = mapped_column(Numeric, nullable=False)

    # currency_code : CHAR(3) COLLATE "utf8mb4_unicode_ci"
    currency_code: Mapped[Optional[str]] = mapped_column(CHAR(3), ForeignKey("refm_currency.code", ondelete="RESTRICT"), default='INR')

    # created_by : CHAR(36) COLLATE "utf8mb4_unicode_ci"
    created_by: Mapped[Optional[str]] = mapped_column(CHAR(36))

    # updated_by : CHAR(36) COLLATE "utf8mb4_unicode_ci"
    updated_by: Mapped[Optional[str]] = mapped_column(CHAR(36))

    # FORWARD RELATIONSHIPS ------------------------------------------------------------
    # A forward relationship is defined in the table that contains the foreign key.

    # chamber_subscriptions.chamber_id -> chamber.chamber_id
    chamber_subscriptions_chamber_id_chamber = relationship(
        "Chamber",
        foreign_keys=[chamber_id], 
        backref=backref("chamber_subscriptions_chamber_id_chambers", cascade="all, delete-orphan")
    )

    # chamber_subscriptions.plan_code -> refm_plan_types.code
    chamber_subscriptions_plan_code_refm_plan_types = relationship(
        "RefmPlanTypes",
        foreign_keys=[plan_code], 
        backref=backref("chamber_subscriptions_plan_code_refm_plan_typess", cascade="all, delete-orphan")
    )

    # chamber_subscriptions.billing_cycle -> refm_billing_cycle.code
    chamber_subscriptions_billing_cycle_refm_billing_cycle = relationship(
        "RefmBillingCycle",
        foreign_keys=[billing_cycle], 
        backref=backref("chamber_subscriptions_billing_cycle_refm_billing_cycles", cascade="all, delete-orphan")
    )

    # chamber_subscriptions.status_code -> refm_subscription_status.code
    chamber_subscriptions_status_code_refm_subscription_status = relationship(
        "RefmSubscriptionStatus",
        foreign_keys=[status_code], 
        backref=backref("chamber_subscriptions_status_code_refm_subscription_statuss", cascade="all, delete-orphan")
    )

    # chamber_subscriptions.currency_code -> refm_currency.code
    chamber_subscriptions_currency_code_refm_currency = relationship(
        "RefmCurrency",
        foreign_keys=[currency_code], 
        backref=backref("chamber_subscriptions_currency_code_refm_currencys", cascade="all, delete-orphan")
    )

    # FORWARD RELATIONSHIPS ------------------------------------------------------------

