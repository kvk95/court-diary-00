"""reports_service.py — Business logic for Reports module"""

from calendar import month_abbr
from datetime import date, timedelta
from typing import List, Optional

from sqlalchemy import and_, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.models.case_clients import CaseClients
from app.database.models.cases import Cases
from app.database.models.client_bills import ClientBills
from app.database.models.client_payments import ClientPayments
from app.database.models.clients import Clients
from app.database.models.hearings import Hearings
from app.database.models.refm_billing_status import RefmBillingStatusConstants
from app.database.models.refm_case_status import RefmCaseStatus, RefmCaseStatusConstants
from app.database.models.refm_case_types import RefmCaseTypes
from app.database.models.refm_courts import RefmCourts
from app.database.models.refm_hearing_status import RefmHearingStatusConstants
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
    """Returns list of (year, month) for last 12 months, oldest first."""
    today = date.today()
    months = []
    for i in range(11, -1, -1):
        d = date(today.year, today.month, 1) - timedelta(days=i * 30)
        months.append((d.year, d.month))
    # Deduplicate while preserving order
    seen = set()
    result = []
    for ym in months:
        if ym not in seen:
            seen.add(ym)
            result.append(ym)
    return result[-12:]


class ReportsService(BaseSecuredService):
    def __init__(self, session: AsyncSession):
        super().__init__(session)

    # ─────────────────────────────────────────────────────────────────────
    # CASES
    # ─────────────────────────────────────────────────────────────────────

    async def _case_summary(self) -> CaseSummaryReport:
        today = date.today()
        cid = self.chamber_id

        def base():
            return select(func.count(Cases.case_id)).where(
                Cases.chamber_id == cid, Cases.is_deleted.is_(False)
            )

        total = await self.session.scalar(base()) or 0
        active = await self.session.scalar(base().where(Cases.status_code == RefmCaseStatusConstants.ACTIVE)) or 0
        adjourned = await self.session.scalar(base().where(Cases.status_code == RefmCaseStatusConstants.ADJOURNED)) or 0
        disposed = await self.session.scalar(base().where(Cases.status_code == RefmCaseStatusConstants.DISPOSED)) or 0
        closed = await self.session.scalar(base().where(Cases.status_code == RefmCaseStatusConstants.CLOSED)) or 0
        overdue = await self.session.scalar(
            base().where(
                Cases.status_code == RefmCaseStatusConstants.ACTIVE,
                Cases.next_hearing_date < today,
            )
        ) or 0

        # Filed this month and this year
        month_start = date(today.year, today.month, 1)
        year_start = date(today.year, 1, 1)
        this_month = await self.session.scalar(
            base().where(Cases.created_date >= month_start)
        ) or 0
        this_year = await self.session.scalar(
            base().where(Cases.created_date >= year_start)
        ) or 0

        return CaseSummaryReport(
            total_cases=total, active_cases=active, adjourned_cases=adjourned,
            disposed_cases=disposed, closed_cases=closed, overdue_cases=overdue,
            cases_filed_this_month=this_month, cases_filed_this_year=this_year,
        )

    async def _cases_by_status(self) -> List[CasesByStatusRow]:
        rows = await self.session.execute(
            select(
                Cases.status_code,
                func.count(Cases.case_id).label("cnt"),
            )
            .where(Cases.chamber_id == self.chamber_id, Cases.is_deleted.is_(False))
            .group_by(Cases.status_code)
        )
        status_data = {r.status_code: r.cnt for r in rows}

        # Enrich descriptions + colors from refm
        refm_rows = await self.session.execute(
            select(RefmCaseStatus.code, RefmCaseStatus.description, RefmCaseStatus.color_code)
            .where(RefmCaseStatus.code.in_(list(status_data.keys())))
        )
        result = []
        for r in refm_rows:
            result.append(CasesByStatusRow(
                status_code=r.code,
                status_description=r.description,
                color_code=r.color_code,
                count=status_data.get(r.code, 0),
            ))
        return sorted(result, key=lambda x: x.count, reverse=True)

    async def _cases_by_court(self) -> List[CasesByCourtRow]:
        rows = await self.session.execute(
            select(
                Cases.court_id,
                RefmCourts.court_name,
                func.count(Cases.case_id).label("cnt"),
            )
            .join(RefmCourts, Cases.court_id == RefmCourts.court_id)
            .where(Cases.chamber_id == self.chamber_id, Cases.is_deleted.is_(False))
            .group_by(Cases.court_id, RefmCourts.court_name)
            .order_by(func.count(Cases.case_id).desc())
            .limit(10)
        )
        return [
            CasesByCourtRow(court_id=r.court_id, court_name=r.court_name, count=r.cnt)
            for r in rows
        ]

    async def _cases_by_type(self) -> List[CasesByTypeRow]:
        rows = await self.session.execute(
            select(
                Cases.case_type_code,
                RefmCaseTypes.description,
                func.count(Cases.case_id).label("cnt"),
            )
            .join(RefmCaseTypes, Cases.case_type_code == RefmCaseTypes.code)
            .where(
                Cases.chamber_id == self.chamber_id,
                Cases.is_deleted.is_(False),
                Cases.case_type_code.isnot(None),
            )
            .group_by(Cases.case_type_code, RefmCaseTypes.description)
            .order_by(func.count(Cases.case_id).desc())
        )
        return [
            CasesByTypeRow(case_type_code=r.case_type_code, description=r.description, count=r.cnt)
            for r in rows
        ]

    async def _cases_by_month(self) -> List[CasesByMonthRow]:
        months = _last_12_months()
        result = []
        for year, month in months:
            month_start = date(year, month, 1)
            next_month = date(year + (month // 12), (month % 12) + 1, 1)
            cnt = await self.session.scalar(
                select(func.count(Cases.case_id)).where(
                    Cases.chamber_id == self.chamber_id,
                    Cases.is_deleted.is_(False),
                    Cases.created_date >= month_start,
                    Cases.created_date < next_month,
                )
            ) or 0
            result.append(CasesByMonthRow(year=year, month=month, month_label=_month_label(year, month), count=cnt))
        return result

    # ─────────────────────────────────────────────────────────────────────
    # HEARINGS
    # ─────────────────────────────────────────────────────────────────────

    async def _hearing_summary(self) -> HearingSummaryReport:
        today = date.today()
        cid = self.chamber_id
        week_end = today + timedelta(days=7)
        month_end = today + timedelta(days=30)

        def base():
            return select(func.count(Hearings.hearing_id)).where(
                Hearings.chamber_id == cid,
                Hearings.is_deleted.is_(False),
            )

        total = await self.session.scalar(base()) or 0
        upcoming = await self.session.scalar(
            base().where(Hearings.status_code.in_(["UP", "SC"]))
        ) or 0
        completed = await self.session.scalar(
            base().where(Hearings.status_code == "CMP")
        ) or 0
        adjourned = await self.session.scalar(
            base().where(Hearings.status_code == "ADJ")
        ) or 0
        this_week = await self.session.scalar(
            base().where(
                Hearings.status_code.in_(["UP", "SC"]),
                Hearings.hearing_date >= today,
                Hearings.hearing_date <= week_end,
            )
        ) or 0
        this_month = await self.session.scalar(
            base().where(
                Hearings.status_code.in_(["UP", "SC"]),
                Hearings.hearing_date >= today,
                Hearings.hearing_date <= month_end,
            )
        ) or 0

        return HearingSummaryReport(
            total_hearings=total, upcoming=upcoming, completed=completed,
            adjourned=adjourned, this_week=this_week, this_month=this_month,
        )

    async def _hearings_by_month(self) -> List[HearingsByMonthRow]:
        months = _last_12_months()
        result = []
        for year, month in months:
            month_start = date(year, month, 1)
            next_month = date(year + (month // 12), (month % 12) + 1, 1)

            base_where = [
                Hearings.chamber_id == self.chamber_id,
                Hearings.is_deleted.is_(False),
                Hearings.hearing_date >= month_start,
                Hearings.hearing_date < next_month,
            ]
            total = await self.session.scalar(
                select(func.count(Hearings.hearing_id)).where(*base_where)
            ) or 0
            completed = await self.session.scalar(
                select(func.count(Hearings.hearing_id)).where(*base_where, Hearings.status_code == "CMP")
            ) or 0
            adjourned = await self.session.scalar(
                select(func.count(Hearings.hearing_id)).where(*base_where, Hearings.status_code == "ADJ")
            ) or 0
            result.append(HearingsByMonthRow(
                year=year, month=month, month_label=_month_label(year, month),
                total=total, completed=completed, adjourned=adjourned,
            ))
        return result

    # ─────────────────────────────────────────────────────────────────────
    # BILLING
    # ─────────────────────────────────────────────────────────────────────

    async def _billing_summary(self) -> BillingSummaryReport:
        today = date.today()
        cid = self.chamber_id

        row = (await self.session.execute(
            select(
                func.count(ClientBills.bill_id).label("cnt"),
                func.coalesce(func.sum(ClientBills.total_amount), 0).label("billed"),
                func.coalesce(func.sum(ClientBills.paid_amount), 0).label("paid"),
            ).where(ClientBills.chamber_id == cid)
        )).first()

        billed = _f(row.billed)
        paid = _f(row.paid)
        bill_count = row.cnt or 0

        paid_count = await self.session.scalar(
            select(func.count(ClientBills.bill_id)).where(
                ClientBills.chamber_id == cid,
                ClientBills.status_code == RefmBillingStatusConstants.PAID,
            )
        ) or 0

        pending_count = await self.session.scalar(
            select(func.count(ClientBills.bill_id)).where(
                ClientBills.chamber_id == cid,
                ClientBills.status_code == RefmBillingStatusConstants.PENDING,
            )
        ) or 0

        overdue_row = (await self.session.execute(
            select(
                func.count(ClientBills.bill_id).label("cnt"),
                func.coalesce(
                    func.sum(ClientBills.total_amount - ClientBills.paid_amount), 0
                ).label("amt"),
            ).where(
                ClientBills.chamber_id == cid,
                ClientBills.status_code.notin_([
                    RefmBillingStatusConstants.PAID,
                    RefmBillingStatusConstants.CANCELLED,
                ]),
                ClientBills.due_date < today,
            )
        )).first()

        collection_rate = round((paid / billed * 100) if billed > 0 else 0.0, 1)

        return BillingSummaryReport(
            total_billed=round(billed, 2),
            total_collected=round(paid, 2),
            total_outstanding=round(billed - paid, 2),
            total_overdue=round(_f(overdue_row.amt), 2),
            bill_count=bill_count,
            paid_bill_count=paid_count,
            pending_bill_count=pending_count,
            overdue_bill_count=overdue_row.cnt or 0,
            collection_rate=collection_rate,
        )

    async def _billing_by_month(self) -> List[BillingByMonthRow]:
        months = _last_12_months()
        result = []
        for year, month in months:
            month_start = date(year, month, 1)
            next_month = date(year + (month // 12), (month % 12) + 1, 1)
            base_where = [
                ClientBills.chamber_id == self.chamber_id,
                ClientBills.bill_date >= month_start,
                ClientBills.bill_date < next_month,
            ]
            row = (await self.session.execute(
                select(
                    func.coalesce(func.sum(ClientBills.total_amount), 0).label("billed"),
                    func.coalesce(func.sum(ClientBills.paid_amount), 0).label("paid"),
                ).where(*base_where)
            )).first()
            result.append(BillingByMonthRow(
                year=year, month=month, month_label=_month_label(year, month),
                billed=round(_f(row.billed), 2),
                collected=round(_f(row.paid), 2),
            ))
        return result

    async def _top_clients(self, limit: int = 10) -> List[TopClientBillingRow]:
        rows = await self.session.execute(
            select(
                ClientBills.client_id,
                Clients.client_name,
                func.coalesce(func.sum(ClientBills.total_amount), 0).label("billed"),
                func.coalesce(func.sum(ClientBills.paid_amount), 0).label("paid"),
            )
            .join(Clients, ClientBills.client_id == Clients.client_id)
            .where(ClientBills.chamber_id == self.chamber_id)
            .group_by(ClientBills.client_id, Clients.client_name)
            .order_by(func.sum(ClientBills.total_amount).desc())
            .limit(limit)
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
        """Single call that assembles all report sections."""
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
