"""billing_invoices"""

from sqlalchemy import ForeignKey, CHAR, Date, DateTime, Numeric, String
from sqlalchemy.orm import relationship, backref
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql import func, text
from datetime import date, datetime
from typing import Any, Optional

from app.database.models.base.base_model import BaseModel

class BillingInvoices(BaseModel):
    __tablename__ = 'billing_invoices'

    # invoice_id : CHAR(36) COLLATE "utf8mb4_unicode_ci"
    invoice_id: Mapped[str] = mapped_column(CHAR(36), primary_key=True, nullable=False)

    # chamber_id : CHAR(36) COLLATE "utf8mb4_unicode_ci"
    chamber_id: Mapped[str] = mapped_column(CHAR(36), ForeignKey("chamber.chamber_id", ondelete="CASCADE"), nullable=False)

    # subscription_id : CHAR(36) COLLATE "utf8mb4_unicode_ci"
    subscription_id: Mapped[str] = mapped_column(CHAR(36), ForeignKey("chamber_subscriptions.subscription_id", ondelete="CASCADE"), nullable=False)

    # invoice_number : VARCHAR(50) COLLATE "utf8mb4_unicode_ci"
    invoice_number: Mapped[str] = mapped_column(String(50), nullable=False)

    # period_start : DATE
    period_start: Mapped[date] = mapped_column(Date, nullable=False)

    # period_end : DATE
    period_end: Mapped[date] = mapped_column(Date, nullable=False)

    # amount : DECIMAL(12, 2)
    amount: Mapped[float] = mapped_column(Numeric, nullable=False)

    # currency_code : CHAR(3) COLLATE "utf8mb4_unicode_ci"
    currency_code: Mapped[Optional[str]] = mapped_column(CHAR(3), ForeignKey("refm_currency.code", ondelete="RESTRICT"), default='INR')

    # status_code : CHAR(4) COLLATE "utf8mb4_unicode_ci"
    status_code: Mapped[str] = mapped_column(CHAR(4), ForeignKey("refm_invoice_status.code", ondelete="CASCADE"), nullable=False)

    # paid_date : DATE
    paid_date: Mapped[Optional[date]] = mapped_column(Date)

    # created_date : TIMESTAMP
    created_date: Mapped[Optional[datetime]] = mapped_column(DateTime, server_default=func.current_timestamp())

    # FORWARD RELATIONSHIPS ------------------------------------------------------------
    # A forward relationship is defined in the table that contains the foreign key.

    # billing_invoices.chamber_id -> chamber.chamber_id
    billing_invoices_chamber_id_chamber = relationship(
        "Chamber",
        foreign_keys=[chamber_id], 
        backref=backref("billing_invoices_chamber_id_chambers", cascade="all, delete-orphan")
    )

    # billing_invoices.subscription_id -> chamber_subscriptions.subscription_id
    billing_invoices_subscription_id_chamber_subscriptions = relationship(
        "ChamberSubscriptions",
        foreign_keys=[subscription_id], 
        backref=backref("billing_invoices_subscription_id_chamber_subscriptionss", cascade="all, delete-orphan")
    )

    # billing_invoices.currency_code -> refm_currency.code
    billing_invoices_currency_code_refm_currency = relationship(
        "RefmCurrency",
        foreign_keys=[currency_code], 
        backref=backref("billing_invoices_currency_code_refm_currencys", cascade="all, delete-orphan")
    )

    # billing_invoices.status_code -> refm_invoice_status.code
    billing_invoices_status_code_refm_invoice_status = relationship(
        "RefmInvoiceStatus",
        foreign_keys=[status_code], 
        backref=backref("billing_invoices_status_code_refm_invoice_statuss", cascade="all, delete-orphan")
    )

    # FORWARD RELATIONSHIPS ------------------------------------------------------------

