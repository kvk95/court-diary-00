# app\database\repositories\activity_log_repository.py


from sqlalchemy import func, select

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
    ):
        stmt = self.__activity_query(limit)

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
