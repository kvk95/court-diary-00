"""support_ticket_controller.py — HTTP routes for Support Ticket module"""

from fastapi import Body, Depends, Query

from app.api.v1.routes.base.base_controller import BaseController
from app.dependencies import get_support_ticket_service
from app.dtos.base.base_out_dto import BaseOutDto
from app.dtos.base.paginated_out import PagingData
from app.dtos.support_ticket_dto import (
    SupportTicketCreate,
    SupportTicketEdit,
    SupportTicketDelete,
    SupportTicketOut,
    SupportTicketListOut,
    SupportTicketStats,
)
from app.services.support_ticket_service import SupportTicketService


class SupportTicketController(BaseController):
    """Controller for Support Ticket operations"""
    
    CONTROLLER_NAME = "support-ticket"
    
    @BaseController.get(
        "/stats",
        summary="Get support ticket statistics",
        response_model=BaseOutDto[SupportTicketStats],
    )
    async def tickets_get_stats(
        self,
        service: SupportTicketService = Depends(get_support_ticket_service),
    ) -> BaseOutDto[SupportTicketStats]:
        """Return summary statistics for support tickets"""
        return self.success(result=await service.tickets_get_stats())
    
    @BaseController.get(
        "",
        summary="List support tickets (paginated)",
        response_model=BaseOutDto[PagingData[SupportTicketListOut]],
    )
    async def tickets_get_paged(
        self,
        page: int = Query(1, ge=1),
        limit: int = Query(50, ge=1, le=100),
        status_code: str | None = Query(None, description="Filter by status code"),
        module_code: str | None = Query(None, description="Filter by module code"),
        assigned_to: str | None = Query(None, description="Filter by assigned user ID"),
        search: str | None = Query(None, description="Search in subject/description/ticket_number"),
        sort_by: str = Query("reported_date", description="Field to sort by"),
        sort_order: str = Query("desc", regex="^(asc|desc)$", description="Sort direction"),
        service: SupportTicketService = Depends(get_support_ticket_service),
    ) -> BaseOutDto[PagingData[SupportTicketListOut]]:
        """Return paginated list of support tickets with filtering"""
        return self.success(result=await service.tickets_get_paged(
            page=page,
            limit=limit,
            status_code=status_code,
            module_code=module_code,
            assigned_to=assigned_to,
            search=search,
            sort_by=sort_by,
            sort_order=sort_order,
        ))
    
    @BaseController.get(
        "/chamber",
        summary="List support tickets (paginated) by chamber",
        response_model=BaseOutDto[PagingData[SupportTicketListOut]],
    )
    async def tickets_get_paged_chamber(
        self,
        page: int = Query(1, ge=1),
        limit: int = Query(50, ge=1, le=100),
        status_code: str | None = Query(None, description="Filter by status code"),
        module_code: str | None = Query(None, description="Filter by module code"),
        assigned_to: str | None = Query(None, description="Filter by assigned user ID"),
        search: str | None = Query(None, description="Search in subject/description/ticket_number"),
        sort_by: str = Query("reported_date", description="Field to sort by"),
        sort_order: str = Query("desc", regex="^(asc|desc)$", description="Sort direction"),
        service: SupportTicketService = Depends(get_support_ticket_service),
    ) -> BaseOutDto[PagingData[SupportTicketListOut]]:
        """Return paginated list of support tickets with filtering"""
        return self.success(result=await service.tickets_get_paged(
            page=page,
            limit=limit,
            status_code=status_code,
            module_code=module_code,
            assigned_to=assigned_to,
            search=search,
            sort_by=sort_by,
            sort_order=sort_order,
            is_chamber=True
        ))
    
    @BaseController.get(
        "/{ticket_id}",
        summary="Get support ticket by ID",
        response_model=BaseOutDto[SupportTicketOut],
    )
    async def tickets_get_by_id(
        self,
        ticket_id: str,
        service: SupportTicketService = Depends(get_support_ticket_service),
    ) -> BaseOutDto[SupportTicketOut]:
        """Return full details of a single support ticket"""
        return self.success(result=await service.tickets_get_by_id(ticket_id=ticket_id))
    
    @BaseController.post(
        "",
        summary="Create new support ticket",
        response_model=BaseOutDto[SupportTicketOut],
    )
    async def tickets_add(
        self,
        payload: SupportTicketCreate = Body(...),
        service: SupportTicketService = Depends(get_support_ticket_service),
    ) -> BaseOutDto[SupportTicketOut]:
        """Create a new support ticket"""
        return self.success(result=await service.tickets_add(payload=payload))
    
    @BaseController.put(
        "",
        summary="Update support ticket",
        response_model=BaseOutDto[SupportTicketOut],
    )
    async def tickets_edit(
        self,
        payload: SupportTicketEdit = Body(...),
        service: SupportTicketService = Depends(get_support_ticket_service),
    ) -> BaseOutDto[SupportTicketOut]:
        """Update an existing support ticket"""
        return self.success(result=await service.tickets_edit(payload=payload))
    
    @BaseController.delete(
        "",
        summary="Delete support ticket (soft)",
        response_model=BaseOutDto[dict],
    )
    async def tickets_delete(
        self,
        payload: SupportTicketDelete = Body(...),
        service: SupportTicketService = Depends(get_support_ticket_service),
    ) -> BaseOutDto[dict]:
        """Soft-delete a support ticket"""
        return self.success(result=await service.tickets_delete(payload=payload))