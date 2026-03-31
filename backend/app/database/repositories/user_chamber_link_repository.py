# app/database/repositories/user_chamber_link_repository.py

from typing import Optional, List
from datetime import date
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
    ) -> None:
        await self.update(
            session=session,
            where=[
                UserChamberLink.user_id == user_id,
                UserChamberLink.chamber_id == chamber_id,
                UserChamberLink.left_date.is_(None),
            ],
            data={
                "left_date": date.today(),
                "status_ind": False,
            },
        )

    async def unlink_user_from_all_chambers(
        self,
        session: AsyncSession,
        user_id: str,
    ) -> None:
        await self.update(
            session=session,
            where=[
                UserChamberLink.user_id == user_id,
                UserChamberLink.left_date.is_(None),
                UserChamberLink.status_ind.is_(True),
            ],
            data={
                "left_date": date.today(),
                "status_ind": False,
            },
        )

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