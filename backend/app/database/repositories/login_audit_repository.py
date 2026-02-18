from datetime import datetime, timezone
from typing import Optional

from sqlalchemy.ext.asyncio import AsyncSession

from app.database.models.login_audit import LoginAudit
from app.dtos.oauth_dtos import LoginRequest
from app.database.repositories.base.repo_context import apply_repo_context
from app.database.repositories.base.base_repository import BaseRepository


@apply_repo_context
class LoginAuditRepository(BaseRepository[LoginAudit]):
    """
    Repository for LoginAudit model.
    Provides a helper to log login attempts with strict CRUD semantics.
    """

    def __init__(self):
        super().__init__(LoginAudit)

    async def log_login(
        self,
        session: AsyncSession,
        *,
        user_id: Optional[int],
        loginRequest: LoginRequest,
        status_code: str,
        failure_reason: Optional[str],
    ) -> LoginAudit:
        """
        Insert a login audit record.
        - user_id: optional FK to Users
        - loginRequest: carries email, ip_address, company_id, user_agent
        - status: enum (Success, Failure, etc.)
        - failure_reason: optional string
        """
        data = {
            "user_id": user_id,
            "email": loginRequest.email,
            "login_time": datetime.now(timezone.utc),
            "ip_address": loginRequest.ip_address or "unknown",
            "company_id": loginRequest.company_id or 1,
            "status_code": status_code,
            "user_agent": loginRequest.user_agent or "unknown",
            "failure_reason": failure_reason,
        }

        # Use BaseRepository.create() for consistency
        obj = await self.create(session, data=data)
        return obj
