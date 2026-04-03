from typing import Optional

from sqlalchemy import insert
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.models.login_audit import LoginAudit
from app.database.repositories.base.base_repository import BaseRepository
from app.database.repositories.base.repo_context import apply_repo_context
from app.database.models.refm_login_status import RefmLoginStatusConstants
from app.dtos.oauth_dtos import LoginRequest
from app.core.context import get_request_context


@apply_repo_context
class LoginAuditRepository(BaseRepository[LoginAudit]):
    """
    Repository for LoginAudit model.
    Handles login attempt logging with chamber context.
    """

    def __init__(self):
        super().__init__(LoginAudit)

    async def log_login(
        self,
        session: AsyncSession,
        *,
        user_id: Optional[str] = None,
        loginRequest: LoginRequest,
        status_code: str,  # 'S' = Success, 'F' = Failed
        failure_reason: Optional[str] = None,
        chamber_id: Optional[str] = None,  # ✅ NEW: Track which chamber was accessed
    ) -> None:
        """
        Log a login attempt to the audit table.
        
        Args:
            session: DB session
            user_id: User ID (None if login failed before user lookup)
            loginRequest: The login request DTO
            status_code: Login status code from refm_login_status
            failure_reason: Reason for failure (if any)
            chamber_id: Chamber ID being accessed (resolved at login time)
        """
        # Get IP and User-Agent from request context
        ctx = get_request_context()
        ip_address = ctx.get("ip_address", "0.0.0.0")
        user_agent = ctx.get("user_agent", "Unknown")

        # If chamber_id not provided, try to resolve from context
        if chamber_id is None:
            chamber_id = ctx.get("chamber_id")

        # Prepare audit data
        audit_data = {
            "actor_user_id": user_id,
            "actor_chamber_id": chamber_id,  # ✅ Required per schema
            "email": loginRequest.email,
            "status_code": status_code,
            "failure_reason": failure_reason,
            "ip_address": ip_address,
            "user_agent": user_agent,
        }

        # Direct INSERT for audit (bypass repository create for performance)
        stmt = insert(LoginAudit).values(**audit_data)
        self._log_stmt(stmt, session)
        await session.execute(stmt)
        await session.flush()

    async def get_recent_logins(
        self,
        session: AsyncSession,
        user_id: str,
        limit: int = 10,
    ) -> list:
        """
        Get recent login attempts for a user.
        """
        from sqlalchemy import select, desc

        stmt = (
            select(LoginAudit)
            .where(LoginAudit.user_id == user_id)
            .order_by(desc(LoginAudit.login_time))
            .limit(limit)
        )

        self._log_stmt(stmt, session)
        result = await session.execute(stmt)
        return list(result.scalars().all())

    async def get_failed_logins_by_ip(
        self,
        session: AsyncSession,
        ip_address: str,
        minutes: int = 30,
    ) -> int:
        """
        Count failed login attempts from an IP in the last N minutes.
        Used for rate limiting / brute force detection.
        """
        from sqlalchemy import select, func, and_
        from datetime import datetime, timedelta

        cutoff = datetime.utcnow() - timedelta(minutes=minutes)

        stmt = (
            select(func.count())
            .select_from(LoginAudit)
            .where(
                and_(
                    LoginAudit.ip_address == ip_address,
                    LoginAudit.status_code == RefmLoginStatusConstants.FAILED,
                    LoginAudit.login_time >= cutoff,
                )
            )
        )

        self._log_stmt(stmt, session)
        result = await session.execute(stmt)
        return result.scalar_one() or 0