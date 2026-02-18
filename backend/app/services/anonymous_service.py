from datetime import datetime

from sqlalchemy.ext.asyncio import AsyncSession

from app.database.cache.refm_cache import RefmCache, RefmData
from app.dtos.anonymous_dtos import ServerDateTimeOut

from .base.base_service import BaseService


class AnonymousService(BaseService):
    def __init__(self, session: AsyncSession):
        super().__init__(session)

    async def get_server_datetime(self) -> ServerDateTimeOut:
        """
        Returns the current date/time formatted as ISO string.
        """
        now = datetime.now()
        formatted = now.strftime("%Y-%m-%d %H:%M:%S")
        return ServerDateTimeOut(server_datetime=formatted)

    async def get_all_refm(self) -> RefmData:
        return await RefmCache.get(session=self.session)
