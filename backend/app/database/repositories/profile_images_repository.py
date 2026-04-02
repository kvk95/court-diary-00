from sqlalchemy.ext.asyncio import AsyncSession

from app.database.repositories.base.repo_context import apply_repo_context
from app.database.repositories.base.base_repository import BaseRepository
from app.database.models.profile_images import ProfileImages


@apply_repo_context
class ProfileImagesRepository(BaseRepository[ProfileImages]):
    def __init__(self):
        super().__init__(ProfileImages)

    # ---------------------------------------------
    # 🔹 INTERNAL MAPPER (reusable)
    # ---------------------------------------------
    @staticmethod
    def _map_image(img: ProfileImages) -> dict:
        return {
            "image_id": img.image_id,
            "image_data": img.image_data,
        }

    # ---------------------------------------------
    # 🔹 SINGLE FETCH (USER)
    # ---------------------------------------------
    async def get_profile_image_by_user_id(
        self,
        session: AsyncSession,
        user_id: str,
    ):
        img = await self.get_first(
            session=session,
            filters={
                ProfileImages.user_id: user_id,
            },
        )

        return self._map_image(img) if img else None

    # ---------------------------------------------
    # 🔹 MULTI FETCH (USER)
    # ---------------------------------------------
    async def get_images_by_user_ids(
        self,
        session: AsyncSession,
        user_ids: list[str],
    ):
        if not user_ids:
            return {}

        rows = await self.list_all(
            session=session,
            where=[
                ProfileImages.user_id.in_(user_ids),
            ],
        )

        return {
            r.user_id: self._map_image(r)
            for r in rows
        }

    # ---------------------------------------------
    # 🔹 SINGLE FETCH (CLIENT)
    # ---------------------------------------------
    async def get_profile_image_by_clientid(
        self,
        session: AsyncSession,
        client_id: str,
    ):
        img = await self.get_first(
            session=session,
            filters={
                ProfileImages.client_id: client_id,
            },
        )

        return self._map_image(img) if img else None

    # ---------------------------------------------
    # 🔹 MULTI FETCH (CLIENT)
    # ---------------------------------------------
    async def get_images_by_client_ids(
        self,
        session: AsyncSession,
        client_ids: list[str],
    ):
        if not client_ids:
            return {}

        rows = await self.list_all(
            session=session,
            where=[
                ProfileImages.client_id.in_(client_ids),
            ],
        )

        return {
            r.client_id: self._map_image(r)
            for r in rows
        }