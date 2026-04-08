from typing import Optional

from sqlalchemy.ext.asyncio import AsyncSession    

from app.core.config import Settings
from app.utils.refm.refm_resolver import RefmResolver

class BaseService:
    def __init__(self, session: AsyncSession):
        self._session: AsyncSession = session
        self.refm_resolver:RefmResolver = RefmResolver(session=self.session)
        self.settings = Settings()

    @property
    def session(self) -> AsyncSession:
        return self._session
    
    def full_name(self, first: Optional[str], last: Optional[str]) ->str:
        parts = [p for p in [first, last] if p]
        return " ".join(parts) if parts else ""   
    
    
    def get_initials(
        self,
        first: Optional[str],
        last: Optional[str],
        concat_str: str = ""
    ) -> str:
        first_initial = first.strip()[0].upper() if first and first.strip() else ""
        last_initial = last.strip()[0].upper() if last and last.strip() else ""

        if first_initial and last_initial:
            return f"{first_initial}{concat_str}{last_initial}"
        return first_initial or last_initial
    
    @property
    def ui_url(self)->str:
        return self.settings.UI_URL
