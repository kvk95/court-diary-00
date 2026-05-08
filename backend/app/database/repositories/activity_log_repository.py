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
        stmt = self.__select_activity()

        stmt = stmt.order_by(ActivityLog.created_date.desc())
        stmt =  stmt.limit(limit)
        return stmt

    def __recent_activity_query(
        self, 
        limit: int,
        search: Optional[str],
        module_code: Optional[str],
        date_filter_code: Optional[str],
        include_chamber_id:bool = True
    ):
        stmt = self.__activity_query(limit)
        if include_chamber_id:
            stmt = stmt.where(
                        ActivityLog.actor_chamber_id == self.chamber_id,
                    )

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
            
            # Helper to zero out time components for clean date boundaries
            def to_midnight(dt: datetime) -> datetime:
                return dt.replace(hour=0, minute=0, second=0, microsecond=0)

            if dfc == "T":
                start = to_midnight(now)
                end = start + timedelta(days=1)
                stmt = stmt.where(ActivityLog.created_date >= start, ActivityLog.created_date < end)

            elif dfc == "W":
                # ISO Week starts Monday (weekday() == 0)
                start = to_midnight(now - timedelta(days=now.weekday()))
                end = start + timedelta(days=7)
                stmt = stmt.where(ActivityLog.created_date >= start, ActivityLog.created_date < end)

            elif dfc == "M":
                start = to_midnight(now.replace(day=1))
                # +32 days guarantees we roll into next month, .replace(day=1) snaps to 1st
                end = to_midnight((start + timedelta(days=32)).replace(day=1))
                stmt = stmt.where(ActivityLog.created_date >= start, ActivityLog.created_date < end)

            elif dfc == "Y":
                start = to_midnight(now.replace(month=1, day=1))
                end = to_midnight(start.replace(year=start.year + 1))
                stmt = stmt.where(ActivityLog.created_date >= start, ActivityLog.created_date < end)

            elif dfc == "LW":
                start = to_midnight(now - timedelta(days=now.weekday() + 7))
                end = start + timedelta(days=7)
                stmt = stmt.where(ActivityLog.created_date >= start, ActivityLog.created_date < end)

            elif dfc == "LM":
                first_day_current = to_midnight(now.replace(day=1))
                end = first_day_current
                # Go back 1 day to land in last month, then snap to day 1
                start = to_midnight((first_day_current - timedelta(days=1)).replace(day=1))
                stmt = stmt.where(ActivityLog.created_date >= start, ActivityLog.created_date < end)

            elif dfc == "LY":
                end = to_midnight(now.replace(month=1, day=1))
                start = end.replace(year=end.year - 1)
                stmt = stmt.where(ActivityLog.created_date >= start, ActivityLog.created_date < end)


        # 🧮 count
        count_stmt = select(func.count()).select_from(stmt.subquery())
        return stmt,count_stmt

    async def get_recent_activity(
        self, 
        session,
        limit: int
    ):
        stmt = self.__activity_query(limit)
        stmt = stmt.where(
                    ActivityLog.actor_chamber_id == self.chamber_id,
                )

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
        include_chamber_id:bool = True
    ):
        stmt, count_stmt = self.__recent_activity_query(
            limit, 
            search, 
            module_code, 
            date_filter_code,
            include_chamber_id)
        total = await self.execute_scalar(session=session, stmt=count_stmt, default=0, include_chamber_id = include_chamber_id)

        # 📄 pagination
        stmt = stmt.offset((page - 1) * limit).limit(limit)

        rows = (await self.execute(session=session, stmt=stmt,include_chamber_id=include_chamber_id)).all()

        return rows, total
