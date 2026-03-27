"""collaborations_controller.py — HTTP routes for Case Collaboration module"""

from typing import List, Optional

from fastapi import Body, Depends, Path, Query

from app.api.v1.routes.base.base_controller import BaseController
from app.dependencies import get_collaborations_service
from app.dtos.base.base_out_dto import BaseOutDto
from app.dtos.base.paginated_out import PagingData
from app.dtos.collaborations_dto import (
    CollaborationInvite,
    CollaborationOut,
    CollaborationRespond,
    CollaborationRevoke,
)
from app.services.collaborations_service import CollaborationsService
from app.utils.constants import PAGINATION_DEFAULT_LIMIT, PAGINATION_DEFAULT_PAGE


class CollaborationsController(BaseController):
    CONTROLLER_NAME = "collaborations"

    # ── Outgoing (as owner) ───────────────────────────────────────────────

    @BaseController.get(
        "/outgoing",
        summary="Collaborations this chamber has sent (as case owner)",
        response_model=BaseOutDto[PagingData[CollaborationOut]],
    )
    async def collabs_get_outgoing(
        self,
        page: int = Query(PAGINATION_DEFAULT_PAGE, ge=1),
        limit: int = Query(PAGINATION_DEFAULT_LIMIT, ge=1, le=200),
        status: Optional[str] = Query(None, description="PN | AC | RJ | RV"),
        service: CollaborationsService = Depends(get_collaborations_service),
    ) -> BaseOutDto[PagingData[CollaborationOut]]:
        return self.success(
            result=await service.collabs_get_outgoing(page=page, limit=limit, status=status)
        )

    # ── Incoming (as collaborator) ────────────────────────────────────────

    @BaseController.get(
        "/incoming",
        summary="Collaboration invitations received by this chamber",
        response_model=BaseOutDto[PagingData[CollaborationOut]],
    )
    async def collabs_get_incoming(
        self,
        page: int = Query(PAGINATION_DEFAULT_PAGE, ge=1),
        limit: int = Query(PAGINATION_DEFAULT_LIMIT, ge=1, le=200),
        status: Optional[str] = Query(None, description="PN | AC | RJ | RV"),
        service: CollaborationsService = Depends(get_collaborations_service),
    ) -> BaseOutDto[PagingData[CollaborationOut]]:
        return self.success(
            result=await service.collabs_get_incoming(page=page, limit=limit, status=status)
        )

    # ── Get for a case ────────────────────────────────────────────────────

    @BaseController.get(
        "/cases/{case_id}",
        summary="All collaborations for a specific case (owner view)",
        response_model=BaseOutDto[List[CollaborationOut]],
    )
    async def collabs_get_by_case(
        self,
        case_id: str = Path(..., min_length=36, max_length=36),
        service: CollaborationsService = Depends(get_collaborations_service),
    ) -> BaseOutDto[List[CollaborationOut]]:
        return self.success(
            result=await service.collabs_get_by_case(case_id=case_id)
        )

    # ── Invite ────────────────────────────────────────────────────────────

    @BaseController.post(
        "/invite",
        summary="Invite another chamber to collaborate on a case",
        response_model=BaseOutDto[CollaborationOut],
    )
    async def collabs_invite(
        self,
        payload: CollaborationInvite = Body(...),
        service: CollaborationsService = Depends(get_collaborations_service),
    ) -> BaseOutDto[CollaborationOut]:
        return self.success(result=await service.collabs_invite(payload=payload))

    # ── Respond (accept / reject) ─────────────────────────────────────────

    @BaseController.put(
        "/respond",
        summary="Accept or reject a collaboration invitation (collaborator chamber)",
        response_model=BaseOutDto[CollaborationOut],
    )
    async def collabs_respond(
        self,
        payload: CollaborationRespond = Body(...),
        service: CollaborationsService = Depends(get_collaborations_service),
    ) -> BaseOutDto[CollaborationOut]:
        return self.success(result=await service.collabs_respond(payload=payload))

    # ── Revoke ────────────────────────────────────────────────────────────

    @BaseController.put(
        "/revoke",
        summary="Revoke a collaboration (owner chamber cancels it)",
        response_model=BaseOutDto[CollaborationOut],
    )
    async def collabs_revoke(
        self,
        payload: CollaborationRevoke = Body(...),
        service: CollaborationsService = Depends(get_collaborations_service),
    ) -> BaseOutDto[CollaborationOut]:
        return self.success(result=await service.collabs_revoke(payload=payload))
