from typing import Optional

from sqlalchemy import select
from sqlalchemy.orm import aliased


from app.database.models.refm_court_type import RefmCourtType
from app.database.models.refm_states import RefmStates
from app.database.repositories.base.repo_context import apply_repo_context
from app.database.repositories.base.base_repository import BaseRepository
from app.database.models.courts import Courts

@apply_repo_context
class CourtsRepository(BaseRepository[Courts]):
    def __init__(self):
        super().__init__(Courts)

    async def list_courts(
        self,
        session,
        limit: int,
        search: Optional[str],
        state_code: Optional[str],
        court_type_code: Optional[str],
    ):

        s = aliased(RefmStates)
        t = aliased(RefmCourtType)

        stmt = (
            select(
                Courts.court_code,
                Courts.court_name,
                Courts.court_type_code,
                t.description.label("court_type_name"),
                Courts.state_code,
                s.description.label("state_name"),
            )
            .select_from(Courts)
            .outerjoin(s, Courts.state_code == s.code)
            .outerjoin(t, Courts.court_type_code == t.code)
        )

        # 🔍 search
        if search:
            stmt = stmt.where(Courts.court_name.ilike(f"%{search}%"))

        # 🎯 filters
        if state_code:
            stmt = stmt.where(Courts.state_code == state_code)

        if court_type_code:
            stmt = stmt.where(Courts.court_type_code == court_type_code)

        # 📄 ordering + limit
        stmt = stmt.order_by(Courts.court_name.asc()).limit(limit)

        rows = (await session.execute(stmt)).all()

        return rows
