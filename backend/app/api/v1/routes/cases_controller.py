# app\api\v1\routes\cases_controller.py

from typing import List, Optional

from fastapi import Body, Depends, Path, Query

from app.api.v1.routes.base.base_controller import BaseController
from app.dependencies import get_cases_service
from app.dtos.base.base_out_dto import BaseOutDto
from app.dtos.base.paginated_out import PagingData
from app.dtos.cases_dto import (
    CaseCreate,
    CaseDelete,
    CaseDetailOut,
    CaseEdit,
    CaseListOut,
    CaseNoteCreate,
    CaseNoteDelete,
    CaseNoteEdit,
    CaseNoteOut,
    CaseSummaryStats,
    HearingCreate,
    HearingDelete,
    HearingEdit,
    HearingOut,
    RecentActivityItem,
)
from app.services.cases_service import CasesService
from app.utils.constants import PAGINATION_DEFAULT_LIMIT, PAGINATION_DEFAULT_PAGE


class CasesController(BaseController):
    CONTROLLER_NAME = "cases"

    # ─────────────────────────────────────────────────────────────────────
    # CASES — Stats (top 4 stat cards)
    # ─────────────────────────────────────────────────────────────────────

    @BaseController.get(
        "/stats",
        summary="Get case summary stats (total, active, adjourned, overdue)",
        response_model=BaseOutDto[CaseSummaryStats],
    )
    async def cases_get_stats(
        self,
        service: CasesService = Depends(get_cases_service),
    ) -> BaseOutDto[CaseSummaryStats]:
        data = await service.cases_get_stats()
        return self.success(result=data)

    # ─────────────────────────────────────────────────────────────────────
    # CASES — Paginated list
    # ─────────────────────────────────────────────────────────────────────

    @BaseController.get(
        "/paged/cases",
        summary="Get cases (paginated, with search and filters)",
        response_model=BaseOutDto[PagingData[CaseListOut]],
    )
    async def cases_get_paged(
        self,
        page: int = Query(PAGINATION_DEFAULT_PAGE, ge=1, description="Page number"),
        limit: int = Query(PAGINATION_DEFAULT_LIMIT, ge=1, le=500, description="Items per page"),
        search: Optional[str] = Query(None, description="Search by case number, petitioner, respondent"),
        status_code: Optional[str] = Query(None, description="Filter by status code (AC, AD, CL, etc.)"),
        court_id: Optional[int] = Query(None, description="Filter by court ID"),
        sort_by: str = Query("updated_date", description="Sort field: updated_date | hearing_date | case_number"),
        service: CasesService = Depends(get_cases_service),
    ) -> BaseOutDto[PagingData[CaseListOut]]:
        data = await service.cases_get_paged(
            page=page,
            limit=limit,
            search=search,
            status_code=status_code,
            court_id=court_id,
            sort_by=sort_by,
        )
        return self.success(result=data)

    # ─────────────────────────────────────────────────────────────────────
    # CASES — Get single case
    # ─────────────────────────────────────────────────────────────────────

    @BaseController.get(
        "/{case_id}",
        summary="Get case detail by ID",
        response_model=BaseOutDto[CaseDetailOut],
    )
    async def cases_get_by_id(
        self,
        case_id: int = Path(..., description="Case ID"),
        service: CasesService = Depends(get_cases_service),
    ) -> BaseOutDto[CaseDetailOut]:
        data = await service.cases_get_by_id(case_id=case_id)
        return self.success(result=data)

    # ─────────────────────────────────────────────────────────────────────
    # CASES — Add
    # ─────────────────────────────────────────────────────────────────────

    @BaseController.post(
        "/add",
        summary="Add a new case",
        response_model=BaseOutDto[CaseDetailOut],
    )
    async def cases_add(
        self,
        payload: CaseCreate = Body(...),
        service: CasesService = Depends(get_cases_service),
    ) -> BaseOutDto[CaseDetailOut]:
        data = await service.cases_add(payload=payload)
        return self.success(result=data)

    # ─────────────────────────────────────────────────────────────────────
    # CASES — Edit
    # ─────────────────────────────────────────────────────────────────────

    @BaseController.put(
        "/edit",
        summary="Update an existing case",
        response_model=BaseOutDto[CaseDetailOut],
    )
    async def cases_edit(
        self,
        payload: CaseEdit = Body(...),
        service: CasesService = Depends(get_cases_service),
    ) -> BaseOutDto[CaseDetailOut]:
        data = await service.cases_edit(payload=payload)
        return self.success(result=data)

    # ─────────────────────────────────────────────────────────────────────
    # CASES — Delete
    # ─────────────────────────────────────────────────────────────────────

    @BaseController.delete(
        "/delete",
        summary="Soft-delete a case",
        response_model=BaseOutDto[dict],
    )
    async def cases_delete(
        self,
        payload: CaseDelete = Body(...),
        service: CasesService = Depends(get_cases_service),
    ) -> BaseOutDto[dict]:
        data = await service.cases_delete(payload=payload)
        return self.success(result=data)

    # ─────────────────────────────────────────────────────────────────────
    # CASES — Recent activity (case detail sidebar)
    # ─────────────────────────────────────────────────────────────────────

    @BaseController.get(
        "/{case_id}/activity",
        summary="Get recent activity log for a case",
        response_model=BaseOutDto[List[RecentActivityItem]],
    )
    async def cases_get_activity(
        self,
        case_id: int = Path(..., description="Case ID"),
        limit: int = Query(10, ge=1, le=50, description="Max activity items"),
        service: CasesService = Depends(get_cases_service),
    ) -> BaseOutDto[List[RecentActivityItem]]:
        data = await service.cases_get_recent_activity(case_id=case_id, limit=limit)
        return self.success(result=data)

    # ─────────────────────────────────────────────────────────────────────
    # HEARINGS — List
    # ─────────────────────────────────────────────────────────────────────

    @BaseController.get(
        "/{case_id}/hearings",
        summary="Get all hearings for a case",
        response_model=BaseOutDto[List[HearingOut]],
    )
    async def hearings_get_by_case(
        self,
        case_id: int = Path(..., description="Case ID"),
        service: CasesService = Depends(get_cases_service),
    ) -> BaseOutDto[List[HearingOut]]:
        data = await service.hearings_get_by_case(case_id=case_id)
        return self.success(result=data)

    # ─────────────────────────────────────────────────────────────────────
    # HEARINGS — Add
    # ─────────────────────────────────────────────────────────────────────

    @BaseController.post(
        "/hearings/add",
        summary="Add a hearing to a case",
        response_model=BaseOutDto[HearingOut],
    )
    async def hearings_add(
        self,
        payload: HearingCreate = Body(...),
        service: CasesService = Depends(get_cases_service),
    ) -> BaseOutDto[HearingOut]:
        data = await service.hearings_add(payload=payload)
        return self.success(result=data)

    # ─────────────────────────────────────────────────────────────────────
    # HEARINGS — Edit
    # ─────────────────────────────────────────────────────────────────────

    @BaseController.put(
        "/hearings/edit",
        summary="Edit a hearing",
        response_model=BaseOutDto[HearingOut],
    )
    async def hearings_edit(
        self,
        payload: HearingEdit = Body(...),
        service: CasesService = Depends(get_cases_service),
    ) -> BaseOutDto[HearingOut]:
        data = await service.hearings_edit(payload=payload)
        return self.success(result=data)

    # ─────────────────────────────────────────────────────────────────────
    # HEARINGS — Delete
    # ─────────────────────────────────────────────────────────────────────

    @BaseController.delete(
        "/hearings/delete",
        summary="Soft-delete a hearing",
        response_model=BaseOutDto[dict],
    )
    async def hearings_delete(
        self,
        payload: HearingDelete = Body(...),
        service: CasesService = Depends(get_cases_service),
    ) -> BaseOutDto[dict]:
        data = await service.hearings_delete(payload=payload)
        return self.success(result=data)

    # ─────────────────────────────────────────────────────────────────────
    # CASE NOTES — List
    # ─────────────────────────────────────────────────────────────────────

    @BaseController.get(
        "/{case_id}/notes",
        summary="Get all notes for a case",
        response_model=BaseOutDto[List[CaseNoteOut]],
    )
    async def case_notes_get(
        self,
        case_id: int = Path(..., description="Case ID"),
        service: CasesService = Depends(get_cases_service),
    ) -> BaseOutDto[List[CaseNoteOut]]:
        data = await service.case_notes_get_by_case(case_id=case_id)
        return self.success(result=data)

    # ─────────────────────────────────────────────────────────────────────
    # CASE NOTES — Add
    # ─────────────────────────────────────────────────────────────────────

    @BaseController.post(
        "/notes/add",
        summary="Add a note to a case",
        response_model=BaseOutDto[CaseNoteOut],
    )
    async def case_notes_add(
        self,
        payload: CaseNoteCreate = Body(...),
        service: CasesService = Depends(get_cases_service),
    ) -> BaseOutDto[CaseNoteOut]:
        data = await service.case_notes_add(payload=payload)
        return self.success(result=data)

    # ─────────────────────────────────────────────────────────────────────
    # CASE NOTES — Edit
    # ─────────────────────────────────────────────────────────────────────

    @BaseController.put(
        "/notes/edit",
        summary="Edit a case note (author only)",
        response_model=BaseOutDto[CaseNoteOut],
    )
    async def case_notes_edit(
        self,
        payload: CaseNoteEdit = Body(...),
        service: CasesService = Depends(get_cases_service),
    ) -> BaseOutDto[CaseNoteOut]:
        data = await service.case_notes_edit(payload=payload)
        return self.success(result=data)

    # ─────────────────────────────────────────────────────────────────────
    # CASE NOTES — Delete
    # ─────────────────────────────────────────────────────────────────────

    @BaseController.delete(
        "/notes/delete",
        summary="Soft-delete a case note",
        response_model=BaseOutDto[dict],
    )
    async def case_notes_delete(
        self,
        payload: CaseNoteDelete = Body(...),
        service: CasesService = Depends(get_cases_service),
    ) -> BaseOutDto[dict]:
        data = await service.case_notes_delete(payload=payload)
        return self.success(result=data)
    
