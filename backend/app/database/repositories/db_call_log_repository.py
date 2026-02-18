

from app.database.repositories.base.repo_context import apply_repo_context
from app.database.repositories.base.base_repository import BaseRepository
from app.database.models.db_call_log import DbCallLog

@apply_repo_context
class DbCallLogRepository(BaseRepository[DbCallLog]):
    def __init__(self):
        super().__init__(DbCallLog)
