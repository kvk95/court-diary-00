# app/database/repositories/user_roles_repository.py

from typing import Optional

from datetime import date
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.models.user_roles import UserRoles
from app.database.models.user_roles import UserRoles
from app.database.repositories.base.base_repository import BaseRepository
from app.database.repositories.base.repo_context import apply_repo_context


@apply_repo_context
class UserRolesRepository(BaseRepository[UserRoles]):
    """Repository for UserRoles model."""

    def __init__(self):
        super().__init__(UserRoles)

    async def get_active_role_for_link(
        self,
        session: AsyncSession,
        link_id: str,
        role_id: int,
    ) -> Optional[UserRoles]:
        """
        Check if a specific role is already active for a link.
        Used to avoid duplicate key errors on user_roles.uk_user_role_active.
        """
        return await self.get_first(
            session=session,
            filters={
                UserRoles.link_id: link_id,
                UserRoles.role_id: role_id,
            },
            where=[UserRoles.end_date.is_(None)]
        )

    async def set_user_role(
        self,
        session: AsyncSession,
        link_id: str,
        role_id: int,
        current_user_id: str,
    ) -> None:
        """
        Complete workflow: End existing roles + assign new role.
        Handles duplicate prevention automatically.
        
        Usage:
            await self.user_roles_repo.set_user_role(
                session=self.session,
                link_id=link_id,
                role_id=role_id,
                current_user_id=self.user_id,
            )
        """
        # Check if same role is already active
        existing_active = await self.get_active_role_for_link(
            session=session,
            link_id=link_id,
            role_id=role_id,
        )
        
        # If same role already active, no update needed
        if existing_active:
            return
        
        # End all current active roles for this link
        await self.bulk_update(
            session=session,
            where=[
                UserRoles.link_id == link_id,
                UserRoles.end_date.is_(None),
            ],
            data={
                "end_date": date.today(),
            },
        )

        await self.create(
            session=session,
            data={
                "link_id": link_id,
                "role_id": role_id,
                "start_date": date.today(),
            },
        )