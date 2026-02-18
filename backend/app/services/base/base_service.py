from sqlalchemy.ext.asyncio import AsyncSession    

from app.utils.refm.refm_resolver import RefmResolver

class BaseService:
    def __init__(self, session: AsyncSession):
        self._session: AsyncSession = session
        self.refm_resolver:RefmResolver = RefmResolver(session=self.session)

    @property
    def session(self) -> AsyncSession:
        return self._session
