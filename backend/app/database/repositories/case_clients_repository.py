

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.models.case_clients import CaseClients
from app.database.models.cases import Cases
from app.database.models.hearings import Hearings
from app.database.models.users import Users
from app.database.repositories.base.base_repository import BaseRepository
from app.database.repositories.base.repo_context import apply_repo_context



@apply_repo_context
class CaseClientsRepository(BaseRepository[CaseClients]):
    def __init__(self):
        super().__init__(CaseClients)

    async def list_cases_for_client(
        self,
        session: AsyncSession,
        chamber_id: str,
        client_id: str,
    ):
        # ─────────────────────────────────────────────
        # 1. SUBQUERY: LATEST HEARING
        # ─────────────────────────────────────────────
        latest_hearing = (
            select(
                Hearings.case_id,
                Hearings.status_code,
                func.row_number()
                .over(
                    partition_by=Hearings.case_id,
                    order_by=Hearings.hearing_date.desc(),
                )
                .label("rn"),
            )
            .where(
                Hearings.deleted_ind.is_(False),
                Hearings.chamber_id == chamber_id,
            )
            .subquery()
        )

        latest_hearing = (
            select(
                latest_hearing.c.case_id,
                latest_hearing.c.status_code,
            )
            .where(latest_hearing.c.rn == 1)
            .subquery()
        )

        # ─────────────────────────────────────────────
        # 2. BASE QUERY (DRIVEN BY CaseClients)
        # ─────────────────────────────────────────────
        stmt = (
            select(
                Cases,
                Users.first_name,
                Users.last_name,
                latest_hearing.c.status_code.label("hearing_status_code"),
                CaseClients.engagement_type_code,
            )
            .select_from(CaseClients)
            .join(
                Cases,
                Cases.case_id == CaseClients.case_id,
            )
            .outerjoin(
                Users,
                Cases.aor_user_id == Users.user_id,
            )
            .outerjoin(
                latest_hearing,
                latest_hearing.c.case_id == CaseClients.case_id ,
            )
            .where(
                CaseClients.client_id == client_id,
                CaseClients.chamber_id == chamber_id,
                Cases.deleted_ind.is_(False),
                Cases.chamber_id == chamber_id,
            )
            .distinct(Cases.case_id)
            .order_by(Cases.updated_date.desc())
        )

        rows = (await self.execute(stmt=stmt, session=session)).all()

        # ─────────────────────────────────────────────
        # 3. COUNT QUERY (CONSISTENT)
        # ─────────────────────────────────────────────
        count_stmt = (
            select(func.count())
            .select_from(CaseClients)
            .join(Cases, Cases.case_id == CaseClients.case_id)
            .where(
                CaseClients.client_id == client_id,
                CaseClients.chamber_id == chamber_id,
                Cases.deleted_ind.is_(False),
                Cases.chamber_id == chamber_id,
            )
        )

        total = await self.execute_scalar(session=session, stmt=count_stmt, default=0)

        return rows, total
