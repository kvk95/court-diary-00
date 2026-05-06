# app/database/repositories/home_repository.py

from sqlalchemy import select, func, distinct
from app.database.repositories.base.base_repository import BaseRepository
from app.database.repositories.base.repo_context import apply_repo_context

from app.database.models.user_chamber_link import UserChamberLink
from app.database.models.users import Users
from app.database.models.cases import Cases


@apply_repo_context
class HomeRepository(BaseRepository[Users]):
    def __init__(self):
        super().__init__(Users)

    async def get_home_stats(self, session):

        stmt = select(
            # 👨‍⚖️ professionals (active users in any chamber)
            func.count(distinct(UserChamberLink.user_id)).label("total_professionals"),

            # ⚖️ total cases
            func.count(Cases.case_id).label("total_cases"),
        ).select_from(UserChamberLink) \
         .join(Users, Users.user_id == UserChamberLink.user_id) \
         .outerjoin(Cases, Cases.chamber_id == UserChamberLink.chamber_id) \
         .where(
            UserChamberLink.status_ind.is_(True),
            UserChamberLink.left_date.is_(None),
            Cases.deleted_ind.is_(False),
        )

        result = await self.execute(session=session, stmt=stmt)
        return result.first()