# app/database/repositories/user_roles_repository.py

from typing import Optional, Tuple,List,Any, Dict

from datetime import date
from sqlalchemy import and_, select,func
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.models.user_roles import UserRoles
from app.database.models.user_roles import UserRoles
from app.database.models.chamber_roles import ChamberRoles
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
                ChamberRoles.role_id,
                ChamberRoles.role_name,
                ChamberRoles.description,
                ChamberRoles.status_ind,
                func.count(UserRoles.user_role_id).label("user_count"),
            )
            .outerjoin(
                UserRoles,
                and_(
                    ChamberRoles.role_id == UserRoles.role_id,
                    UserRoles.end_date.is_(None),
                ),
            )
            .where(ChamberRoles.deleted_ind.is_(False))
            .group_by(ChamberRoles.role_id)
        )

        if search and search.strip():
            stmt = stmt.where(ChamberRoles.role_name.ilike(f"%{search.strip()}%"))

        if status is not None:
            stmt = stmt.where(ChamberRoles.status_ind == status)

        # Count
        count_stmt = select(func.count()).select_from(stmt.order_by(None).subquery())
        total = await self.execute_scalar( session=session, stmt=count_stmt)

        # Pagination
        stmt = stmt.order_by(ChamberRoles.role_name.asc())
        stmt = stmt.offset((page - 1) * limit).limit(limit)

        result = await self.execute( session=session, stmt=stmt)
        rows = result.all()

        roles = [
            {
                "role_id": row.role_id,
                "role_name": row.role_name,
                "description": row.description,
                "status_ind": row.status_ind,
                "user_count": row.user_count or 0,
            }
            for row in rows
        ]

        return roles, total