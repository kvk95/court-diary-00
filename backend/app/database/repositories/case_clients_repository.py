

from sqlalchemy import and_, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.models.case_aors import CaseAors
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
        latest_hearing = (
            select(
                Hearings.case_id,
                Hearings.status_code,
                func.row_number().over(
                    partition_by=Hearings.case_id,
                    order_by=Hearings.hearing_date.desc(),
                ).label("rn"),
            )
            .where(
                Hearings.deleted_ind.is_(False),
                Hearings.chamber_id == chamber_id,
            )
            .subquery()
        )

        latest_hearing = (
            select(latest_hearing.c.case_id, latest_hearing.c.status_code)
            .where(latest_hearing.c.rn == 1)
            .subquery()
        )

        stmt = (
            select(
                Cases,
                Users.first_name,
                Users.last_name,
                CaseAors.user_id.label("aor_user_id"),  # ✅ ADD THIS
                latest_hearing.c.status_code.label("hearing_status_code"),
                CaseClients.party_role_code,
                CaseClients,
            )
            .join(CaseClients, CaseClients.case_id == Cases.case_id)

            # ✅ FIXED AOR JOIN
            .outerjoin(
                CaseAors,
                and_(
                    CaseAors.case_id == Cases.case_id,
                    CaseAors.primary_ind.is_(True),
                    CaseAors.withdrawal_date.is_(None),
                ),
            )
            .outerjoin(
                Users,
                Users.user_id == CaseAors.user_id,
            )

            .outerjoin(latest_hearing, Cases.case_id == latest_hearing.c.case_id)

            .where(
                CaseClients.client_id == client_id,
                CaseClients.chamber_id == chamber_id,
                Cases.deleted_ind.is_(False),
            )
            .order_by(Cases.updated_date.desc())
        )

        rows = (await self.execute(session=session, stmt=stmt)).all()

        count_stmt = (
            select(func.count())
            .select_from(CaseClients)
            .where(
                CaseClients.client_id == client_id,
                CaseClients.chamber_id == chamber_id,
            )
        )

        total = await self.execute_scalar(session=session, stmt=count_stmt, default=0)

        return rows, total
