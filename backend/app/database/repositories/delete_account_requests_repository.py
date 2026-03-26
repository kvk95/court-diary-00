from typing import List, Optional, Tuple, Dict, Any

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.models.delete_account_requests import DeleteAccountRequests
from app.database.models.users import Users
from app.database.models.refm_user_deletion_status import (
    RefmUserDeletionStatusConstants,
)
from app.database.repositories.base.base_repository import BaseRepository
from app.database.repositories.base.repo_context import apply_repo_context


@apply_repo_context
class DeleteAccountRequestsRepository(BaseRepository[DeleteAccountRequests]):
    def __init__(self):
        super().__init__(DeleteAccountRequests)

    async def list_pending(self, session: AsyncSession) -> List[DeleteAccountRequests]:
        stmt = select(self.model).where(
            self.model.status_code == RefmUserDeletionStatusConstants.PENDING
        )
        res = await session.execute(stmt)
        return list(res.scalars().all())

    async def get_by_request_no(
        self, session: AsyncSession, request_no: str
    ) -> Optional[DeleteAccountRequests]:
        stmt = select(self.model).where(self.model.request_no == request_no)
        res = await session.execute(stmt)
        return res.scalars().first()
    
    async def get_deletion_requests_paginated(
        self,
        session: AsyncSession,
        chamber_id: str,
        page: int = 1,
        limit: int = 50,
        status: Optional[str] = None,
    ) -> Tuple[List[Dict[str, Any]], int]:
        """
        Get paginated deletion requests with user info.
        Returns list of dicts for service to transform into DTOs.
        """
        # Build base query with join
        stmt = (
            select(
                DeleteAccountRequests.request_id,
                DeleteAccountRequests.request_no,
                DeleteAccountRequests.user_id,
                DeleteAccountRequests.request_date,
                DeleteAccountRequests.status_code,
                DeleteAccountRequests.notes,
                DeleteAccountRequests.created_by,
                Users.email,
                Users.first_name,
                Users.last_name,
            )
            .join(Users, DeleteAccountRequests.user_id == Users.user_id)
            .where(DeleteAccountRequests.chamber_id == chamber_id)
        )

        # Apply status filter
        if status:
            stmt = stmt.where(DeleteAccountRequests.status_code == status)

        # Count total (before pagination)
        count_stmt = select(func.count()).select_from(stmt.order_by(None).subquery())
        count_result = await session.execute(count_stmt)
        total = count_result.scalar_one() or 0

        # Apply ordering and pagination
        stmt = stmt.order_by(DeleteAccountRequests.request_date.desc())
        stmt = stmt.offset((page - 1) * limit).limit(limit)

        result = await session.execute(stmt)
        rows = result.all()

        # Return as list of dicts
        requests = [
            {
                "request_id": row.request_id,
                "request_no": row.request_no,
                "user_id": row.user_id,
                "user_email": row.email,
                "user_name": f"{row.first_name} {row.last_name or ''}".strip(),
                "request_date": row.request_date,
                "status_code": row.status_code,
                "notes": row.notes,
                "created_by": row.created_by,
            }
            for row in rows
        ]

        return requests, total
