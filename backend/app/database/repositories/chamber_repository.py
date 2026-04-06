"""chamber_repository.py — Repository for Chamber model"""



from app.database.models.chamber import Chamber
from app.database.repositories.base.base_repository import BaseRepository
from app.database.repositories.base.repo_context import apply_repo_context


@apply_repo_context
class ChamberRepository(BaseRepository[Chamber]):
    def __init__(self):
        super().__init__(Chamber)