@BaseController.post(
    "/{case_id}/clients/link",
    summary="Link a client to a case",
    response_model=BaseOutDto[dict],
)
async def link_client_to_case(
    self,
    case_id: int = Path(..., description="Case ID"),
    payload: dict = Body(..., description="Client link data"),
    service: CasesService = Depends(get_cases_service),
) -> BaseOutDto[dict]:
    result = await service.link_client_to_case(
        case_id=case_id,
        client_id=payload["client_id"],
        party_role=payload["party_role"],
        is_primary=payload.get("is_primary", False),
        engagement_type=payload.get("engagement_type"),
    )
    return self.success(result=result)

# ─────────────────────────────────────────────────────────────────────────
# CASE CLIENTS — Unlink client
# ─────────────────────────────────────────────────────────────────────────
@BaseController.delete(
    "/{case_id}/clients/{client_id}/unlink",
    summary="Unlink a client from a case",
    response_model=BaseOutDto[dict],
)
async def unlink_client_from_case(
    self,
    case_id: int = Path(..., description="Case ID"),
    client_id: int = Path(..., description="Client ID"),
    service: CasesService = Depends(get_cases_service),
) -> BaseOutDto[dict]:
    result = await service.unlink_client_from_case(
        case_id=case_id,
        client_id=client_id,
    )
    return self.success(result=result)

# ─────────────────────────────────────────────────────────────────────────
# CASE CLIENTS — Get clients
# ─────────────────────────────────────────────────────────────────────────
@BaseController.get(
    "/{case_id}/clients",
    summary="Get all clients linked to a case",
    response_model=BaseOutDto[List[dict]],
)
async def get_case_clients(
    self,
    case_id: int = Path(..., description="Case ID"),
    service: CasesService = Depends(get_cases_service),
) -> BaseOutDto[List[dict]]:
    result = await service.get_case_clients(case_id=case_id)
    return self.success(result=result)