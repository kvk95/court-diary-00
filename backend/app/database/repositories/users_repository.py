# app/database/repositories/users_repository.py

from typing import List, Optional, Tuple, Dict, Any
from sqlalchemy import and_, func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.models.chamber_roles import ChamberRoles
from app.database.models.login_audit import LoginAudit
from app.database.models.profile_images import ProfileImages
from app.database.models.refm_login_status import RefmLoginStatusConstants
from app.database.models.user_chamber_link import UserChamberLink
from app.database.models.user_profiles import UserProfiles
from app.database.models.user_roles import UserRoles
from app.database.models.users import Users
from app.database.models.chamber import Chamber
from app.database.repositories.base.base_repository import BaseRepository
from app.database.repositories.role_permissions_repository import RolePermissionsRepository
from app.database.repositories.base.repo_context import apply_repo_context
from app.utils.constants import SUPERADMIN_ROLE_CODE


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
        
        latest_login_subq = (
            select(
                LoginAudit.actor_user_id.label("user_id"),
                func.max(LoginAudit.login_time).label("last_login_time"),
            )
            .where(
                    LoginAudit.status_code == RefmLoginStatusConstants.SUCCESS,                
                    LoginAudit.actor_chamber_id == chamber_id, 
                )
            .group_by(LoginAudit.actor_user_id)
            .subquery()
        )

        # Build base query with all joins
        stmt = (
            select(
                # User fields
                Users.user_id,
                Users.first_name,
                Users.last_name,
                Users.email,
                Users.phone,
                Users.advocate_ind,
                latest_login_subq.c.last_login_time,
                UserChamberLink.status_ind,
                Users.created_date,
                # Profile fields
                UserProfiles.profile_id,
                UserProfiles.header_color,
                UserProfiles.sidebar_color,
                UserProfiles.primary_color,
                UserProfiles.font_family,
                # Role fields
                ChamberRoles.role_id,
                ChamberRoles.role_code,
                ChamberRoles.role_name,
                ChamberRoles.description.label("role_description"),
                ChamberRoles.status_ind.label("role_status_ind"),
                ChamberRoles.admin_ind,
                # Chamber fields
                Chamber.chamber_id,
                Chamber.chamber_name,
                ProfileImages.image_id,
                ProfileImages.image_data,
            )
            .join(
                UserChamberLink,
                and_(
                    Users.user_id == UserChamberLink.user_id,
                    UserChamberLink.chamber_id == chamber_id,
                    UserChamberLink.left_date.is_(None),
                )
            )
            .outerjoin(UserProfiles, Users.user_id == UserProfiles.user_id)
            .outerjoin(ProfileImages, 
                       and_( Users.user_id == ProfileImages.user_id,
                            ProfileImages.deleted_ind.is_(False),
                            ProfileImages.deleted_date.is_(None)
                            )
                       )
            .outerjoin(
                UserRoles,
                and_(
                    UserChamberLink.link_id == UserRoles.link_id,
                    UserRoles.end_date.is_(None),
                )
            )
            .outerjoin(ChamberRoles, UserRoles.role_id == ChamberRoles.role_id)
            .outerjoin(
                latest_login_subq,
                Users.user_id == latest_login_subq.c.user_id,
            )
            .join(Chamber, UserChamberLink.chamber_id == Chamber.chamber_id)
            .where(Users.deleted_ind.is_(False))
        )

        if user_id:
            stmt = stmt.where(Users.user_id == user_id)
        else:
            stmt = stmt.where(Users.email == email)

        self._log_stmt(stmt, session)
        result = await self.execute( session=session, stmt=stmt)
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
            "advocate_ind":row.advocate_ind,
            "super_admin_ind": row.role_code == SUPERADMIN_ROLE_CODE,
            "created_date": row.created_date,
            "image_id":row.image_id,
            "image_data":row.image_data,
            "last_login_time": row.last_login_time,
            "profile": {
                "header_color": row.header_color,
                "sidebar_color": row.sidebar_color,
                "primary_color": row.primary_color,
                "font_family": row.font_family,
            } if row.profile_id else None,
            "role": {
                "role_id": row.role_id,
                "role_code": row.role_code,
                "role_name": row.role_name,
                "description": row.role_description,
                "status_ind": row.role_status_ind,
                "admin_ind": row.admin_ind,
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
        role_code: Optional[str] = None,
        search: Optional[str] = None,
        status_ind: Optional[bool]=None,
    ) -> Tuple[List[Dict[str, Any]], int]:
        """
        Paginated users for a chamber with role.
        Returns list of dicts for service to transform into DTOs.
        """

        latest_login_subq = (
            select(
                LoginAudit.actor_user_id.label("user_id"),
                func.max(LoginAudit.login_time).label("last_login_time"),
            )
            .where(
                    LoginAudit.status_code == RefmLoginStatusConstants.SUCCESS,                
                    LoginAudit.actor_chamber_id == chamber_id, 
                )
            .group_by(LoginAudit.actor_user_id)
            .subquery()
        )

        stmt = (
            select(
                Users.user_id,
                func.concat(Users.first_name, " ", func.coalesce(Users.last_name, "")).label("full_name"),
                Users.first_name,
                Users.last_name,
                Users.email,
                Users.phone,
                Users.advocate_ind,
                UserChamberLink.status_ind,
                Users.created_date,
                ChamberRoles.role_id,
                ChamberRoles.role_code,
                ChamberRoles.role_name,
                ChamberRoles.description.label("role_description"),
                ChamberRoles.status_ind.label("role_status_ind"),
                ChamberRoles.admin_ind,
                UserProfiles.header_color,
                UserProfiles.sidebar_color,
                UserProfiles.primary_color,
                UserProfiles.font_family,
                Chamber.chamber_name,
                ProfileImages.image_id,
                ProfileImages.image_data,
                latest_login_subq.c.last_login_time,
            )
            .join(UserChamberLink, Users.user_id == UserChamberLink.user_id)
            .outerjoin(ProfileImages, Users.user_id == ProfileImages.user_id)
            .outerjoin(
                UserRoles,
                and_(
                    UserChamberLink.link_id == UserRoles.link_id,
                    UserRoles.end_date.is_(None),
                ),
            )
            .outerjoin(ChamberRoles, UserRoles.role_id == ChamberRoles.role_id)
            .outerjoin(UserProfiles, Users.user_id == UserProfiles.user_id)
            .outerjoin(
                latest_login_subq,
                Users.user_id == latest_login_subq.c.user_id,
            )
            .join(Chamber, UserChamberLink.chamber_id == Chamber.chamber_id)
            .where(
                Users.deleted_ind.is_(False),
                UserChamberLink.chamber_id == chamber_id,
                UserChamberLink.left_date.is_(None),
            )
        )

        if role_code and role_code.strip():
            stmt = stmt.where( ChamberRoles.role_code == role_code.strip() )

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

        if status_ind is not None:
            stmt = stmt.where(UserChamberLink.status_ind.is_(status_ind))

        # Count before pagination
        count_stmt = select(func.count()).select_from(stmt.order_by(None).subquery())
        count_result = await self.execute(session=session,stmt=count_stmt)
        total_records: int = count_result.scalar_one() or 0

        stmt = stmt.order_by(Users.user_id.desc()).offset((page - 1) * limit).limit(limit)

        result = await self.execute(session=session,stmt=stmt)
        
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
                "super_admin_ind": row.role_code == SUPERADMIN_ROLE_CODE,
                "status_ind": row.status_ind,
                "advocate_ind": row.advocate_ind,
                "created_date": row.created_date,
                "image_id": row.image_id,
                "image_data": row.image_data,
                "last_login_time": row.last_login_time,
                "role": {
                    "role_id": row.role_id,
                    "role_code": row.role_code,
                    "role_name": row.role_name,
                    "description": row.role_description,
                    "status_ind": row.role_status_ind,
                    "admin_ind": row.admin_ind,
                } if row.role_id else None,
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
                .outerjoin(ChamberRoles, ChamberRoles.role_id == UserRoles.role_id)
                .where(
                    Users.deleted_ind.is_(False),
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
                .outerjoin(ChamberRoles, ChamberRoles.role_id == UserRoles.role_id)
                .where(
                    Users.deleted_ind.is_(False),
                    Users.status_ind.is_(True),
                )
            )

        if email:
            stmt = stmt.where(Users.email == email)
        else:
            stmt = stmt.where(Users.user_id == user_id)

        self._log_stmt(stmt, session)
        res = await self.execute( session=session, stmt=stmt)
        row = res.first()
        if not row:
            return None
        return row.tuple()

    async def reactivate_deleted_user(
        self,
        session: AsyncSession,
        user_id: str,
        status_ind:bool = False
    ) -> None:
        await self.bulk_update(
            session=session,
            where=[
                Users.user_id == user_id,
                Users.deleted_ind.is_(True),
            ],
            data={
                "deleted_ind": False,
                "deleted_date": None,
                "deleted_by": None,
                "status_ind": status_ind, # Activate user using email
            },
        )

    async def get_user_stats(
        self,
        session: AsyncSession,
        chamber_id: str,
    ) -> Dict[str, int]:
        """
        Get user management statistics for a chamber.
        Returns dict with total_users, active_users, total_roles.
        """
        # 1. Total users linked to this chamber (including historical)
        total_users_stmt = select(
            func.count(func.distinct(UserChamberLink.user_id))
        ).where(
            UserChamberLink.chamber_id == chamber_id
        )

        total_users = await self.execute_scalar(
            session=session, stmt=total_users_stmt, default=0
        )

        # 2. Active users (currently linked and active)
        active_users_stmt = select(
            func.count(func.distinct(UserChamberLink.user_id))
        ).where(
            and_(
                UserChamberLink.chamber_id == chamber_id,
                UserChamberLink.left_date.is_(None),
                UserChamberLink.status_ind.is_(True),
                # Optional: exclude deleted users
                # Users.status_ind.is_(True),   # if you join with Users
            )
        )

        active_users = await self.execute_scalar(
            session=session, stmt=active_users_stmt, default=0
        )

        # 3. Total unique roles currently assigned in this chamber
        total_roles_stmt = (
            select(func.count(func.distinct(UserRoles.role_id)))
            .join(
                UserChamberLink,
                UserChamberLink.link_id == UserRoles.link_id
            )
            .where(
                and_(
                    UserChamberLink.chamber_id == chamber_id,
                    UserChamberLink.left_date.is_(None),
                    UserChamberLink.status_ind.is_(True),
                    UserRoles.end_date.is_(None),
                )
            )
        )

        total_roles = await self.execute_scalar(
            session=session, stmt=total_roles_stmt, default=0
        )

        return {
            "total_users": total_users,
            "active_users": active_users,
            "total_roles": total_roles,        # or "roles_count" to match other methods
        }