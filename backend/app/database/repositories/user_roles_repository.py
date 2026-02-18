

from app.database.repositories.base.repo_context import apply_repo_context
from app.database.repositories.base.base_repository import BaseRepository
from app.database.models.user_roles import UserRoles

@apply_repo_context
class UserRolesRepository(BaseRepository[UserRoles]):
    def __init__(self):
        super().__init__(UserRoles)
