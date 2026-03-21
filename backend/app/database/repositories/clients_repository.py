from typing import List, Optional, Tuple
from sqlalchemy import and_, func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession
from app.database.models.clients import Clients
from app.database.repositories.base.base_repository import BaseRepository
from app.database.repositories.base.repo_context import apply_repo_context

@apply_repo_context
class ClientsRepository(BaseRepository[Clients]):
    def __init__(self):
        super().__init__(Clients)

    async def search_clients(
        self,
        session: AsyncSession,
        chamber_id: int,
        query: str,
        limit: int = 20,
    ) -> List[Clients]:
        """Fast search by name, phone, or email for the Link Client modal."""
        kw = f"%{query.strip()}%"
        stmt = (
            select(Clients)
            .where(
                Clients.chamber_id == chamber_id,
                Clients.is_deleted.is_(False),
                Clients.status_ind.is_(True),
                or_(
                    Clients.client_name.ilike(kw),
                    Clients.display_name.ilike(kw),
                    Clients.phone.ilike(kw),
                    Clients.email.ilike(kw),
                ),
            )
            .order_by(Clients.client_name.asc())
            .limit(limit)
        )
        result = await session.execute(stmt)
        return list(result.scalars().all())
