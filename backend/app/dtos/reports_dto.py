# app/dtos/reports_dto.py

from datetime import date
from typing import Optional

from app.dtos.base.base_data import BaseInData, BaseRecordData


# ─────────────────────────────────────────────
# FILTER
# ─────────────────────────────────────────────

class ChamberGrowthFilter(BaseInData):

    date_from: Optional[date] = None
    date_to: Optional[date] = None

    group_by: Optional[str] = "month"


# ─────────────────────────────────────────────
# KPI
# ─────────────────────────────────────────────

class ChamberGrowthStats(BaseRecordData):

    total_chambers: int = 0
    active_chambers: int = 0

    new_this_month: int = 0

    growth_percentage: float = 0

    total_revenue: float = 0
    monthly_revenue: float = 0

    pending_revenue: float = 0
    cancelled_revenue: float = 0


# ─────────────────────────────────────────────
# TREND
# ─────────────────────────────────────────────

class ChamberGrowthTrendItem(BaseRecordData):

    label: str
    chamber_count: int


# ─────────────────────────────────────────────
# PLAN DISTRIBUTION
# ─────────────────────────────────────────────

class ChamberPlanDistributionItem(BaseRecordData):

    plan_code: str
    plan_name: str

    chamber_count: int


# ─────────────────────────────────────────────
# REVENUE SPLIT
# ─────────────────────────────────────────────

class ChamberRevenueStatusItem(BaseRecordData):

    status_code: str
    status_name: str

    amount: float


# ─────────────────────────────────────────────
# FINAL OUT
# ─────────────────────────────────────────────

class ChamberGrowthReportOut(BaseRecordData):

    stats: ChamberGrowthStats

    trend: list[ChamberGrowthTrendItem]

    plans: list[ChamberPlanDistributionItem]

    revenue: list[ChamberRevenueStatusItem]


# ─────────────────────────────────────────────
# LOGIN ANALYTICS
# ─────────────────────────────────────────────

class LoginHeatmapItem(BaseRecordData):

    weekday: int
    weekday_name: str

    hour_of_day: int

    login_count: int


class LoginAnalyticsStats(BaseRecordData):

    total_logins: int = 0

    successful_logins: int = 0
    failed_logins: int = 0

    active_users: int = 0

    peak_hour: int = 0
    peak_hour_count: int = 0


class LoginFailureReasonItem(BaseRecordData):

    failure_reason: str

    count: int


class LoginTrendItem(BaseRecordData):

    label: str

    login_count: int


class LoginAnalyticsReportOut(BaseRecordData):

    stats: LoginAnalyticsStats | None

    heatmap: list[LoginHeatmapItem]

    trend: list[LoginTrendItem]

    failure_reasons: list[LoginFailureReasonItem]

# ─────────────────────────────────────────────
# CASE FILING TRENDS
# ─────────────────────────────────────────────

class CaseFilingTrendStats(BaseRecordData):

    total_cases: int = 0

    new_cases_this_month: int = 0

    active_cases: int = 0
    disposed_cases: int = 0

    filing_growth_percentage: float = 0


class CaseFilingTrendItem(BaseRecordData):

    label: str

    case_count: int


class CaseTypeAnalyticsItem(BaseRecordData):

    case_type_code: Optional[str]

    case_type_description: Optional[str]

    case_count: int


class CaseStatusAnalyticsItem(BaseRecordData):

    status_code: str

    status_description: str

    color_code: Optional[str]

    case_count: int


class TopFilingChamberItem(BaseRecordData):

    chamber_id: str

    chamber_name: str

    case_count: int


class CourtFilingAnalyticsItem(BaseRecordData):

    court_code: str

    court_name: str

    case_count: int


class CaseFilingTrendReportOut(BaseRecordData):

    stats: CaseFilingTrendStats | None

    trend: list[CaseFilingTrendItem]

    case_types: list[CaseTypeAnalyticsItem]

    statuses: list[CaseStatusAnalyticsItem]

    top_chambers: list[TopFilingChamberItem]

    courts: list[CourtFilingAnalyticsItem]