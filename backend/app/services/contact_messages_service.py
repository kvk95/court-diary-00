"""Contact Message Service"""

from typing import Optional

from sqlalchemy.ext.asyncio import AsyncSession

from app.database.models.contact_messages import ContactMessages
from app.database.models.refm_ticket_status import RefmTicketStatus
from app.database.repositories.contact_messages_repository import ContactMessagesRepository
from app.dtos.base.paginated_out import PagingBuilder, PagingData
from app.dtos.contact_message_dto import (
    ContactMessageCreate,
    ContactMessageDelete,
    ContactMessageEdit,
    ContactMessageOut,
    ContactMessageListOut,
)
from app.services.base.secured_base_service import BaseSecuredService
from app.validators import ErrorCodes, ValidationErrorDetail
from app.validators.field_validations import FieldValidator


class ContactMessagesService(BaseSecuredService):

    def __init__(
        self,
        session: AsyncSession,
        contact_messages_repo: Optional[ContactMessagesRepository] = None,
    ):
        super().__init__(session)
        self.contact_messages_repo = contact_messages_repo or ContactMessagesRepository()

    # ─────────────────────────────────────
    # GET LIST
    # ─────────────────────────────────────

    async def get_paged(
        self,
        page: int,
        limit: int,
        status_code: Optional[str]  = None,
        search: Optional[str] = None,
    ) -> PagingData[ContactMessageListOut]:

        rows, total = await self.contact_messages_repo.list_messages(
            session=self.session,
            status_code=status_code,
            search=search,
        )

        records = [
            await self.__to_out(r)
            for r in rows
        ]

        return PagingBuilder(total_records=total, page=page, limit=limit).build(records)

    async def __to_out(self, r):        

        status_map = await self.refm_resolver.get_desc_map(
            column_attr=ContactMessages.status_code,
            value_column=RefmTicketStatus.description
        )

        return ContactMessageListOut(
                message_id=r.message_id,
                chamber_id=r.chamber_id,
                full_name=r.full_name,
                email=r.email,
                subject=r.subject,
                message=r.message,
                status_code=r.status_code,
                status_description= await self.refm_resolver.get_value(
                    code= r.status_code,
                    desc_map=status_map,
                ),
                created_date=r.created_date,
                updated_date=r.updated_date,
            )

    # ─────────────────────────────────────
    # GET ONE
    # ─────────────────────────────────────

    async def get_by_id(self, message_id: str) -> ContactMessageOut:

        msg = await self.contact_messages_repo.get_by_id(
            session=self.session,
            filters={
                ContactMessages.message_id: message_id,
                ContactMessages.chamber_id: self.chamber_id,
            },
        )

        if not msg:
            raise ValidationErrorDetail(
                code=ErrorCodes.NOT_FOUND,
                message="Message not found",
            )
        
        return await self.__to_out(msg)

    # ─────────────────────────────────────
    # CREATE
    # ─────────────────────────────────────

    async def add(self, payload: ContactMessageCreate) -> ContactMessageOut:   
            
        if err := FieldValidator.validate_email(payload.email):
            raise(err)

        data = payload.model_dump(exclude_unset=True, exclude_none=True)

        if self.chamber_id:
            data["chamber_id"] = self.chamber_id
            data["audit_user_id"] = self.user_id  # 👈 your requirement

        msg = await self.contact_messages_repo.create(
            session=self.session,
            data=self.contact_messages_repo.map_fields_to_db_column(data),
        )

        return await self.__to_out(msg)

    async def update_status(self, payload: ContactMessageEdit):

        msg = await self.contact_messages_repo.get_by_id(
            session=self.session,
            filters={
                ContactMessages.message_id: payload.message_id,
                ContactMessages.chamber_id: self.chamber_id,
            },
        )

        if not msg:
            raise ValidationErrorDetail(
                code=ErrorCodes.NOT_FOUND,
                message="Message not found",
            )

        updated = await self.contact_messages_repo.update(
            session=self.session,
            id_values=payload.message_id,
            data={"status_code": payload.status_code},
        )

        return await self.__to_out(updated)

    # ─────────────────────────────────────
    # DELETE
    # ─────────────────────────────────────

    async def delete(self, payload: ContactMessageDelete) -> dict:

        msg = await self.contact_messages_repo.get_by_id(
            session=self.session,
            filters={
                ContactMessages.message_id: payload.message_id,
                ContactMessages.chamber_id: self.chamber_id,
            },
        )

        if not msg:
            raise ValidationErrorDetail(
                code=ErrorCodes.NOT_FOUND,
                message="Message not found",
            )

        await self.contact_messages_repo.delete(
            session=self.session,
            id_values=payload.message_id,
        )

        return {"message_id": payload.message_id, "deleted": True}