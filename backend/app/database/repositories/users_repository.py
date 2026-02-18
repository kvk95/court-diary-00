from typing import List, Optional, Tuple

from sqlalchemy import and_, func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.models.security_roles import SecurityRoles
from app.database.models.user_profiles import UserProfiles
from app.database.models.user_roles import UserRoles
from app.database.models.users import Users
from app.database.repositories.base.base_repository import BaseRepository
from app.dtos.users_dto import UserOut
from app.database.repositories.base.repo_context import apply_repo_context

@apply_repo_context
class UsersRepository(BaseRepository[Users]):
    """
    Repository for Users model.
    Provides login checks, existence checks, and paginated listing.
    All queries use strict column-object filters and validated CRUD helpers.
    """

    def __init__(self):
        super().__init__(Users)

    async def check_login_async(
        self, session: AsyncSession, email: str
    ) -> Optional[Users]:
        """
        Return user by email, only if active and not deleted.
        Uses filters for equality and where for status check.
        """
        return await self.get_first(
            session,
            filters={Users.email: email},
            where=[Users.status_ind.__eq__(True)],
        )

    async def list_users_paginated(
        self,
        session: AsyncSession,
        page: int,
        limit: int,
        company_id: int,
        search: Optional[str] = None,
    ) -> Tuple[List[UserOut], int]:
        """
        Return paginated users for a company, with optional search across username, email, first_name, last_name.
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
                Users.image,
            )
            .outerjoin(UserRoles, Users.user_id == UserRoles.user_id)
            .outerjoin(SecurityRoles, UserRoles.role_id == SecurityRoles.role_id)
            .where(
                and_(
                    Users.is_deleted.is_(False),
                    Users.company_id == company_id,
                )
            )
        )

        stmt = stmt.where(Users.company_id == company_id)
        # Apply search filter if provided
        if search:
            search_pattern = f"%{search}%"
            stmt = stmt.where(
                or_(
                    func.concat(Users.first_name, " ", Users.last_name).ilike(
                        search_pattern
                    ),
                    Users.email.ilike(search_pattern),
                    Users.phone.ilike(search_pattern),
                    SecurityRoles.role_name.ilike(search_pattern),
                )
            )

        # Count total records (for pagination metadata)
        count_stmt = stmt.with_only_columns(func.count()).order_by(None)
        count_result = await session.execute(count_stmt)
        total_records: int = count_result.scalar_one()

        # Apply ordering, offset, and limit for pagination
        stmt = (
            stmt.order_by(Users.user_id.desc()).offset((page - 1) * limit).limit(limit)
        )

        result = await session.execute(stmt)
        rows = result.all()

        # Convert rows to UserOut Pydantic models
        users = [
            UserOut(
                user_id=row.user_id,
                full_name=row.full_name or "",
                first_name=row.first_name or "",
                last_name=row.last_name or "",
                email=row.email or "",
                phone=row.phone or "",
                role_id=row.role_id,  # Make sure Pydantic model allows None
                role_name=row.role_name,
                status_ind=row.status_ind,
                image=row.image or "/assets/images/avathar/none.png",
            )
            for row in rows
        ]

        return users, total_records

    async def exists_by_email(self, session: AsyncSession, email: str) -> bool:
        """
        Check if a user exists by email.
        """
        user = await self.get_first(session, filters={Users.email: email})
        return user is not None

    async def get_user_with_profile_and_role(
        self,
        session: AsyncSession,
        *,
        email: Optional[str] = None,
        user_id: Optional[int] = None,
    ) -> Optional[Tuple[Users, Optional[UserProfiles], Optional[SecurityRoles]]]:
        """
        Return (user, profile, role) with joins.
        Exactly one of email or user_id must be provided.
        Applies soft-delete and active status filters.
        """
        if not email and not user_id:
            raise ValueError("Either email or user_id must be provided")

        stmt = (
            select(Users, UserProfiles, SecurityRoles)
            .outerjoin(UserProfiles, Users.user_id == UserProfiles.user_id)
            .outerjoin(UserRoles, UserRoles.user_id == Users.user_id)
            .outerjoin(SecurityRoles, SecurityRoles.role_id == UserRoles.role_id)
            .where(
                Users.is_deleted.is_(False),
                Users.status_ind.__eq__(True),
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
