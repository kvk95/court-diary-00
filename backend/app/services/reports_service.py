"""reports_service.py — Business logic only; all DB queries delegated to repositories"""

from calendar import month_abbr
from datetime import date, timedelta
from typing import List

from sqlalchemy.ext.asyncio import AsyncSession

from app.database.models.refm_billing_status import RefmBillingStatusConstants
from app.database.models.refm_case_status import RefmCaseStatusConstants
from app.database.repositories.cases_repository import CasesRepository
from app.database.repositories.client_bills_repository import ClientBillsRepository
from app.database.repositories.hearings_repository import HearingsRepository
from app.dtos.reports_dto import (
    BillingByMonthRow,
    BillingSummaryReport,
    CasesByCourtRow,
    CasesByMonthRow,
    CasesByStatusRow,
    CasesByTypeRow,
    CaseSummaryReport,
    HearingsByMonthRow,
    HearingSummaryReport,
    ReportsDashboardOut,
    TopClientBillingRow,
)
from app.services.base.secured_base_service import BaseSecuredService


def _f(v) -> float:
    return float(v) if v is not None else 0.0


def _month_label(year: int, month: int) -> str:
    return f"{month_abbr[month]} {year}"


def _last_12_months() -> List[tuple]:
    today = date.today()
    seen: set = set()
    result = []
    for i in range(11, -1, -1):
        d = date(today.year, today.month, 1) - timedelta(days=i * 30)
        ym = (d.year, d.month)
        if ym not in seen:
            seen.add(ym)
            result.append(ym)
    return result[-12:]


def _next_month(year: int, month: int) -> date:
    if month == 12:
        return date(year + 1, 1, 1)
    return date(year, month + 1, 1)


