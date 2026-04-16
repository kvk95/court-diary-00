from typing import Optional, List, Tuple

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, or_, func

from app.database.models.contact_messages import ContactMessages
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
        search: Optional[str] = None,
    ) -> Tuple[List[ContactMessages], int]:

        filters = {}
        where = [ContactMessages.deleted_ind == False]

        # 🔹 Search (OR condition — this is important)
        if search:
            search_term = f"%{search}%"
            where.append(
                or_(
                    ContactMessages.full_name.ilike(search_term),
                    ContactMessages.email.ilike(search_term),
                    ContactMessages.subject.ilike(search_term),
                    ContactMessages.message.ilike(search_term),
                )
            )

        # 🔹 Fetch rows
        rows = await self.list_all(
            session=session,
            filters=filters,
            where=where,
            order_by=[ContactMessages.created_date.desc()],
        )

        # 🔹 Count query
        count_stmt = select(func.count(ContactMessages.message_id)).where(
            ContactMessages.deleted_ind == False
        )

        if search:
            search_term = f"%{search}%"
            count_stmt = count_stmt.where(
                or_(
                    ContactMessages.full_name.ilike(search_term),
                    ContactMessages.email.ilike(search_term),
                    ContactMessages.subject.ilike(search_term),
                    ContactMessages.message.ilike(search_term),
                )
            )

        total = (await session.execute(count_stmt)).scalar() or 0

        return rows, total