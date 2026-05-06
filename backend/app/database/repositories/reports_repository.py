# app/database/repositories/reports_repository.py

from datetime import date
from sqlalchemy import select, func, case, and_

from app.database.models.cases import Cases
from app.database.models.courts import Courts
from app.database.models.login_audit import LoginAudit
from app.database.models.refm_case_status import RefmCaseStatus, RefmCaseStatusConstants
from app.database.models.refm_case_types import RefmCaseTypes
from app.database.models.refm_login_status import RefmLoginStatusConstants
from app.database.models.refm_subscription_status import RefmSubscriptionStatusConstants
from app.database.repositories.base.base_repository import BaseRepository
from app.database.repositories.base.repo_context import apply_repo_context

from app.database.models.chamber import Chamber
from app.database.models.billing_invoices import BillingInvoices
from app.database.models.chamber_subscriptions import ChamberSubscriptions

from app.database.models.refm_plan_types import RefmPlanTypes
from app.database.models.refm_invoice_status import RefmInvoiceStatus


@apply_repo_context
class ReportsRepository(BaseRepository[Chamber]):
    
    def __init__(self):
        super().__init__(Chamber)

    # ---------------------------------------------------
    # KPI STATS
    # ---------------------------------------------------

    async def get_chamber_growth_stats(
        self,
        session,
        month_start: date,
        prev_month_start: date,
    ):

        current_month_case = case(
            (
                Chamber.created_date >= month_start,
                1
            ),
            else_=None
        )

        prev_month_case = case(
            (
                and_(
                    Chamber.created_date >= prev_month_start,
                    Chamber.created_date < month_start,
                ),
                1
            ),
            else_=None
        )

        stmt = select(

            # total
            func.count(Chamber.chamber_id).label("total_chambers"),

            # active
            func.count(
                case(
                    (
                        Chamber.status_ind.is_(True),
                        1
                    ),
                    else_=None
                )
            ).label("active_chambers"),

            # new month
            func.count(current_month_case).label("new_this_month"),

            # prev month
            func.count(prev_month_case).label("prev_month"),

        ).where(
            Chamber.deleted_ind.is_(False)
        )

        result = await self.execute(session=session, stmt=stmt)

        return result.first()

    # ---------------------------------------------------
    # TREND
    # ---------------------------------------------------

    async def get_chamber_growth_trend(
        self,
        session,
    ):

        stmt = (
            select(
                func.date_format(
                    Chamber.created_date,
                    "%Y-%m"
                ).label("label"),

                func.count(
                    Chamber.chamber_id
                ).label("chamber_count")
            )
            .where(
                Chamber.deleted_ind.is_(False)
            )
            .group_by("label")
            .order_by("label")
        )

        result = await self.execute(session=session, stmt=stmt)

        return result.all()

    # ---------------------------------------------------
    # PLAN DISTRIBUTION
    # ---------------------------------------------------

    async def get_plan_distribution(
        self,
        session,
    ):

        stmt = (
            select(
                ChamberSubscriptions.plan_code,

                RefmPlanTypes.description.label("plan_name"),

                func.count(
                    ChamberSubscriptions.subscription_id
                ).label("chamber_count")
            )
            .join(
                RefmPlanTypes,
                RefmPlanTypes.code == ChamberSubscriptions.plan_code
            )
            .where(
                ChamberSubscriptions.status_code == RefmSubscriptionStatusConstants.ACTIVE
            )
            .group_by(
                ChamberSubscriptions.plan_code,
                RefmPlanTypes.description,
            )
        )

        result = await self.execute(session=session, stmt=stmt)

        return result.all()

    # ---------------------------------------------------
    # REVENUE SPLIT
    # ---------------------------------------------------

    async def get_revenue_split(
        self,
        session,
    ):

        stmt = (
            select(
                BillingInvoices.status_code,

                RefmInvoiceStatus.description.label("status_name"),

                func.sum(
                    BillingInvoices.amount
                ).label("amount")
            )
            .join(
                RefmInvoiceStatus,
                RefmInvoiceStatus.code == BillingInvoices.status_code
            )
            .group_by(
                BillingInvoices.status_code,
                RefmInvoiceStatus.description,
            )
        )

        result = await self.execute(session=session, stmt=stmt)

        return result.all()
    
    async def get_login_analytics_stats(
        self,
        session,
    ):

        stmt = select(

            func.count(
                LoginAudit.login_id
            ).label("total_logins"),

            func.count(
                case(
                    (
                        LoginAudit.status_code == RefmLoginStatusConstants.SUCCESS,
                        1
                    ),
                    else_=None
                )
            ).label("successful_logins"),

            func.count(
                case(
                    (
                        LoginAudit.status_code == RefmLoginStatusConstants.FAILED,
                        1
                    ),
                    else_=None
                )
            ).label("failed_logins"),

            func.count(
                func.distinct(
                    LoginAudit.actor_user_id
                )
            ).label("active_users"),

        )

        result = await self.execute(
            session=session,
            stmt=stmt
        )

        return result.first()
    
    async def get_login_heatmap(
        self,
        session,
    ):

        stmt = (
            select(

                func.weekday(
                    LoginAudit.login_time
                ).label("weekday"),

                func.dayname(
                    LoginAudit.login_time
                ).label("weekday_name"),

                func.hour(
                    LoginAudit.login_time
                ).label("hour_of_day"),

                func.count(
                    LoginAudit.login_id
                ).label("login_count")

            )
            .group_by(
                func.weekday(LoginAudit.login_time),
                func.dayname(LoginAudit.login_time),
                func.hour(LoginAudit.login_time),
            )
            .order_by(
                func.weekday(LoginAudit.login_time),
                func.hour(LoginAudit.login_time),
            )
        )

        result = await self.execute(
            session=session,
            stmt=stmt
        )

        return result.mappings().all()
    
    async def get_login_trend(
        self,
        session,
    ):

        stmt = (
            select(

                func.date_format(
                    LoginAudit.login_time,
                    "%Y-%m-%d"
                ).label("label"),

                func.count(
                    LoginAudit.login_id
                ).label("login_count")

            )
            .group_by("label")
            .order_by("label")
        )

        result = await self.execute(
            session=session,
            stmt=stmt
        )

        return result.mappings().all()
    
    async def get_login_failure_reasons(
        self,
        session,
    ):

        stmt = (
            select(

                LoginAudit.failure_reason,

                func.count(
                    LoginAudit.login_id
                ).label("count")

            )
            .where(
                LoginAudit.failure_reason.is_not(None)
            )
            .group_by(
                LoginAudit.failure_reason
            )
            .order_by(
                func.count(LoginAudit.login_id).desc()
            )
            .limit(10)
        )

        result = await self.execute(
            session=session,
            stmt=stmt
        )

        return result.mappings().all()
    
    async def get_case_filing_stats(
        self,
        session,
        month_start,
        prev_month_start,
    ):

        current_month_case = case(
            (
                Cases.created_date >= month_start,
                1
            ),
            else_=None
        )

        prev_month_case = case(
            (
                and_(
                    Cases.created_date >= prev_month_start,
                    Cases.created_date < month_start,
                ),
                1
            ),
            else_=None
        )

        stmt = select(

            func.count(
                Cases.case_id
            ).label("total_cases"),

            func.count(
                current_month_case
            ).label("new_cases_this_month"),

            func.count(
                case(
                    (
                        Cases.status_code == RefmCaseStatusConstants.ACTIVE,
                        1
                    ),
                    else_=None
                )
            ).label("active_cases"),

            func.count(
                case(
                    (
                        Cases.status_code == RefmCaseStatusConstants.DISPOSED,
                        1
                    ),
                    else_=None
                )
            ).label("disposed_cases"),

            func.count(
                prev_month_case
            ).label("prev_month")

        ).where(
            Cases.deleted_ind.is_(False)
        )

        result = await self.execute(
            session=session,
            stmt=stmt
        )

        return result.mappings().first()
    
    async def get_case_filing_trend(
        self,
        session,
    ):

        stmt = (
            select(

                func.date_format(
                    Cases.created_date,
                    "%Y-%m"
                ).label("label"),

                func.count(
                    Cases.case_id
                ).label("case_count")

            )
            .where(
                Cases.deleted_ind.is_(False)
            )
            .group_by("label")
            .order_by("label")
        )

        result = await self.execute(
            session=session,
            stmt=stmt
        )

        return result.mappings().all()
    
    async def get_case_type_distribution(
        self,
        session,
    ):

        stmt = (
            select(

                Cases.case_type_code,

                RefmCaseTypes.description.label(
                    "case_type_description"
                ),

                func.count(
                    Cases.case_id
                ).label("case_count")

            )
            .outerjoin(
                RefmCaseTypes,
                RefmCaseTypes.code == Cases.case_type_code
            )
            .where(
                Cases.deleted_ind.is_(False)
            )
            .group_by(
                Cases.case_type_code,
                RefmCaseTypes.description,
            )
        )

        result = await self.execute(
            session=session,
            stmt=stmt
        )

        return result.mappings().all()
    
    async def get_case_status_distribution(
        self,
        session,
    ):

        stmt = (
            select(

                Cases.status_code,

                RefmCaseStatus.description.label(
                    "status_description"
                ),

                RefmCaseStatus.color_code,

                func.count(
                    Cases.case_id
                ).label("case_count")

            )
            .join(
                RefmCaseStatus,
                RefmCaseStatus.code ==
                Cases.status_code
            )
            .where(
                Cases.deleted_ind.is_(False)
            )
            .group_by(
                Cases.status_code,
                RefmCaseStatus.description,
                RefmCaseStatus.color_code,
            )
        )

        result = await self.execute(
            session=session,
            stmt=stmt
        )

        return result.mappings().all()
    
    async def get_top_filing_chambers(
        self,
        session,
    ):

        stmt = (
            select(

                Chamber.chamber_id,

                Chamber.chamber_name,

                func.count(
                    Cases.case_id
                ).label("case_count")

            )
            .join(
                Chamber,
                Chamber.chamber_id ==
                Cases.chamber_id
            )
            .where(
                Cases.deleted_ind.is_(False)
            )
            .group_by(
                Chamber.chamber_id,
                Chamber.chamber_name,
            )
            .order_by(
                func.count(
                    Cases.case_id
                ).desc()
            )
            .limit(10)
        )

        result = await self.execute(
            session=session,
            stmt=stmt
        )

        return result.mappings().all()
    
    async def get_case_court_distribution(
        self,
        session,
    ):

        stmt = (
            select(

                Courts.court_code,

                Courts.court_name,

                func.count(
                    Cases.case_id
                ).label("case_count")

            )
            .join(
                Courts,
                Courts.court_code ==
                Cases.court_code
            )
            .where(
                Cases.deleted_ind.is_(False)
            )
            .group_by(
                Courts.court_code,
                Courts.court_name,
            )
            .order_by(
                func.count(
                    Cases.case_id
                ).desc()
            )
            .limit(10)
        )

        result = await self.execute(
            session=session,
            stmt=stmt
        )

        return result.mappings().all()