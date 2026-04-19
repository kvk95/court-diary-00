from typing import Optional, List, Tuple

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, or_, func, case

from app.database.models.contact_messages import ContactMessages
from app.database.models.refm_ticket_status import RefmTicketStatusConstants
from app.database.repositories.base.base_repository import BaseRepository
from app.database.repositories.base.repo_context import apply_repo_context


@apply_repo_context
class ContactMessagesRepository(BaseRepository[ContactMessages]):
    """Repository for ContactMessages"""

    def __init__(self):
        super().__init__(ContactMessages)

    async def list_messages(
        self,
        session: AsyncSession,
        status_code: Optional[str] = None,
        search: Optional[str] = None,
    ) -> Tuple[List[ContactMessages], int]:

        where = [ContactMessages.deleted_ind == False]

        if status_code:
            where.append(ContactMessages.status_code == status_code)

        if search:
            kw = f"%{search}%"
            where.append(
                or_(
                    ContactMessages.full_name.ilike(kw),
                    ContactMessages.email.ilike(kw),
                    ContactMessages.subject.ilike(kw),
                    ContactMessages.message.ilike(kw),
                )
            )

        rows = await self.list_all(
            session=session,
            where=where,
            order_by=[ContactMessages.created_date.desc()],
        )

        count_stmt = select(func.count(ContactMessages.message_id)).where(*where)
        total = (await session.execute(count_stmt)).scalar() or 0

        return rows, total
    
    async def get_stats(self, session: AsyncSession):
        stmt = select(
            func.count(ContactMessages.message_id).label("total"),
            func.sum(case((ContactMessages.status_code == RefmTicketStatusConstants.OPEN, 1), else_=0)).label("open"),
            func.sum(case((ContactMessages.status_code == RefmTicketStatusConstants.IN_PROGRESS, 1), else_=0)).label("in_progress"),
            func.sum(case((ContactMessages.status_code == RefmTicketStatusConstants.RESOLVED, 1), else_=0)).label("resolved"),
        ).where(ContactMessages.deleted_ind == False)

        result = await session.execute(stmt)
        return result.first()