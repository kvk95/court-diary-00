# app\database\repositories\activity_log_repository.py


from datetime import datetime, timedelta
from typing import Optional

from sqlalchemy import func, or_, select

from app.database.repositories.base.repo_context import apply_repo_context
from app.database.repositories.base.base_repository import BaseRepository
from app.database.models.activity_log import ActivityLog

@apply_repo_context
class ActivityLogRepository(BaseRepository[ActivityLog]):
    def __init__(self):
        super().__init__(ActivityLog)    

    def __select_activity(self):
        return select(
                    ActivityLog.action,
                    ActivityLog.actor_user_id,
                    ActivityLog.created_date,
                    ActivityLog.metadata_json,
                    ActivityLog.module_code,
                )

    def __activity_query(self, limit):
        stmt = self.__select_activity().where(
                    ActivityLog.actor_chamber_id == self.chamber_id,
                )

        stmt = stmt.order_by(ActivityLog.created_date.desc())
        stmt =  stmt.limit(limit)
        return stmt

    async def get_recent_activity(
        self, 
        session,
        limit: int
    ):
        stmt = self.__activity_query(limit)

        rows = (await self.execute(session=session, stmt=stmt)).all()

        return rows

    async def get_recent_activity_paged(
        self, 
        session,
        page: int,
        limit: int,
        search: Optional[str],
        module_code: Optional[str],
        date_filter_code: Optional[str],
    ):
        stmt = self.__activity_query(limit)

        if search and search.strip():
            kw = f"%{search.strip()}%"
            stmt = stmt.where(
                or_(
                    ActivityLog.target.like(f"case:{kw}%"),
                    ActivityLog.module_code.like(f"{kw}%"),
                    ActivityLog.metadata_json.like(f"{kw}%"),
                )
            )
        if module_code:
            stmt = stmt.where(ActivityLog.module_code == module_code)
        
        if date_filter_code:
            dfc = date_filter_code.strip().upper()
            now = datetime.now()
            
            if dfc == "T":
                start = now.replace(hour=0, minute=0, second=0, microsecond=0)
                end = start + timedelta(days=1)
                stmt = stmt.where(ActivityLog.created_date >= start, ActivityLog.created_date < end)

            elif dfc == "W":
                # ISO week starts on Monday. Change to (now.weekday() + 1) % 7 if you want Sunday.
                start = (now - timedelta(days=now.weekday())).replace(hour=0, minute=0, second=0, microsecond=0)
                end = start + timedelta(days=7)
                stmt = stmt.where(ActivityLog.created_date >= start, ActivityLog.created_date < end)

            elif dfc == "M":
                start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
                if now.month == 12:
                    end = now.replace(year=now.year + 1, month=1, day=1)
                else:
                    end = now.replace(month=now.month + 1, day=1)
                stmt = stmt.where(ActivityLog.created_date >= start, ActivityLog.created_date < end)


        # 🧮 count
        count_stmt = select(func.count()).select_from(stmt.subquery())
        total = await self.execute_scalar(session=session, stmt=count_stmt, default=0)

        # 📄 pagination
        stmt = stmt.offset((page - 1) * limit).limit(limit)

        rows = (await self.execute(session=session, stmt=stmt)).all()

        return rows, total

    async def get_all_chamber_recent_activity_paged(
        self, 
        session,
        page: int,
        limit: int,
    ):
        stmt = self.__select_activity()
        stmt = stmt.order_by(ActivityLog.created_date.desc())
        stmt =  stmt.limit(limit)

        # 🧮 count
        count_stmt = select(func.count()).select_from(stmt.subquery())
        total = await self.execute_scalar(session=session, stmt=count_stmt, default=0)

        # 📄 pagination
        stmt = stmt.offset((page - 1) * limit).limit(limit)

        rows = (await self.execute(session=session, stmt=stmt)).all()

        return rows, total
