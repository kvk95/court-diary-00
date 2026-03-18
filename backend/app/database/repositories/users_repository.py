from typing import List, Optional, Tuple

from sqlalchemy import and_, func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.models.security_roles import SecurityRoles
from app.database.models.user_profiles import UserProfiles
from app.database.models.user_roles import UserRoles
from app.database.models.users import Users
from app.database.models.user_chamber_link import UserChamberLink
from app.database.repositories.base.base_repository import BaseRepository
from app.dtos.users_dto import UserOut
from app.database.repositories.base.repo_context import apply_repo_context

@apply_repo_context
class UsersRepository(BaseRepository[Users]):
    """
    Repository for Users model.
    Provides login checks, existence checks, and paginated listing.
    """

    def __init__(self):
        super().__init__(Users)

    async def list_users_paginated(
        self,
        session: AsyncSession,
        page: int,
        limit: int,
        chamber_id: int,  # ✅ Changed from company_id
        search: Optional[str] = None,
    ) -> Tuple[List[UserOut], int]:
        """
        Return paginated users for a chamber, with optional search.
        """
        stmt = (
            select(
                Users.user_id,
                func.concat(Users.first_name, " ", Users.last_name).label("full_name"),
                Users.first_name,
                Users.last_name,
                Users.email,
                Users.phone,
                SecurityRoles.role_id,
                SecurityRoles.role_name,
                Users.status_ind,
            )
            .outerjoin(UserRoles, Users.user_id == UserRoles.user_id)
            .outerjoin(SecurityRoles, UserRoles.role_id == SecurityRoles.role_id)
            .where(
                and_(
                    Users.is_deleted.is_(False),
                    Users.status_ind == True,
                )
            )
        )

        # ✅ Filter by chamber via user_chamber_links (if using link table)
        # OR directly if users.chamber_id exists
        stmt = stmt.join(UserChamberLink, Users.user_id == UserChamberLink.user_id).where(
            UserChamberLink.chamber_id == chamber_id,
            UserChamberLink.left_date == None,
            UserChamberLink.status_ind == True
        )

        # Apply search filter if provided
        if search:
            search_pattern = f"%{search}%"
            stmt = stmt.where(
                or_(
                    func.concat(Users.first_name, " ", Users.last_name).ilike(search_pattern),
                    Users.email.ilike(search_pattern),
                    Users.phone.ilike(search_pattern),
                    SecurityRoles.role_name.ilike(search_pattern),
                )
            )

        # Count total records
        count_stmt = select(func.count()).select_from(stmt.subquery())
        count_result = await session.execute(count_stmt)
        total_records: int = count_result.scalar_one()

        # Apply ordering, offset, and limit
        stmt = stmt.order_by(Users.user_id.desc()).offset((page - 1) * limit).limit(limit)

        result = await session.execute(stmt)
        rows = result.all()

        users = [
            UserOut(
                user_id=row.user_id,
                full_name=row.full_name or "",
                first_name=row.first_name or "",
                last_name=row.last_name or "",
                email=row.email or "",
                phone=row.phone or "",
                role_id=row.role_id,
                role_name=row.role_name,
                status_ind=row.status_ind,
                image="/assets/images/avatar/none.png",  # ✅ Default (no image column)
            )
            for row in rows
        ]

        return users, total_records

    async def exists_by_email(self, session: AsyncSession, email: str) -> bool:
        """Check if a user exists by email."""
        user = await self.get_first(session, filters={Users.email: email})
        return user is not None

    async def get_user_with_profile_and_role(
        self,
        session: AsyncSession,
        *,
        email: Optional[str] = None,
        user_id: Optional[int] = None,
        chamber_id: Optional[int] = None,  # ✅ NEW: Resolve role per chamber
    ) -> Optional[Tuple[Users, Optional[UserProfiles], Optional[SecurityRoles]]]:
        """
        Return (user, profile, role) with joins.
        If chamber_id is provided, resolves role for that specific chamber context.
        """
        if not email and not user_id:
            raise ValueError("Either email or user_id must be provided")

        # ✅ If chamber_id provided, join through user_chamber_links → user_roles
        if chamber_id:
            stmt = (
                select(Users, UserProfiles, SecurityRoles)
                .outerjoin(UserProfiles, Users.user_id == UserProfiles.user_id)
                .join(UserChamberLink, Users.user_id == UserChamberLink.user_id)
                .join(UserRoles, UserChamberLink.link_id == UserRoles.link_id)  # ✅ Via link_id
                .outerjoin(SecurityRoles, SecurityRoles.role_id == UserRoles.role_id)
                .where(
                    Users.is_deleted.is_(False),
                    Users.status_ind == True,
                    UserChamberLink.chamber_id == chamber_id,
                    UserChamberLink.left_date == None,
                    UserChamberLink.status_ind == True,
                    UserRoles.end_date == None,
                )
            )
        else:
            # ✅ Fallback: Direct user_roles join (if not using link table yet)
            stmt = (
                select(Users, UserProfiles, SecurityRoles)
                .outerjoin(UserProfiles, Users.user_id == UserProfiles.user_id)
                .outerjoin(UserRoles, UserRoles.user_id == Users.user_id)
                .outerjoin(SecurityRoles, SecurityRoles.role_id == UserRoles.role_id)
                .where(
                    Users.is_deleted.is_(False),
                    Users.status_ind == True,
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

    async def get_by_email_with_chamber(
        self,
        session: AsyncSession,
        email: str,
        chamber_id: int,  # ✅ Required for contextual membership
    ) -> Optional[Users]:
        """
        Get user by email, validated for a specific chamber.
        Returns None if user is not a member of this chamber.
        """
        stmt = (
            select(Users)
            .join(UserChamberLink, Users.user_id == UserChamberLink.user_id)
            .where(
                Users.email == email,
                Users.is_deleted.is_(False),
                Users.status_ind == True,
                UserChamberLink.chamber_id == chamber_id,
                UserChamberLink.left_date == None,
                UserChamberLink.status_ind == True,
            )
        )
        result = await session.execute(stmt)
        return result.scalar_one_or_none()