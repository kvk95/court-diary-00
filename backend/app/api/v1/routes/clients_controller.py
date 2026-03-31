"""clients_controller.py — HTTP routes for Clients module"""

from typing import List, Optional

from fastapi import Body, Depends, Path, Query

from app.api.v1.routes.base.base_controller import BaseController
from app.dependencies import get_clients_service
from app.dtos.base.base_out_dto import BaseOutDto
from app.dtos.base.paginated_out import PagingData
from app.dtos.clients_dto import (
    ClientCreate,
    ClientDetailOut,
    ClientEdit,
    ClientListOut,
    ClientSearchOut,
    ClientSummaryStats,
)
from app.services.clients_service import ClientsService
from app.utils.constants import PAGINATION_DEFAULT_LIMIT, PAGINATION_DEFAULT_PAGE


class ClientsController(BaseController):
    CONTROLLER_NAME = "clients"

    # ── Search (for Link Client modal) ────────────────────────────────────

    @BaseController.get(
        "/search",
        summary="Search clients by name, phone, or email",
        response_model=BaseOutDto[List[ClientSearchOut]],
    )
    async def clients_search(
        self,        
        search: Optional[str] = Query(
            None,
            description="Search by case number, petitioner, or respondent",
        ),
        limit: int = Query(20, ge=1, le=100),
        service: ClientsService = Depends(get_clients_service),
    ) -> BaseOutDto[List[ClientSearchOut]]:
        return self.success(result=await service.clients_search(search=search, limit=limit))

    # ── List ──────────────────────────────────────────────────────────────

    @BaseController.get(
        "/paged",
        summary="Get clients (paginated)",
        response_model=BaseOutDto[PagingData[ClientListOut]],
    )
    async def clients_get_paged(
        self,
        page: int = Query(PAGINATION_DEFAULT_PAGE, ge=1),
        limit: int = Query(PAGINATION_DEFAULT_LIMIT, ge=1, le=500),
        search: Optional[str] = Query(None, description="Search name, phone, email"),
        client_type: Optional[str] = Query(None, description="I=Individual, O=Organization"),
        service: ClientsService = Depends(get_clients_service),
    ) -> BaseOutDto[PagingData[ClientListOut]]:
        return self.success(result=await service.clients_get_paged(
            page=page, limit=limit, search=search, client_type=client_type
        ))

    # ── Single ────────────────────────────────────────────────────────────
    @BaseController.get(
        "/stats",
        summary="Client summary stats",
        response_model=BaseOutDto[ClientSummaryStats],
    )
    async def clients_get_stats(
        self,
        service: ClientsService = Depends(get_clients_service),
    ) -> BaseOutDto[ClientSummaryStats]:
        return self.success(result=await service.clients_get_stats())

    @BaseController.get(
        "/{client_id}",
        summary="Get client detail",
        response_model=BaseOutDto[ClientDetailOut],
    )
    async def clients_get_by_id(
        self,
        client_id: str = Path(..., min_length=36, max_length=36),
        service: ClientsService = Depends(get_clients_service),
    ) -> BaseOutDto[ClientDetailOut]:
        return self.success(result=await service.clients_get_by_id(client_id=client_id))

    # ── Add ───────────────────────────────────────────────────────────────

    @BaseController.post(
        "/add",
        summary="Add a new client",
        response_model=BaseOutDto[ClientDetailOut],
    )
    async def clients_add(
        self,
        payload: ClientCreate = Body(...),
        service: ClientsService = Depends(get_clients_service),
    ) -> BaseOutDto[ClientDetailOut]:
        return self.success(result=await service.clients_add(payload=payload))

    # ── Edit ──────────────────────────────────────────────────────────────

    @BaseController.put(
        "/{client_id}/edit",
        summary="Edit a client",
        response_model=BaseOutDto[ClientDetailOut],
    )
    async def clients_edit(
        self,
        client_id: str = Path(..., min_length=36, max_length=36),
        payload: ClientEdit = Body(...),
        service: ClientsService = Depends(get_clients_service),
    ) -> BaseOutDto[ClientDetailOut]:
        return self.success(result=await service.clients_edit(client_id=client_id, payload=payload))

    # ── Delete ────────────────────────────────────────────────────────────

    @BaseController.delete(
        "/{client_id}/delete",
        summary="Soft-delete a client (blocked if linked to cases)",
        response_model=BaseOutDto[dict],
    )
    async def clients_delete(
        self,
        client_id: str = Path(..., min_length=36, max_length=36),
        service: ClientsService = Depends(get_clients_service),
    ) -> BaseOutDto[dict]:
        return self.success(result=await service.clients_delete(client_id=client_id))
