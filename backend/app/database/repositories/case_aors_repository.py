from app.database.repositories.base.repo_context import apply_repo_context
from app.database.repositories.base.base_repository import BaseRepository
from app.database.models.case_aors import CaseAors

@apply_repo_context
class CaseAorsRepository(BaseRepository[CaseAors]):
    def __init__(self):
        super().__init__(CaseAors)
