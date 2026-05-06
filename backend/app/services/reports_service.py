# app/services/reports_service.py

from datetime import date, timedelta
from typing import Optional
from dateutil.relativedelta import relativedelta

from sqlalchemy.ext.asyncio import AsyncSession

from app.database.models.refm_billing_status import RefmBillingStatusConstants
from app.database.repositories.reports_repository import ReportsRepository
from app.services.base.base_service import BaseService

from app.dtos.reports_dto import (
    CaseFilingTrendItem,
    CaseFilingTrendReportOut,
    CaseFilingTrendStats,
    CaseStatusAnalyticsItem,
    CaseTypeAnalyticsItem,
    ChamberGrowthReportOut,
    ChamberGrowthStats,
    ChamberGrowthTrendItem,
    ChamberPlanDistributionItem,
    ChamberRevenueStatusItem,
    CourtFilingAnalyticsItem,
    LoginAnalyticsReportOut,
    LoginAnalyticsStats,
    LoginFailureReasonItem,
    LoginHeatmapItem,
    LoginTrendItem,
    TopFilingChamberItem,
)


class ReportsService(BaseService):

    def __init__(
        self,
        session: AsyncSession,
        reports_repo: Optional[ReportsRepository] = None,
    ):
        super().__init__(session)
        self.reports_repo = reports_repo or ReportsRepository()

    async def get_chamber_growth_report(self) -> ChamberGrowthReportOut:

        today = date.today()

        month_start = today.replace(day=1)

        prev_month_start = (
            month_start - relativedelta(months=1)
        )

        # ---------------------------------------------------
        # LOAD
        # ---------------------------------------------------

        stats_row = await self.reports_repo.get_chamber_growth_stats(
            session=self.session,
            month_start=month_start,
            prev_month_start=prev_month_start,
        )

        trend_rows = await self.reports_repo.get_chamber_growth_trend(
            session=self.session,
        )

        plan_rows = await self.reports_repo.get_plan_distribution(
            session=self.session,
        )

        revenue_rows = await self.reports_repo.get_revenue_split(
            session=self.session,
        )

        # ---------------------------------------------------
        # GROWTH %
        # ---------------------------------------------------

        prev_month = stats_row.prev_month if stats_row and stats_row.prev_month else 0

        new_this_month = stats_row.new_this_month if stats_row and stats_row.new_this_month else 0

        growth_percentage = 0

        if prev_month > 0:
            growth_percentage = round(
                (
                    (new_this_month - prev_month)
                    / prev_month
                ) * 100,
                2
            )

        # ---------------------------------------------------
        # REVENUE
        # ---------------------------------------------------

        total_revenue = 0
        pending_revenue = 0
        cancelled_revenue = 0

        revenue_items = []

        for r in revenue_rows:

            amt = float(r.amount or 0)

            revenue_items.append(
                ChamberRevenueStatusItem(
                    status_code=r.status_code,
                    status_name=r.status_name,
                    amount=amt,
                )
            )

            total_revenue += amt

            if r.status_code == RefmBillingStatusConstants.PENDING:
                pending_revenue += amt

            elif r.status_code == RefmBillingStatusConstants.CANCELLED:
                cancelled_revenue += amt

        # ---------------------------------------------------
        # OUT
        # ---------------------------------------------------

        return ChamberGrowthReportOut(

            stats=ChamberGrowthStats(
                total_chambers=stats_row.total_chambers if stats_row and stats_row.total_chambers else 0,

                active_chambers=stats_row.active_chambers if stats_row and stats_row.active_chambers else 0,

                new_this_month=new_this_month,

                growth_percentage=growth_percentage,

                total_revenue=total_revenue,

                monthly_revenue=0,

                pending_revenue=pending_revenue,

                cancelled_revenue=cancelled_revenue,
            ),

            trend=[
                ChamberGrowthTrendItem(
                    label=r.label,
                    chamber_count=r.chamber_count
                )
                for r in trend_rows
            ],

            plans=[
                ChamberPlanDistributionItem(
                    plan_code=r.plan_code,
                    plan_name=r.plan_name,
                    chamber_count=r.chamber_count,
                    )
                for r in plan_rows
            ],

            revenue=revenue_items,
        )
    
    async def get_login_analytics_report(self):

        stats_row = await self.reports_repo.get_login_analytics_stats(
            session=self.session,
        )

        heatmap_rows = await self.reports_repo.get_login_heatmap(
            session=self.session,
        )

        trend_rows = await self.reports_repo.get_login_trend(
            session=self.session,
        )

        failure_rows = await self.reports_repo.get_login_failure_reasons(
            session=self.session,
        )

        # ---------------------------------------------------
        # PEAK HOUR
        # ---------------------------------------------------

        peak_hour = 0
        peak_hour_count = 0

        hour_map = {}

        for r in heatmap_rows:

            hr = r.hour_of_day

            hour_map[hr] = (
                hour_map.get(hr, 0)
                + (r.login_count or 0)
            )

        if hour_map:

            peak_hour =  max(
                hour_map.items(),
                key=lambda x: x[1]
            )[0]

            peak_hour_count = hour_map[peak_hour]

        stats=None
        if stats_row:
            stats=LoginAnalyticsStats(

                total_logins=stats_row.total_logins or 0,

                successful_logins=stats_row.successful_logins or 0,

                failed_logins=stats_row.failed_logins or 0,

                active_users=stats_row.active_users or 0,

                peak_hour=peak_hour,

                peak_hour_count=peak_hour_count,
            )

        return LoginAnalyticsReportOut(

            stats=stats,

            heatmap=[
                LoginHeatmapItem(**r)
                for r in heatmap_rows
            ],

            trend=[
                LoginTrendItem(**r)
                for r in trend_rows
            ],

            failure_reasons=[
                LoginFailureReasonItem(**r)
                for r in failure_rows
            ]
        )
    
    async def get_case_filing_trend_report(self):

        today = date.today()

        month_start = today.replace(day=1)

        prev_month_end = (
            month_start - timedelta(days=1)
        )

        prev_month_start = (
            prev_month_end.replace(day=1)
        )

        # ---------------------------------------------------
        # LOAD
        # ---------------------------------------------------

        stats_row = await self.reports_repo.get_case_filing_stats(
            session=self.session,
            month_start=month_start,
            prev_month_start=prev_month_start,
        )

        trend_rows = await self.reports_repo.get_case_filing_trend(
            session=self.session,
        )

        type_rows = await self.reports_repo.get_case_type_distribution(
            session=self.session,
        )

        status_rows = await self.reports_repo.get_case_status_distribution(
            session=self.session,
        )

        chamber_rows = await self.reports_repo.get_top_filing_chambers(
            session=self.session,
        )

        court_rows = await self.reports_repo.get_case_court_distribution(
            session=self.session,
        )

        # ---------------------------------------------------
        # GROWTH %
        # ---------------------------------------------------

        prev_month = stats_row["prev_month"] if stats_row else 0

        current_month = (
             stats_row["new_cases_this_month"] if stats_row else 0
        )

        growth_percentage = 0

        if prev_month > 0:

            growth_percentage = round(
                (
                    (
                        current_month - prev_month
                    ) / prev_month
                ) * 100,
                2
            )

        stats = None

        if stats_row:
            stats=CaseFilingTrendStats(

                total_cases=stats_row["total_cases"] or 0,

                new_cases_this_month=current_month,

                active_cases=stats_row["active_cases"] or 0,

                disposed_cases=stats_row["disposed_cases"] or 0,

                filing_growth_percentage=growth_percentage,
            )

        return CaseFilingTrendReportOut(

            stats=stats,

            trend=[
                CaseFilingTrendItem(**r)
                for r in trend_rows
            ],

            case_types=[
                CaseTypeAnalyticsItem(**r)
                for r in type_rows
            ],

            statuses=[
                CaseStatusAnalyticsItem(**r)
                for r in status_rows
            ],

            top_chambers=[
                TopFilingChamberItem(**r)
                for r in chamber_rows
            ],

            courts=[
                CourtFilingAnalyticsItem(**r)
                for r in court_rows
            ]
        )