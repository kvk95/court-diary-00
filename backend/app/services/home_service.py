# app/services/home_service.py
from typing import Optional

from sqlalchemy.ext.asyncio import AsyncSession

from app.database.repositories.home_repository import HomeRepository
from app.dtos.home_dtos import HomeStatsOut
from app.services.base.base_service import BaseService


class HomeService(BaseService):

    def __init__(
        self,
        session: AsyncSession,
        home_repo: Optional[HomeRepository] = None,
    ):
        super().__init__(session)
        self.repo: HomeRepository = home_repo or HomeRepository()

    async def get_home_stats(self) -> HomeStatsOut:

        row = await self.repo.get_home_stats(self.session)

        if not row:
            return HomeStatsOut();

        return HomeStatsOut(
            total_professionals=row.total_professionals or 0,
            total_cases=row.total_cases or 0,
        )