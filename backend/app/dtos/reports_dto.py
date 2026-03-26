"""reports_dto.py — DTOs for Reports module"""

from typing import List, Optional

from app.dtos.base.base_data import BaseRecordData


# ─────────────────────────────────────────────────────────────────────────────
# CASES
# ─────────────────────────────────────────────────────────────────────────────

class CaseSummaryReport(BaseRecordData):
    total_cases: int = 0
    active_cases: int = 0
    adjourned_cases: int = 0
    disposed_cases: int = 0
    closed_cases: int = 0
    overdue_cases: int = 0
    cases_filed_this_month: int = 0
    cases_filed_this_year: int = 0


class CasesByStatusRow(BaseRecordData):
    status_code: str
    status_description: str
    color_code: Optional[str] = None
    count: int = 0


class CasesByCourtRow(BaseRecordData):
    court_id: int
    court_name: str
    count: int = 0


class CasesByTypeRow(BaseRecordData):
    case_type_code: str
    description: str
    count: int = 0


class CasesByMonthRow(BaseRecordData):
    year: int
    month: int
    month_label: str     # e.g. "Mar 2025"
    count: int = 0


# ─────────────────────────────────────────────────────────────────────────────
# HEARINGS
# ─────────────────────────────────────────────────────────────────────────────

class HearingSummaryReport(BaseRecordData):
    total_hearings: int = 0
    upcoming: int = 0
    completed: int = 0
    adjourned: int = 0
    this_week: int = 0
    this_month: int = 0


class HearingsByMonthRow(BaseRecordData):
    year: int
    month: int
    month_label: str
    total: int = 0
    completed: int = 0
    adjourned: int = 0


# ─────────────────────────────────────────────────────────────────────────────
# BILLING
# ─────────────────────────────────────────────────────────────────────────────

class BillingSummaryReport(BaseRecordData):
    total_billed: float = 0.0
    total_collected: float = 0.0
    total_outstanding: float = 0.0
    total_overdue: float = 0.0
    bill_count: int = 0
    paid_bill_count: int = 0
    pending_bill_count: int = 0
    overdue_bill_count: int = 0
    collection_rate: float = 0.0         # percentage 0-100


class BillingByMonthRow(BaseRecordData):
    year: int
    month: int
    month_label: str
    billed: float = 0.0
    collected: float = 0.0


class TopClientBillingRow(BaseRecordData):
    client_id: str
    client_name: str
    total_billed: float = 0.0
    total_paid: float = 0.0
    outstanding: float = 0.0


# ─────────────────────────────────────────────────────────────────────────────
# FULL DASHBOARD — single payload for the Reports screen
# ─────────────────────────────────────────────────────────────────────────────

class ReportsDashboardOut(BaseRecordData):
    # Cases
    case_summary: CaseSummaryReport
    cases_by_status: List[CasesByStatusRow] = []
    cases_by_court: List[CasesByCourtRow] = []
    cases_by_type: List[CasesByTypeRow] = []
    cases_by_month: List[CasesByMonthRow] = []     # last 12 months

    # Hearings
    hearing_summary: HearingSummaryReport
    hearings_by_month: List[HearingsByMonthRow] = []

    # Billing
    billing_summary: BillingSummaryReport
    billing_by_month: List[BillingByMonthRow] = []
    top_clients: List[TopClientBillingRow] = []
