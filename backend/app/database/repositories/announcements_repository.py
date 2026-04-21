from typing import Any, List, Optional, Tuple, Dict

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
    ) -> Tuple[List[Dict[str, Any]], int]:

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
        total = (await session.execute(count_stmt)).scalar()

        # 📄 pagination
        stmt = stmt.order_by(Announcements.created_date.desc())
        stmt = stmt.offset((page - 1) * limit).limit(limit)

        rows = (await session.execute(stmt)).all()

        result = []
        for r in rows:
            result.append({
                "announcement_id": r.announcement_id,
                "title": r.title,
                "content": r.content,
                "type_code": r.type_code,
                "audience_code": r.audience_code,
                "status_code": r.status_code,
                "scheduled_at": r.scheduled_at,
                "expires_at": r.expires_at,
                "created_date": r.created_date,
            })

        return result, total
