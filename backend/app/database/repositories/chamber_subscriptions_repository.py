

from typing import Optional

from sqlalchemy import func, select

from app.database.models.cases import Cases
from app.database.models.refm_plan_types import RefmPlanTypes
from app.database.models.refm_subscription_status import RefmSubscriptionStatusConstants
from app.database.models.user_chamber_link import UserChamberLink
from app.database.repositories.base.repo_context import apply_repo_context
from app.database.repositories.base.base_repository import BaseRepository
from app.database.models.chamber_subscriptions import ChamberSubscriptions

@apply_repo_context
class ChamberSubscriptionsRepository(BaseRepository[ChamberSubscriptions]):
    def __init__(self):
        super().__init__(ChamberSubscriptions)

    async def get_subscription_stats(self, session, chamber_id: str):

        stmt = (
            select(
                ChamberSubscriptions.plan_code,
                RefmPlanTypes.description.label("plan_name"),

                RefmPlanTypes.max_users,
                RefmPlanTypes.max_cases,

                ChamberSubscriptions.next_renewal_date,
                ChamberSubscriptions.price_amt,

                # ✅ counts
                func.count(func.distinct(UserChamberLink.link_id)).label("users_used"),
                func.count(func.distinct(Cases.case_id)).label("cases_used"),
            )
            .join(
                RefmPlanTypes,
                RefmPlanTypes.code == ChamberSubscriptions.plan_code
            )
            .outerjoin(
                UserChamberLink,
                UserChamberLink.chamber_id == ChamberSubscriptions.chamber_id
            )
            .outerjoin(
                Cases,
                Cases.chamber_id == ChamberSubscriptions.chamber_id
            )
            .where(
                ChamberSubscriptions.chamber_id == chamber_id,
                ChamberSubscriptions.status_code == RefmSubscriptionStatusConstants.ACTIVE,
            )
            .group_by(
                ChamberSubscriptions.subscription_id,
                RefmPlanTypes.max_users,
                RefmPlanTypes.max_cases,
            )
        )

        result = await self.execute(session=session,stmt=stmt)
        return result.first()

    async def get_active_subscription(self, session, chamber_id: str) -> Optional[ChamberSubscriptions]:
        stmt = (
            select(
                ChamberSubscriptions
            )
            .join(RefmPlanTypes, RefmPlanTypes.code == ChamberSubscriptions.plan_code)
            .where(
                ChamberSubscriptions.chamber_id == chamber_id,
                ChamberSubscriptions.status_code == RefmSubscriptionStatusConstants.ACTIVE
            )
        )

        result = await self.execute(session=session,stmt=stmt)
        return result.scalars().first()

    async def list_plans(self, session):
        stmt = select(RefmPlanTypes).where(
            RefmPlanTypes.status_ind.is_(True)
        ).order_by(RefmPlanTypes.sort_order)

        result = await session.execute(stmt)
        return result.scalars().all()
    
    async def get_usage_stats(self, session, chamber_id: str):
        stmt = (
            select(
                func.count(func.distinct(UserChamberLink.link_id)).label("users_used"),
                func.count(func.distinct(Cases.case_id)).label("cases_used"),

                RefmPlanTypes.max_users,
                RefmPlanTypes.max_cases,
            )
            .join(ChamberSubscriptions, ChamberSubscriptions.chamber_id == UserChamberLink.chamber_id)
            .join(RefmPlanTypes, RefmPlanTypes.code == ChamberSubscriptions.plan_code)
            .outerjoin(Cases, Cases.chamber_id == UserChamberLink.chamber_id)
            .where(
                UserChamberLink.chamber_id == chamber_id,
                ChamberSubscriptions.status_code == RefmSubscriptionStatusConstants.ACTIVE,
            )
            .group_by(
                RefmPlanTypes.max_users,
                RefmPlanTypes.max_cases
            )
        )

        result = await self.execute(session=session,stmt=stmt)
        return result.first()
