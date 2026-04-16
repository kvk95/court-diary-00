from typing import Any, Dict, Optional

from sqlalchemy.ext.asyncio import AsyncSession    

from app.core.config import Settings
from app.utils.logging_framework.activity_logger import log_activity
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

    # ─────────────────────────────────────────────────────────────────────
    # LOG ACTIVITY — HELPER
    # ─────────────────────────────────────────────────────────────────────
    
    async def log_entity_change(
        self,
        action: str,
        entity_type: str,
        entity_id: str,
        case_id: Optional[str] = None,
        payload: Optional[Any] = None,
        extra_metadata: Optional[Dict] = None,
    ):
        """Standardized logging for entity CRUD operations."""
        metadata = payload.model_dump(exclude_unset=True, exclude_none=True) if payload else {}
        metadata.update(extra_metadata or {})
        if case_id:
            metadata["case_id"] = case_id
        
        target = f"{entity_type}:{entity_id}"
        if case_id:
            target = f"case:{case_id}:{entity_type}:{entity_id}"
        
        await log_activity(action=action, target=target, metadata=metadata)
