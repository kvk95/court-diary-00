"""invitations_controller.py — User invitation management"""

from typing import Optional

from fastapi import Body, Depends, Path, Query

from app.api.v1.routes.base.base_controller import BaseController
from app.dependencies import get_invitations_service
from app.dtos.base.base_out_dto import BaseOutDto
from app.dtos.base.paginated_out import PagingData
from app.dtos.invitations_dto import InvitationCreate, InvitationOut, InvitationRevoke
from app.services.invitations_service import InvitationsService
from app.utils.constants import PAGINATION_DEFAULT_LIMIT, PAGINATION_DEFAULT_PAGE


class InvitationsController(BaseController):
    CONTROLLER_NAME = "invitations"

    @BaseController.get(
        "/paged",
        summary="List invitations",
        response_model=BaseOutDto[PagingData[InvitationOut]],
    )
    async def invitations_get_paged(
        self,
        page: int = Query(PAGINATION_DEFAULT_PAGE, ge=1),
        limit: int = Query(PAGINATION_DEFAULT_LIMIT, ge=1, le=200),
        status: Optional[str] = Query(None, description="PN=Pending, AC=Accepted, RJ=Rejected, EX=Expired"),
        service: InvitationsService = Depends(get_invitations_service),
    ) -> BaseOutDto[PagingData[InvitationOut]]:
        return self.success(result=await service.invitations_get_paged(page=page, limit=limit, status=status))

    @BaseController.post(
        "/send",
        summary="Send an invitation to join the chamber",
        response_model=BaseOutDto[InvitationOut],
    )
    async def invitations_send(
        self,
        payload: InvitationCreate = Body(...),
        service: InvitationsService = Depends(get_invitations_service),
    ) -> BaseOutDto[InvitationOut]:
        return self.success(result=await service.invitations_send(payload=payload))

    @BaseController.put(
        "/revoke",
        summary="Revoke a pending invitation",
        response_model=BaseOutDto[dict],
    )
    async def invitations_revoke(
        self,
        payload: InvitationRevoke = Body(...),
        service: InvitationsService = Depends(get_invitations_service),
    ) -> BaseOutDto[dict]:
        return self.success(result=await service.invitations_revoke(payload=payload))
