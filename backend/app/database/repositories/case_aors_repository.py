
from typing import Optional

from sqlalchemy import or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.models.user_chamber_link import UserChamberLink
from app.database.models.users import Users
from app.database.repositories.base.repo_context import apply_repo_context
from app.database.repositories.base.base_repository import BaseRepository
from app.database.models.case_aors import CaseAors

@apply_repo_context
class CaseAorsRepository(BaseRepository[CaseAors]):
    def __init__(self):
        super().__init__(CaseAors)

    from sqlalchemy import or_

    async def aors_get_by_chamber(
            self,
            session: AsyncSession,
            search: Optional[str],
        ):

        where = [
            Users.advocate_ind.is_(True),
            Users.status_ind.is_(True),
            UserChamberLink.chamber_id == self.chamber_id,
        ]

        if search and search.strip():
            kw = f"%{search.strip()}%"
            where.append(
                or_(
                    Users.first_name.ilike(kw),
                    Users.last_name.ilike(kw),
                    Users.email.ilike(kw),
                    Users.phone.ilike(kw),
                )
            )

        stmt = (
            select(Users)
            .join(
                UserChamberLink,
                UserChamberLink.user_id == Users.user_id
            )
            .where(*where)
            .order_by(Users.first_name.asc())
        )

        rows = await self.execute(stmt=stmt, session=session)

        return rows.scalars().all()


