from typing import List, Optional, Tuple

from sqlalchemy import and_, func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.models.security_roles import SecurityRoles
from app.database.models.user_chamber_link import UserChamberLink
from app.database.models.user_profiles import UserProfiles
from app.database.models.user_roles import UserRoles
from app.database.models.users import Users
from app.database.repositories.base.base_repository import BaseRepository
from app.database.repositories.base.repo_context import apply_repo_context
from app.dtos.users_dto import UserOut


@apply_repo_context
class UsersRepository(BaseRepository[Users]):
    """
    Repository for Users model.
    All chamber-scoped queries join through user_chamber_link.
    """

    def __init__(self):
        super().__init__(Users)

    async def list_users_paginated(
        self,
        session: AsyncSession,
        page: int,
        limit: int,
        chamber_id: int,
        search: Optional[str] = None,
    ) -> Tuple[List[UserOut], int]:
        """
        Paginated users for a chamber with role, filtered through user_chamber_link.
        Joins UserRoles via link_id (the correct contextual path).
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
                SecurityRoles.role_id,
                SecurityRoles.role_name,
            )
            .join(UserChamberLink, Users.user_id == UserChamberLink.user_id)
            .outerjoin(
                UserRoles,
                and_(
                    UserChamberLink.link_id == UserRoles.link_id,   # ✅ via link_id, not user_id
                    UserRoles.end_date.is_(None),
                ),
            )
            .outerjoin(SecurityRoles, UserRoles.role_id == SecurityRoles.role_id)
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
                    SecurityRoles.role_name.ilike(kw),
                )
            )

        # Count before pagination
        count_stmt = select(func.count()).select_from(stmt.order_by(None).subquery())
        count_result = await session.execute(count_stmt)
        total_records: int = count_result.scalar_one() or 0

        stmt = stmt.order_by(Users.user_id.desc()).offset((page - 1) * limit).limit(limit)

        result = await session.execute(stmt)
        rows = result.all()

        users = [
            UserOut(
                user_id=row.user_id,
                full_name=(row.full_name or "").strip(),
                first_name=row.first_name or "",
                last_name=row.last_name or "",
                email=row.email,
                phone=row.phone,
                status_ind=row.status_ind,
                role_id=row.role_id,
                role_name=row.role_name,
                created_date=row.created_date,
                image="/assets/images/avatar/none.png",
            )
            for row in rows
        ]

        return users, total_records

    async def exists_by_email(self, session: AsyncSession, email: str) -> bool:
        """Check if a user exists globally by email (email is unique across all chambers)."""
        user = await self.get_first(session, filters={Users.email: email})
        return user is not None

    async def get_user_with_profile_and_role(
        self,
        session: AsyncSession,
        *,
        email: Optional[str] = None,
        user_id: Optional[int] = None,
        chamber_id: Optional[int] = None,
    ) -> Optional[Tuple[Users, Optional[UserProfiles], Optional[SecurityRoles]]]:
        """
        Return (user, profile, role) tuple.
        When chamber_id is provided, resolves role through the correct
        user_chamber_link → user_roles path.
        """
        if not email and not user_id:
            raise ValueError("Either email or user_id must be provided")

        if chamber_id:
            stmt = (
                select(Users, UserProfiles, SecurityRoles)
                .outerjoin(UserProfiles, Users.user_id == UserProfiles.user_id)
                .join(UserChamberLink, Users.user_id == UserChamberLink.user_id)
                .outerjoin(                                          # ✅ link_id path
                    UserRoles,
                    and_(
                        UserChamberLink.link_id == UserRoles.link_id,
                        UserRoles.end_date.is_(None),
                    ),
                )
                .outerjoin(SecurityRoles, SecurityRoles.role_id == UserRoles.role_id)
                .where(
                    Users.is_deleted.is_(False),
                    Users.status_ind.is_(True),
                    UserChamberLink.chamber_id == chamber_id,
                    UserChamberLink.left_date.is_(None),
                    UserChamberLink.status_ind.is_(True),
                )
            )
        else:
            # Fallback: no chamber scoping (used internally, e.g. superadmin)
            stmt = (
                select(Users, UserProfiles, SecurityRoles)
                .outerjoin(UserProfiles, Users.user_id == UserProfiles.user_id)
                .outerjoin(UserChamberLink, Users.user_id == UserChamberLink.user_id)
                .outerjoin(
                    UserRoles,
                    and_(
                        UserChamberLink.link_id == UserRoles.link_id,
                        UserRoles.end_date.is_(None),
                    ),
                )
                .outerjoin(SecurityRoles, SecurityRoles.role_id == UserRoles.role_id)
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
