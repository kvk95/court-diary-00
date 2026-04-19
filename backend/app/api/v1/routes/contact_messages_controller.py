"""Controller for Contact Messages"""

from fastapi import Body, Depends, Query

from app.api.v1.routes.base.base_controller import BaseController
from app.dependencies import get_contact_messages_service
from app.dtos.base.base_out_dto import BaseOutDto
from app.dtos.base.paginated_out import PagingData
from app.dtos.contact_message_dto import (
    ContactMessageCreate,
    ContactMessageDelete,
    ContactMessageEdit,
    ContactMessageOut,
    ContactMessageListOut,
    ContactMessageStats,
)
from app.services.contact_messages_service import ContactMessagesService


class ContactMessagesController(BaseController):

    CONTROLLER_NAME = "contact-messages"
    
    @BaseController.get(
        "/stats",
        summary="Get support ticket statistics",
        response_model=BaseOutDto[ContactMessageStats],
    )
    async def contact_messages_get_stats(
        self,
        service: ContactMessagesService = Depends(get_contact_messages_service),
    ) -> BaseOutDto[ContactMessageStats]:
        """Return summary statistics for support tickets"""
        return self.success(result=await service.contact_messages_get_stats())

    @BaseController.get(
        "",
        summary="List contact messages",
        response_model=BaseOutDto[PagingData[ContactMessageListOut]],
    )
    async def get_paged(
        self,
        page: int = Query(1, ge=1),
        limit: int = Query(50, ge=1, le=100),
        status_code: str | None = Query(None),
        search: str | None = Query(None),
        service: ContactMessagesService = Depends(get_contact_messages_service),
    ):
        return self.success(
            result=await service.get_paged(
                page=page,
                limit=limit,
                status_code=status_code,
                search=search,
            )
        )

    @BaseController.get(
        "/{message_id}",
        summary="Get message by ID",
        response_model=BaseOutDto[ContactMessageOut],
    )
    async def get_by_id(
        self,
        message_id: str,
        service: ContactMessagesService = Depends(get_contact_messages_service),
    ):
        return self.success(
            result=await service.get_by_id(message_id=message_id)
        )

    @BaseController.post(
        "",
        summary="Create contact message",
        response_model=BaseOutDto[ContactMessageOut],
    )
    async def add(
        self,
        payload: ContactMessageCreate = Body(...),
        service: ContactMessagesService = Depends(get_contact_messages_service),
    ):
        return self.success(result=await service.add(payload=payload))

    @BaseController.put(
        "",
        summary="Update contact message",
        response_model=BaseOutDto[ContactMessageOut],
    )
    async def update_status(
        self,
        payload: ContactMessageEdit = Body(...),
        service: ContactMessagesService = Depends(get_contact_messages_service),
    ):
        return self.success(result=await service.update_status(payload=payload))

    @BaseController.delete(
        "",
        summary="Delete contact message",
        response_model=BaseOutDto[dict],
    )
    async def delete(
        self,
        payload: ContactMessageDelete = Body(...),
        service: ContactMessagesService = Depends(get_contact_messages_service),
    ):
        return self.success(result=await service.delete(payload=payload))