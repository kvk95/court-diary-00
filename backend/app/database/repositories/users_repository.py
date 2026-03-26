# app/database/repositories/users_repository.py

from typing import List, Optional, Tuple, Dict, Any
from datetime import datetime
from sqlalchemy import and_, func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.models.chamber_roles import ChamberRoles
from app.database.models.user_chamber_link import UserChamberLink
from app.database.models.user_profiles import UserProfiles
from app.database.models.user_roles import UserRoles
from app.database.models.users import Users
from app.database.models.chamber import Chamber
from app.database.models.user_invitations import UserInvitations
from app.database.repositories.base.base_repository import BaseRepository
from app.database.repositories.role_permissions_repository import RolePermissionsRepository
from app.database.repositories.base.repo_context import apply_repo_context


@apply_repo_context
class UsersRepository(BaseRepository[Users]):
    """
    Repository for Users model.
    All chamber-scoped queries join through user_chamber_link.
    """

    def __init__(self):
        super().__init__(Users)

    async def get_user_full_details(
        self,
        session: AsyncSession,
        *,
        user_id: Optional[str] = None,
        email: Optional[str] = None,
        chamber_id: str,
    ) -> Optional[Dict[str, Any]]:
        """
        Get complete user details with profile, role, permissions, and chamber.
        All complex joins handled in repository layer.
        Returns dict for service to transform into DTO.
        """
        if not user_id and not email:
            raise ValueError("Either user_id or email must be provided")

        # Build base query with all joins
        stmt = (
            select(
                # User fields
                Users.user_id,
                Users.first_name,
                Users.last_name,
                Users.email,
                Users.phone,
                Users.status_ind,
                Users.created_date,
                # Profile fields
                UserProfiles.profile_id,
                UserProfiles.header_color,
                UserProfiles.sidebar_color,
                UserProfiles.primary_color,
                UserProfiles.font_family,
                # Role fields
                ChamberRoles.role_id,
                ChamberRoles.role_name,
                ChamberRoles.description.label("role_description"),
                ChamberRoles.status_ind.label("role_status_ind"),
                # Chamber fields
                Chamber.chamber_id,
                Chamber.chamber_name,
            )
            .join(
                UserChamberLink,
                and_(
                    Users.user_id == UserChamberLink.user_id,
                    UserChamberLink.chamber_id == chamber_id,
                    UserChamberLink.left_date.is_(None),
                    UserChamberLink.status_ind.is_(True),
                )
            )
            .outerjoin(UserProfiles, Users.user_id == UserProfiles.user_id)
            .outerjoin(
                UserRoles,
                and_(
                    UserChamberLink.link_id == UserRoles.link_id,
                    UserRoles.end_date.is_(None),
                )
            )
            .outerjoin(ChamberRoles, UserRoles.chamber_role_id == ChamberRoles.role_id)
            .join(Chamber, UserChamberLink.chamber_id == Chamber.chamber_id)
            .where(Users.is_deleted.is_(False))
        )

        if user_id:
            stmt = stmt.where(Users.user_id == user_id)
        else:
            stmt = stmt.where(Users.email == email)

        self._log_stmt(stmt, session)
        result = await session.execute(stmt)
        row = result.first()

        if not row:
            return None

        # Get permissions for this role in this chamber
        role_permissions_repo = RolePermissionsRepository()
        permissions = await role_permissions_repo.get_role_permissions(
            session=session,
            chamber_id=chamber_id,
            user_id=row.user_id,
        )

        return {
            "user_id": row.user_id,
            "first_name": row.first_name,
            "last_name": row.last_name,
            "email": row.email,
            "phone": row.phone,
            "status_ind": row.status_ind,
            "created_date": row.created_date,
            "profile": {
                "header_color": row.header_color,
                "sidebar_color": row.sidebar_color,
                "primary_color": row.primary_color,
                "font_family": row.font_family,
            } if row.profile_id else None,
            "role": {
                "role_id": row.role_id,
                "role_name": row.role_name,
                "description": row.role_description,
                "status_ind": row.role_status_ind,
            } if row.role_id else None,
            "chamber": {
                "chamber_id": row.chamber_id,
                "chamber_name": row.chamber_name,
            },
            "permissions": permissions,
        }

    # ─────────────────────────────────────────────────────────────────────────
    # Paginated List (Returns raw dicts, NOT DTOs)
    # ─────────────────────────────────────────────────────────────────────────

    async def list_users_paginated(
        self,
        session: AsyncSession,
        page: int,
        limit: int,
        chamber_id: str,
        search: Optional[str] = None,
    ) -> Tuple[List[Dict[str, Any]], int]:
        """
        Paginated users for a chamber with role.
        Returns list of dicts for service to transform into DTOs.
        """
        stmt = (
            select(
                Users.user_id,
                func.concat(Users.first_name, " ", func.coalesce(Users.last_name, "")).label("full_name"),
                Users.first_name,
                Users.last_name,
                Users.email,
                Users.phone,
                Users.status_ind,
                Users.created_date,
                ChamberRoles.role_id,
                ChamberRoles.role_name,
                ChamberRoles.description.label("role_description"),
                ChamberRoles.status_ind.label("role_status_ind"),
                UserProfiles.header_color,
                UserProfiles.sidebar_color,
                UserProfiles.primary_color,
                UserProfiles.font_family,
                Chamber.chamber_name,
            )
            .join(UserChamberLink, Users.user_id == UserChamberLink.user_id)
            .outerjoin(
                UserRoles,
                and_(
                    UserChamberLink.link_id == UserRoles.link_id,
                    UserRoles.end_date.is_(None),
                ),
            )
            .outerjoin(ChamberRoles, UserRoles.chamber_role_id == ChamberRoles.role_id)
            .outerjoin(UserProfiles, Users.user_id == UserProfiles.user_id)
            .join(Chamber, UserChamberLink.chamber_id == Chamber.chamber_id)
            .where(
                Users.is_deleted.is_(False),
                UserChamberLink.chamber_id == chamber_id,
                UserChamberLink.left_date.is_(None),
                UserChamberLink.status_ind.is_(True),
            )
        )

        if search and search.strip():
            kw = f"%{search.strip()}%"
            stmt = stmt.where(
                or_(
                    Users.first_name.ilike(kw),
                    Users.last_name.ilike(kw),
                    Users.email.ilike(kw),
                    Users.phone.ilike(kw),
                    ChamberRoles.role_name.ilike(kw),
                )
            )

        # Count before pagination
        count_stmt = select(func.count()).select_from(stmt.order_by(None).subquery())
        count_result = await session.execute(count_stmt)
        total_records: int = count_result.scalar_one() or 0

        stmt = stmt.order_by(Users.user_id.desc()).offset((page - 1) * limit).limit(limit)

        result = await session.execute(stmt)
        rows = result.all()

        # Return raw dicts for service to transform
        users = [
            {
                "user_id": row.user_id,
                "full_name": (row.full_name or "").strip(),
                "first_name": row.first_name or "",
                "last_name": row.last_name or "",
                "email": row.email,
                "phone": row.phone,
                "status_ind": row.status_ind,
                "created_date": row.created_date,
                "role": {
                    "role_id": row.chamber_role_id,
                    "role_name": row.role_name,
                    "description": row.role_description,
                    "status_ind": row.role_status_ind,
                } if row.chamber_role_id else None,
                "profile": {
                    "header_color": row.header_color,
                    "sidebar_color": row.sidebar_color,
                    "primary_color": row.primary_color,
                    "font_family": row.font_family,
                } if row.header_color else None,
                "chamber_name": row.chamber_name,
            }
            for row in rows
        ]

        return users, total_records

    # ─────────────────────────────────────────────────────────────────────────
    # Helper Methods
    # ─────────────────────────────────────────────────────────────────────────

    async def exists_by_email(self, session: AsyncSession, email: str) -> bool:
        """Check if a user exists globally by email."""
        user = await self.get_first(session, filters={Users.email: email})
        return user is not None

    async def get_user_with_profile_and_role(
        self,
        session: AsyncSession,
        *,
        email: Optional[str] = None,
        user_id: Optional[str] = None,
        chamber_id: Optional[str] = None,
    ) -> Optional[Tuple[Users, Optional[UserProfiles], Optional[ChamberRoles]]]:
        """
        Return (user, profile, role) tuple.
        When chamber_id is provided, resolves role through user_chamber_link → user_roles.
        """
        if not email and not user_id:
            raise ValueError("Either email or user_id must be provided")

        if chamber_id:
            stmt = (
                select(Users, UserProfiles, ChamberRoles)
                .outerjoin(UserProfiles, Users.user_id == UserProfiles.user_id)
                .join(UserChamberLink, Users.user_id == UserChamberLink.user_id)
                .outerjoin(
                    UserRoles,
                    and_(
                        UserChamberLink.link_id == UserRoles.link_id,
                        UserRoles.end_date.is_(None),
                    ),
                )
                .outerjoin(ChamberRoles, ChamberRoles.role_id == UserRoles.chamber_role_id)
                .where(
                    Users.is_deleted.is_(False),
                    Users.status_ind.is_(True),
                    UserChamberLink.chamber_id == chamber_id,
                    UserChamberLink.left_date.is_(None),
                    UserChamberLink.status_ind.is_(True),
                )
            )
        else:
            stmt = (
                select(Users, UserProfiles, ChamberRoles)
                .outerjoin(UserProfiles, Users.user_id == UserProfiles.user_id)
                .outerjoin(UserChamberLink, Users.user_id == UserChamberLink.user_id)
                .outerjoin(
                    UserRoles,
                    and_(
                        UserChamberLink.link_id == UserRoles.link_id,
                        UserRoles.end_date.is_(None),
                    ),
                )
                .outerjoin(ChamberRoles, ChamberRoles.role_id == UserRoles.chamber_role_id)
                .where(
                    Users.is_deleted.is_(False),
                    Users.status_ind.is_(True),
                )
            )

        if email:
            stmt = stmt.where(Users.email == email)
        else:
            stmt = stmt.where(Users.user_id == user_id)

        self._log_stmt(stmt, session)
        res = await session.execute(stmt)
        row = res.first()
        if not row:
            return None
        return row.tuple()
    
    async def update_deleted_user(
        self,
        session: AsyncSession,
        user_id: str,
        data: Dict[str, Any],
    ) -> None:
        """
        Update a soft-deleted user (bypasses soft-delete filtering).
        Used for reactivation scenarios.
        """
        from sqlalchemy import update
        
        stmt = (
            update(Users)
            .where(Users.user_id == user_id)
            .values(**data)
        )
        
        await session.execute(stmt)
        await session.flush()

    async def reactivate_deleted_user(
        self,
        session: AsyncSession,
        user_id: str,
        current_user_id: str,
    ) -> None:
        """
        Undelete a user (bypasses soft-delete filtering in BaseRepository.update()).
        Used for reactivating deleted users who are being re-added to a chamber.
        """
        from sqlalchemy import update
        
        stmt = (
            update(Users)
            .where(Users.user_id == user_id)
            .values(
                is_deleted=False,
                deleted_date=None,
                deleted_by=None,
                status_ind=True,
                updated_by=current_user_id,
                updated_date=datetime.now(),
            )
        )
        
        await session.execute(stmt)
        await session.flush()

    async def get_user_stats(
        self,
        session: AsyncSession,
        chamber_id: str,
    ) -> Dict[str, int]:
        """
        Get user management statistics for a chamber.
        Returns dict with total_users, active_users, total_roles, pending_invites.
        """
        # 1. Total users in chamber (all time, including left)
        total_users_stmt = select(func.count(func.distinct(UserChamberLink.user_id))).where(
            UserChamberLink.chamber_id == chamber_id
        )
        total_users_result = await session.execute(total_users_stmt)
        total_users = total_users_result.scalar_one() or 0

        # 2. Active users in chamber (not left, status_ind=True)
        active_users_stmt = select(func.count(func.distinct(UserChamberLink.user_id))).where(
            and_(
                UserChamberLink.chamber_id == chamber_id,
                UserChamberLink.left_date.is_(None),
                UserChamberLink.status_ind.is_(True),
            )
        )
        active_users_result = await session.execute(active_users_stmt)
        active_users = active_users_result.scalar_one() or 0

        # 3. Total roles defined for chamber (via user_roles)
        total_roles_stmt = select(func.count(func.distinct(UserRoles.chamber_role_id))).join(
            UserChamberLink,
            UserChamberLink.link_id == UserRoles.link_id
        ).where(
            and_(
                UserChamberLink.chamber_id == chamber_id,
                UserChamberLink.left_date.is_(None),
                UserChamberLink.status_ind.is_(True),
                UserRoles.end_date.is_(None),
            )
        )
        total_roles_result = await session.execute(total_roles_stmt)
        total_roles = total_roles_result.scalar_one() or 0

        # 4. Pending invitations
        pending_invites_stmt = select(func.count(UserInvitations.invitation_id)).where(
            and_(
                UserInvitations.chamber_id == chamber_id,
                UserInvitations.status_code == 'PN',
            )
        )
        pending_invites_result = await session.execute(pending_invites_stmt)
        pending_invites = pending_invites_result.scalar_one() or 0

        return {
            "total_users": total_users,
            "active_users": active_users,
            "total_roles": total_roles,
            "pending_invites": pending_invites,
        }