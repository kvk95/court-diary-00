from typing import Optional
from sqlalchemy import func
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.repositories.base.repo_context import apply_repo_context
from app.database.repositories.base.base_repository import BaseRepository
from app.database.models.security_roles import SecurityRoles


@apply_repo_context
class SecurityRolesRepository(BaseRepository[SecurityRoles]):
    """
    Repository for SecurityRoles model.
    Provides helpers for role lookups and CRUD operations.
    """

    def __init__(self):
        super().__init__(SecurityRoles)

    async def get_by_name(
        self, session: AsyncSession, name: str, company_id: int
    ) -> Optional[SecurityRoles]:
        """
        Return a role by name (case-insensitive) within a given company.
        """
        return await self.get_first(
            session=session,
            filters={self.model.company_id: company_id},
            where=[func.lower(SecurityRoles.role_name) == func.lower(name)],
        )