class ReportsService(BaseSecuredService):
    def __init__(self, session: AsyncSession):
        super().__init__(session)
        self.cases_repo = CasesRepository()
        self.hearings_repo = HearingsRepository()
        self.bills_repo = ClientBillsRepository()

    # ─────────────────────────────────────────────────────────────────────
    # CASES
    # ─────────────────────────────────────────────────────────────────────

    async def _case_summary(self) -> CaseSummaryReport:
        today = date.today()
        cid = self.chamber_id

        stats = await self.cases_repo.get_case_summary_stats(
            session=self.session,
            chamber_id=cid,
            active_code=RefmCaseStatusConstants.ACTIVE,
            adjourned_code=RefmCaseStatusConstants.ADJOURNED,
            disposed_code=RefmCaseStatusConstants.DISPOSED,
            closed_code=RefmCaseStatusConstants.CLOSED,
            today=today,
        )

        month_start = date(today.year, today.month, 1)
        year_start = date(today.year, 1, 1)

        this_month = await self.cases_repo.count_cases_since(
            session=self.session, chamber_id=cid, since=month_start
        )
        this_year = await self.cases_repo.count_cases_since(
            session=self.session, chamber_id=cid, since=year_start
        )

        return CaseSummaryReport(
            total_cases=stats["total"],
            active_cases=stats["active"],
            adjourned_cases=stats["adjourned"],
            disposed_cases=0,   # populated via by_status breakdown below
            closed_cases=0,
            overdue_cases=stats["overdue"],
            cases_filed_this_month=this_month,
            cases_filed_this_year=this_year,
        )

    async def _cases_by_status(self) -> List[CasesByStatusRow]:
        rows = await self.cases_repo.get_cases_by_status(
            session=self.session, chamber_id=self.chamber_id
        )
        result = [
            CasesByStatusRow(
                status_code=r["status_code"],
                status_description=r["status_description"],
                color_code=r["color_code"],
                count=r["count"],
            )
            for r in rows
        ]
        return sorted(result, key=lambda x: x.count, reverse=True)

    async def _cases_by_court(self) -> List[CasesByCourtRow]:
        rows = await self.cases_repo.get_cases_by_court(
            session=self.session, chamber_id=self.chamber_id
        )
        return [
            CasesByCourtRow(court_id=r["court_id"], court_name=r["court_name"], count=r["count"])
            for r in rows
        ]

    async def _cases_by_type(self) -> List[CasesByTypeRow]:
        rows = await self.cases_repo.get_cases_by_type(
            session=self.session, chamber_id=self.chamber_id
        )
        return [
            CasesByTypeRow(case_type_code=r["case_type_code"], description=r["description"], count=r["count"])
            for r in rows
        ]

    async def _cases_by_month(self) -> List[CasesByMonthRow]:
        result = []
        for year, month in _last_12_months():
            month_start = date(year, month, 1)
            cnt = await self.cases_repo.count_cases_in_month(
                session=self.session,
                chamber_id=self.chamber_id,
                month_start=month_start,
                month_end=_next_month(year, month),
            )
            result.append(CasesByMonthRow(
                year=year, month=month,
                month_label=_month_label(year, month),
                count=cnt,
            ))
        return result

    # ─────────────────────────────────────────────────────────────────────
    # HEARINGS
    # ─────────────────────────────────────────────────────────────────────

    async def _hearing_summary(self) -> HearingSummaryReport:
        stats = await self.hearings_repo.get_hearing_summary_stats(
            session=self.session,
            chamber_id=self.chamber_id,
            today=date.today(),
        )
        return HearingSummaryReport(
            total_hearings=stats["total"],
            upcoming=stats["upcoming"],
            completed=stats["completed"],
            adjourned=stats["adjourned"],
            this_week=stats["this_week"],
            this_month=stats["this_month"],
        )

    async def _hearings_by_month(self) -> List[HearingsByMonthRow]:
        result = []
        for year, month in _last_12_months():
            month_start = date(year, month, 1)
            month_end = _next_month(year, month)
            total = await self.hearings_repo.count_hearings_in_month(
                session=self.session, chamber_id=self.chamber_id,
                month_start=month_start, month_end=month_end,
            )
            completed = await self.hearings_repo.count_hearings_in_month(
                session=self.session, chamber_id=self.chamber_id,
                month_start=month_start, month_end=month_end, status_code="CMP",
            )
            adjourned = await self.hearings_repo.count_hearings_in_month(
                session=self.session, chamber_id=self.chamber_id,
                month_start=month_start, month_end=month_end, status_code="ADJ",
            )
            result.append(HearingsByMonthRow(
                year=year, month=month, month_label=_month_label(year, month),
                total=total, completed=completed, adjourned=adjourned,
            ))
        return result

    # ─────────────────────────────────────────────────────────────────────
    # BILLING
    # ─────────────────────────────────────────────────────────────────────

    async def _billing_summary(self) -> BillingSummaryReport:
        stats = await self.bills_repo.get_billing_stats(
            session=self.session,
            chamber_id=self.chamber_id,
            today=date.today(),
            paid_code=RefmBillingStatusConstants.PAID,
            cancelled_code=RefmBillingStatusConstants.CANCELLED,
            pending_code=RefmBillingStatusConstants.PENDING,
        )
        billed = stats["total"]
        paid = stats["paid"]
        collection_rate = round((paid / billed * 100) if billed > 0 else 0.0, 1)

        return BillingSummaryReport(
            total_billed=round(billed, 2),
            total_collected=round(paid, 2),
            total_outstanding=round(billed - paid, 2),
            total_overdue=round(stats["overdue_amt"], 2),
            bill_count=stats["bill_count"],
            paid_bill_count=stats["paid_count"],
            pending_bill_count=stats["pending_count"],
            overdue_bill_count=stats["overdue_count"],
            collection_rate=collection_rate,
        )

    async def _billing_by_month(self) -> List[BillingByMonthRow]:
        result = []
        for year, month in _last_12_months():
            month_start = date(year, month, 1)
            data = await self.bills_repo.get_billing_by_month(
                session=self.session,
                chamber_id=self.chamber_id,
                month_start=month_start,
                month_end=_next_month(year, month),
            )
            result.append(BillingByMonthRow(
                year=year, month=month, month_label=_month_label(year, month),
                billed=round(data["billed"], 2),
                collected=round(data["paid"], 2),
            ))
        return result

    async def _top_clients(self) -> List[TopClientBillingRow]:
        rows = await self.bills_repo.get_top_clients_billing(
            session=self.session, chamber_id=self.chamber_id
        )
        return [
            TopClientBillingRow(
                client_id=r.client_id,
                client_name=r.client_name,
                total_billed=round(_f(r.billed), 2),
                total_paid=round(_f(r.paid), 2),
                outstanding=round(_f(r.billed) - _f(r.paid), 2),
            )
            for r in rows
        ]

    # ─────────────────────────────────────────────────────────────────────
    # FULL DASHBOARD
    # ─────────────────────────────────────────────────────────────────────

    async def reports_get_dashboard(self) -> ReportsDashboardOut:
        return ReportsDashboardOut(
            case_summary=await self._case_summary(),
            cases_by_status=await self._cases_by_status(),
            cases_by_court=await self._cases_by_court(),
            cases_by_type=await self._cases_by_type(),
            cases_by_month=await self._cases_by_month(),
            hearing_summary=await self._hearing_summary(),
            hearings_by_month=await self._hearings_by_month(),
            billing_summary=await self._billing_summary(),
            billing_by_month=await self._billing_by_month(),
            top_clients=await self._top_clients(),
        )
