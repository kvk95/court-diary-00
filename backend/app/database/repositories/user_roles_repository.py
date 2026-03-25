# app/database/repositories/user_roles_repository.py

from typing import Optional, Tuple,List,Any, Dict

from datetime import date
from sqlalchemy import and_, update, select,func
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.models.user_roles import UserRoles
from app.database.models.user_roles import UserRoles
from app.database.models.security_roles import SecurityRoles
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
        link_id: int,
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

    async def end_all_active_roles_for_link(
        self,
        session: AsyncSession,
        link_id: int,
        end_date: date,
        updated_by: int,
    ) -> None:
        """
        End all active role assignments for a link (set end_date).
        Used when assigning a new role to replace existing ones.
        """
        stmt = (
            update(UserRoles)
            .where(
                and_(
                    UserRoles.link_id == link_id,
                    UserRoles.end_date.is_(None),
                )
            )
            .values(
                end_date=end_date,
                updated_by=updated_by,
                updated_date=date.today(),
            )
        )
        
        await session.execute(stmt)
        await session.flush()

    async def assign_role_to_link(
        self,
        session: AsyncSession,
        link_id: int,
        role_id: int,
        start_date: date,
        created_by: int,
    ) -> UserRoles:
        """
        Create a new role assignment for a link.
        """
        return await self.create(
            session=session,
            data={
                "link_id": link_id,
                "role_id": role_id,
                "start_date": start_date,
                "created_by": created_by,
            },
        )

    async def set_user_role(
        self,
        session: AsyncSession,
        link_id: int,
        role_id: int,
        current_user_id: int,
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
        await self.end_all_active_roles_for_link(
            session=session,
            link_id=link_id,
            end_date=date.today(),
            updated_by=current_user_id,
        )
        
        # Create new role assignment
        await self.assign_role_to_link(
            session=session,
            link_id=link_id,
            role_id=role_id,
            start_date=date.today(),
            created_by=current_user_id,
        )
    
    async def get_roles_paged(
        self,
        session: AsyncSession,
        page: int,
        limit: int,
        search: Optional[str] = None,
        status: Optional[bool] = None,
    ) -> Tuple[List[Dict[str, Any]], int]:
        """Paginated roles with active user count."""
        stmt = (
            select(
                SecurityRoles.role_id,
                SecurityRoles.role_name,
                SecurityRoles.role_code,
                SecurityRoles.description,
                SecurityRoles.status_ind,
                func.count(UserRoles.user_role_id).label("user_count"),
            )
            .outerjoin(
                UserRoles,
                and_(
                    SecurityRoles.role_id == UserRoles.role_id,
                    UserRoles.end_date.is_(None),
                ),
            )
            .where(SecurityRoles.is_deleted.is_(False))
            .group_by(SecurityRoles.role_id)
        )

        if search and search.strip():
            stmt = stmt.where(SecurityRoles.role_name.ilike(f"%{search.strip()}%"))

        if status is not None:
            stmt = stmt.where(SecurityRoles.status_ind == status)

        # Count
        count_stmt = select(func.count()).select_from(stmt.order_by(None).subquery())
        count_result = await session.execute(count_stmt)
        total = count_result.scalar_one() or 0

        # Pagination
        stmt = stmt.order_by(SecurityRoles.role_name.asc())
        stmt = stmt.offset((page - 1) * limit).limit(limit)

        result = await session.execute(stmt)
        rows = result.all()

        roles = [
            {
                "role_id": row.role_id,
                "role_name": row.role_name,
                "role_code": row.role_code,
                "description": row.description,
                "status_ind": row.status_ind,
                "user_count": row.user_count or 0,
            }
            for row in rows
        ]

        return roles, total