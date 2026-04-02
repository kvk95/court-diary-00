

from sqlalchemy import distinct, func, select
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

        primary_aor = (
            select(
                CaseAors.case_id,
                func.min(CaseAors.user_id).label("aor_user_id"),
            )
            .where(
                CaseAors.chamber_id == chamber_id,
                CaseAors.primary_ind.is_(True),
                CaseAors.withdrawal_date.is_(None),
            )
            .group_by(CaseAors.case_id)
            .subquery()
        )

        # ONE row per case for this client — pick primary if exists,
        # else pick the first role alphabetically
        linked_cases = (
            select(
                CaseClients.case_id,
                CaseClients.case_client_id,
                CaseClients.client_id,
                CaseClients.party_role_code,
                CaseClients.primary_ind,
                CaseClients.chamber_id,
                func.row_number().over(
                    partition_by=CaseClients.case_id,
                    order_by=[
                        CaseClients.primary_ind.desc(),
                        CaseClients.party_role_code.asc(),
                    ],
                ).label("rn"),
            )
            .where(
                CaseClients.client_id == client_id,
                CaseClients.chamber_id == chamber_id,
            )
            .subquery()
        )

        # Wrap to filter rn == 1 — guarantees one row per case
        linked_cases_deduped = (
            select(
                linked_cases.c.case_id,
                linked_cases.c.case_client_id,
                linked_cases.c.client_id,
                linked_cases.c.party_role_code,
                linked_cases.c.primary_ind,
                linked_cases.c.chamber_id,
            )
            .where(linked_cases.c.rn == 1)
            .subquery()
        )

        stmt = (
            select(
                Cases,
                Users.first_name,
                Users.last_name,
                primary_aor.c.aor_user_id,
                latest_hearing.c.status_code.label("hearing_status_code"),
                linked_cases_deduped.c.party_role_code,
            )
            .join(linked_cases_deduped, Cases.case_id == linked_cases_deduped.c.case_id)
            .outerjoin(primary_aor, Cases.case_id == primary_aor.c.case_id)
            .outerjoin(Users, Users.user_id == primary_aor.c.aor_user_id)
            .outerjoin(latest_hearing, Cases.case_id == latest_hearing.c.case_id)
            .where(
                Cases.deleted_ind.is_(False),
                Cases.chamber_id == chamber_id,
            )
            .order_by(Cases.updated_date.desc())
        )

        rows = (await self.execute(session=session, stmt=stmt)).all()

        count_stmt = (
            select(func.count(distinct(CaseClients.case_id)))
            .where(
                CaseClients.client_id == client_id,
                CaseClients.chamber_id == chamber_id,
            )
        )
        total = await self.execute_scalar(session=session, stmt=count_stmt, default=0)

        return rows, total
