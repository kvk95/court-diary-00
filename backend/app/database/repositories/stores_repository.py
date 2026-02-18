

from app.database.repositories.base.repo_context import apply_repo_context
from app.database.repositories.base.base_repository import BaseRepository
from app.database.models.stores import Stores

@apply_repo_context
class StoresRepository(BaseRepository[Stores]):
    def __init__(self):
        super().__init__(Stores)
