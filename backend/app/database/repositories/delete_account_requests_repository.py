from typing import List, Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.models.delete_account_requests import DeleteAccountRequests
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
