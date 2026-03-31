
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.repositories.base.repo_context import apply_repo_context
from app.database.repositories.base.base_repository import BaseRepository
from app.database.models.profile_images import ProfileImages

@apply_repo_context
class ProfileImagesRepository(BaseRepository[ProfileImages]):
    def __init__(self):
        super().__init__(ProfileImages)

    async def get_profile_image_by_user(
        self,
        session: AsyncSession,
        user_id: str,
    ):
        result = await self.execute(
            session=session,
            stmt=select(ProfileImages).where(
                ProfileImages.user_id == user_id
            ),
        )

        img = result.scalars().first()

        if not img:
            return None

        return {
            "image_id": img.image_id,
            "image_data": img.image_data,
        }
    
    async def get_images_by_user_ids(
        self,
        session: AsyncSession,
        user_ids: list[str],
    ):
        result = await self.execute(
            session=session,
            stmt=select(
                ProfileImages.user_id,
                ProfileImages.image_id,
                ProfileImages.image_data,
            ).where(
                ProfileImages.user_id.in_(user_ids)
            ),
        )

        rows = result.all()

        return {
            r.user_id: {
                "image_id": r.image_id,
                "image_data": r.image_data,
            }
            for r in rows
        }

    async def get_profile_image_by_clientid(
        self,
        session: AsyncSession,
        client_id: str,
    ):
        result = await self.execute(
            session=session,
            stmt=select(ProfileImages).where(
                ProfileImages.client_id == client_id
            ),
        )

        img = result.scalars().first()
        
        if not img:
            return None

        return {
            "image_id": img.image_id,
            "image_data": img.image_data,
        }
    
    async def get_images_by_client_ids(
        self,
        session: AsyncSession,
        client_ids: list[str],
    ):
        result = await self.execute(
            session=session,
            stmt=select(
                ProfileImages.client_id,
                ProfileImages.image_id,
                ProfileImages.image_data,
            ).where(
                ProfileImages.client_id.in_(client_ids)
            ),
        )

        rows = result.all()

        return {
            r.client_id: {
                "image_id": r.image_id,
                "image_data": r.image_data,
            }
            for r in rows
        }
