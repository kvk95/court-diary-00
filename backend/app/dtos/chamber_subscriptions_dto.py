# app/dtos/chamber_subscriptions_dto.py

from datetime import date, datetime
from typing import Optional
from app.dtos.base.base_data import BaseInData, BaseRecordData


class SubscriptionStats(BaseRecordData):

    plan_code: Optional[str]
    plan_name: Optional[str]

    users_used: int
    users_allowed: Optional[int]

    cases_used: int
    cases_allowed: Optional[int]

    next_renewal_date: Optional[date]
    next_amount: Optional[float]

class SubscriptionPlanItem(BaseRecordData):
    code: str
    description: str

    email_ind: bool
    sms_ind: bool
    whatsapp_ind: bool

    max_users: Optional[int]
    max_cases: Optional[int]

    price_monthly_amt: float
    price_annual_amt: float


class ChamberSubscriptionOut(BaseRecordData):
    plan_code: Optional[str]
    plan_name: Optional[str]

    billing_cycle: Optional[str]
    billing_cycle_desc: Optional[str]

    status_code: Optional[str]
    status_description: Optional[str]

    next_renewal_date: Optional[date]
    next_amount: Optional[float]

    max_users: Optional[int]
    max_cases: Optional[int]

class ChangePlanIn(BaseInData):
    plan_code: str
    billing_cycle: str

class UsageStats(BaseRecordData):
    users_used: int
    users_allowed: Optional[int]

    cases_used: int
    cases_allowed: Optional[int]

class CancelSubscriptionIn(BaseInData):
    reason: Optional[str] = None

class BillingInvoiceItem(BaseRecordData):
    invoice_id: str
    invoice_number: str

    period_label: str   # "Feb 2026"
    amount: float

    status_code: str
    status_description: str

    invoice_date: datetime