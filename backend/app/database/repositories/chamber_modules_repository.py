
from sqlalchemy import select

from app.database.repositories.base.repo_context import apply_repo_context
from app.database.repositories.base.base_repository import BaseRepository
from app.database.models.chamber_modules import ChamberModules

@apply_repo_context
class ChamberModulesRepository(BaseRepository[ChamberModules]):
    def __init__(self):
        super().__init__(ChamberModules)

    async def get_modules_by_chamber(self, session, chamber_id: str):

        stmt = select(
            ChamberModules.module_code,
            ChamberModules.chamber_module_id,
        ).where(
            ChamberModules.chamber_id == chamber_id,
            ChamberModules.active_ind.is_(True),
        )

        result = await self.execute(session=session, stmt=stmt)

        rows = result.scalars().all()

        return {
            r["module_code"]: r["chamber_module_id"]
            for r in rows
        }