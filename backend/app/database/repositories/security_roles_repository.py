

from app.database.models.security_roles import SecurityRoles
from app.database.models.security_roles import SecurityRoles
from app.database.repositories.base.base_repository import BaseRepository
from app.database.repositories.base.repo_context import apply_repo_context


@apply_repo_context
class SecurityRolesRepository(BaseRepository[SecurityRoles]):
    """
    Repository for SecurityRoles model.
    Note: SecurityRoles is a GLOBAL table (not scoped to chamber).
    """

    def __init__(self):
        super().__init__(SecurityRoles) 