
from sqlalchemy import select, func, and_
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.repositories.base.repo_context import apply_repo_context
from app.database.repositories.base.base_repository import BaseRepository
from app.database.models.chamber_roles import ChamberRoles
from app.database.models.user_roles import UserRoles

@apply_repo_context
class ChamberRolesRepository(BaseRepository[ChamberRoles]):
    def __init__(self):
        super().__init__(ChamberRoles)    

    async def get_roles_paged(
        self,
        session: AsyncSession,
        *,
        page, limit, search, status):
        stmt = (
            select(
                ChamberRoles,
                func.count(UserRoles.user_role_id).label("user_count"),
            )
            .outerjoin(
                UserRoles,
                and_(
                    ChamberRoles.role_id == UserRoles.role_id,
                    UserRoles.end_date.is_(None),
                ),
            )
            .where(ChamberRoles.deleted_ind.is_(False))
            .group_by(ChamberRoles.role_id)
        )

        if search and search.strip():
            stmt = stmt.where(ChamberRoles.role_name.ilike(f"%{search.strip()}%"))

        if status is not None:
            stmt = stmt.where(ChamberRoles.status_ind == status)

        count_stmt = select(func.count()).select_from(stmt.order_by(None).subquery())
        count_result = await self.execute(session=session, stmt=count_stmt)
        total = count_result.scalar_one() or 0

        stmt = stmt.order_by(ChamberRoles.role_name.asc())
        stmt = stmt.offset((page - 1) * limit).limit(limit)

        result = await self.execute(session=session,stmt=stmt)
        rows = result.all()
        return total,rows
