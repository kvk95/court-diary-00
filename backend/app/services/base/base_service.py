from typing import Optional

from sqlalchemy.ext.asyncio import AsyncSession    

from app.utils.refm.refm_resolver import RefmResolver

class BaseService:
    def __init__(self, session: AsyncSession):
        self._session: AsyncSession = session
        self.refm_resolver:RefmResolver = RefmResolver(session=self.session)

    @property
    def session(self) -> AsyncSession:
        return self._session
    
    def full_name(self, first: Optional[str], last: Optional[str]) ->str:
        parts = [p for p in [first, last] if p]
        return " ".join(parts) if parts else ""
