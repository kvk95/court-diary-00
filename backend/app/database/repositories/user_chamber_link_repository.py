# app/database/repositories/user_chamber_link_repository.py

from typing import Optional, List
from datetime import date
from sqlalchemy import and_, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.models.user_chamber_link import UserChamberLink
from app.database.repositories.base.base_repository import BaseRepository
from app.database.repositories.base.repo_context import apply_repo_context


@apply_repo_context
class UserChamberLinkRepository(BaseRepository[UserChamberLink]):
    """Repository for UserChamberLink model."""

    def __init__(self):
        super().__init__(UserChamberLink)

    async def get_active_link(
        self,
        session: AsyncSession,
        user_id: str,
        chamber_id: str,
    ) -> Optional[UserChamberLink]:
        """Get active user_chamber_link for user in chamber."""
        return await self.get_first(
            session=session,
            filters={
                UserChamberLink.user_id: user_id,
                UserChamberLink.chamber_id: chamber_id,
            },
            where=[
                UserChamberLink.left_date.is_(None),
                UserChamberLink.status_ind.is_(True),
            ]
        )

    async def get_link_for_user_chamber(
        self,
        session: AsyncSession,
        user_id: str,
        chamber_id: str,
    ) -> Optional[UserChamberLink]:
        """
        Get ANY link for user+chamber (active or inactive).
        ✅ Used to check if link exists before creating new one.
        """
        return await self.get_first(
            session=session,
            filters={
                UserChamberLink.user_id: user_id,
                UserChamberLink.chamber_id: chamber_id,
            },
        )

    async def reactivate_chamber_link(
        self,
        session: AsyncSession,
        link_id: str,
        current_user_id: str,
    ) -> None:
        """
        Reactivate a previously deleted chamber link.
        ✅ Sets left_date=NULL, status_ind=TRUE (bypasses soft-delete filtering).
        """
        from sqlalchemy import update
        
        stmt = (
            update(UserChamberLink)
            .where(UserChamberLink.link_id == link_id)
            .values(
                left_date=None,
                status_ind=True,
                updated_by=current_user_id,
                updated_date=date.today(),
            )
        )
        
        await session.execute(stmt)
        await session.flush()

    async def get_all_active_links_for_user(
        self,
        session: AsyncSession,
        user_id: str,
    ) -> List[UserChamberLink]:
        """Get all active chamber links for a user."""
        return await self.list_all(
            session=session,
            filters={UserChamberLink.user_id: user_id},
            where=[
                UserChamberLink.left_date.is_(None),
                UserChamberLink.status_ind.is_(True),
            ]
        )
    
    async def unlink_user_from_chamber(
        self,
        session: AsyncSession,
        user_id: str,
        chamber_id: str,
        current_user_id: str,
    ) -> None:
        """
        Unlink user from a specific chamber (set left_date and status_ind=False).
        ✅ Uses direct SQL to bypass soft-delete filtering in BaseRepository.update().
        """
        from sqlalchemy import update
        
        stmt = (
            update(UserChamberLink)
            .where(
                and_(
                    UserChamberLink.user_id == user_id,
                    UserChamberLink.chamber_id == chamber_id,
                    UserChamberLink.left_date.is_(None),
                )
            )
            .values(
                left_date=date.today(),
                status_ind=False,
                updated_by=current_user_id,
                updated_date=date.today(),
            )
        )
        
        await session.execute(stmt)
        await session.flush()

    async def unlink_user_from_all_chambers(
        self,
        session: AsyncSession,
        user_id: str,
        current_user_id: str,
    ) -> None:
        """Unlink user from all chambers."""
        stmt = (
            update(UserChamberLink)
            .where(
                and_(
                    UserChamberLink.user_id == user_id,
                    UserChamberLink.left_date.is_(None),
                    UserChamberLink.status_ind.is_(True),
                )
            )
            .values(
                left_date=date.today(),
                status_ind=False,
                updated_by=current_user_id,
                updated_date=date.today(),
            )
        )
        
        await session.execute(stmt)
        await session.flush()

    async def create_chamber_link(
        self,
        session: AsyncSession,
        user_id: str,
        chamber_id: str,
        primary_ind: bool,
        created_by: str,
    ) -> UserChamberLink:
        """Create a new user-chamber link."""
        return await self.create(
            session=session,
            data={
                "user_id": user_id,
                "chamber_id": chamber_id,
                "primary_ind": primary_ind,
                "joined_date": date.today(),
                "status_ind": True,
                "created_by": created_by,
            },
        )

    async def get_primary_link(
        self,
        session: AsyncSession,
        user_id: str,
    ) -> Optional[UserChamberLink]:
        """Get user's primary chamber link."""
        return await self.get_first(
            session=session,
            filters={
                UserChamberLink.user_id: user_id,
                UserChamberLink.primary_ind: True,
            },
            where=[
                UserChamberLink.left_date.is_(None),
                UserChamberLink.status_ind.is_(True),
            ]
        )