from typing import Optional

from sqlalchemy import select, func

from app.database.repositories.base.repo_context import apply_repo_context
from app.database.repositories.base.base_repository import BaseRepository
from app.database.models.announcements import Announcements

@apply_repo_context
class AnnouncementsRepository(BaseRepository[Announcements]):
    def __init__(self):
        super().__init__(Announcements)
    
    async def list_announcements(
        self,
        session,
        page: int,
        limit: int,
        search: Optional[str],
        status: Optional[str],
        type_code: Optional[str],
        audience_code: Optional[str],
    ):

        stmt = (
            select(
                Announcements.announcement_id,
                Announcements.title,
                Announcements.content,
                Announcements.type_code,
                Announcements.audience_code,
                Announcements.status_code,
                Announcements.scheduled_at,
                Announcements.expires_at,
                Announcements.created_date,
            )
            .where(Announcements.deleted_ind.is_(False))
        )

        # 🔍 search
        if search:
            kw = f"%{search}%"
            stmt = stmt.where(
                Announcements.title.ilike(kw)
            )

        # 🎯 filters
        if status:
            stmt = stmt.where(Announcements.status_code == status)

        if type_code:
            stmt = stmt.where(Announcements.type_code == type_code)

        if audience_code:
            stmt = stmt.where(Announcements.audience_code == audience_code)

        # 🧮 count
        count_stmt = select(func.count()).select_from(stmt.subquery())
        total = await self.execute_scalar(session=session, stmt=count_stmt, default=0)

        # 📄 pagination
        stmt = stmt.order_by(Announcements.created_date.desc())
        stmt = stmt.offset((page - 1) * limit).limit(limit)

        rows = (await self.execute(session=session, stmt=stmt)).all()

        return rows, total
