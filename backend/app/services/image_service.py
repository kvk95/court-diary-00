from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.models.refm_img_upload_for import RefmImgUploadForEnum
from app.database.repositories.profile_images_repository import ProfileImagesRepository
from app.database.models.profile_images import ProfileImages
from app.services.base.secured_base_service import BaseSecuredService


class ImageService(BaseSecuredService):
    def __init__(
        self,
        session: AsyncSession,
        profile_images_repo: Optional[ProfileImagesRepository] = None,
    ):
        super().__init__(session)
        self.profile_images_repo = profile_images_repo or ProfileImagesRepository()

    async def handle_image(
        self,
        *,
        session: AsyncSession,
        payload,
        entity_id: str,
        image_upload_code: RefmImgUploadForEnum,
        description: str = "Image uploaded",
    ) -> Optional[ProfileImages]:
        """Handle image upload for Client and User (add + edit)"""

        if not getattr(payload, "image_data", None):
            return None

        # Determine entity field and repo method
        if image_upload_code == RefmImgUploadForEnum.CLIENT:
            get_image_func = self.profile_images_repo.get_profile_image_by_clientid
            entity_field = ProfileImages.client_id.key
        else:  # USER
            get_image_func = self.profile_images_repo.get_profile_image_by_user_id
            entity_field = ProfileImages.user_id.key

        existing_img = await get_image_func(session=session, **{entity_field: entity_id})

        image_details = {
            entity_field: entity_id,
            ProfileImages.image_upload_code.key: image_upload_code.value,
            ProfileImages.image_data.key: payload.image_data,
            ProfileImages.description.key: description,
        }

        if existing_img and existing_img.get(ProfileImages.image_id.key):
            # UPSERT (update)
            image_details[ProfileImages.image_id.key] = existing_img[ProfileImages.image_id.key]

            img = await self.profile_images_repo.upsert(
                filters={ProfileImages.image_id: existing_img[ProfileImages.image_id.key]},   # Must be column object
                session=session,
                data=self.profile_images_repo.map_fields_to_db_column(image_details),
            )
        else:
            # CREATE new
            img = await self.profile_images_repo.create(
                session=session,
                data=self.profile_images_repo.map_fields_to_db_column(image_details),
            )

        return img