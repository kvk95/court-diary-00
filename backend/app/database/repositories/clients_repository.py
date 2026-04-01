
from typing import List, Optional
from sqlalchemy import func, or_, select, case
from sqlalchemy.ext.asyncio import AsyncSession
from app.database.models.case_clients import CaseClients
from app.database.models.clients import Clients
from app.database.models.refm_client_type import RefmClientTypeConstants
from app.database.models.refm_party_type import RefmPartyTypeConstants
from app.database.repositories.base.base_repository import BaseRepository
from app.database.repositories.base.repo_context import apply_repo_context

@apply_repo_context
class ClientsRepository(BaseRepository[Clients]):
    def __init__(self):
        super().__init__(Clients)

    async def get_client_summary(
        self,
        session: AsyncSession,
        chamber_id: str,
    ):
        stmt = select(
            # CLIENT STATS (no join)
            func.count(Clients.client_id).label("total"),

            func.count(
                case((Clients.party_type_code == RefmPartyTypeConstants.PARTY_TO_CASE, 1))
            ).label("parties"),

            func.count(
                case((Clients.client_type_code == RefmClientTypeConstants.INDIVIDUAL, 1))
            ).label("individual"),

            func.count(
                case((Clients.client_type_code == RefmClientTypeConstants.CORPORATE, 1))
            ).label("corporate"),

            # 🔥 ASSOCIATIONS (separate query)
            select(func.count(CaseClients.case_client_id))
            .where(CaseClients.chamber_id == chamber_id)
            .scalar_subquery()
            .label("case_associations"),
        ).where(
            Clients.chamber_id == chamber_id,
            Clients.deleted_ind.is_(False),
        )

        row = await self.execute(session=session, stmt=stmt)
        return row.one()

    async def search_clients(
        self,
        session: AsyncSession,
        chamber_id: str,
        search:  Optional[str],
        limit: int = 20,
    ) -> List[Clients]:
        """Fast search by name, phone, or email for the Link Client modal."""
        if search:
            kw = f"%{search.strip()}%"
        stmt = (
            select(Clients)
            .where(
                Clients.chamber_id == chamber_id,
                Clients.deleted_ind.is_(False),          
            ).order_by(Clients.client_name.asc())
            .limit(limit)
        )

        if search:
            stmt = stmt.where(
                or_(
                    Clients.client_name.ilike(kw),
                    Clients.display_name.ilike(kw),
                    Clients.phone.ilike(kw),
                    Clients.email.ilike(kw),
                )
            )
            
        result = await self.execute( session=session, stmt=stmt)
        return list(result.scalars().all())
