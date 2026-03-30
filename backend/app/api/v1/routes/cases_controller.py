"""cases_controller.py — HTTP routes for Cases, Hearings, Case Notes, Case Clients"""

from typing import List, Optional

from fastapi import Body, Depends, Path, Query

from app.api.v1.routes.base.base_controller import BaseController
from app.dependencies import get_cases_service
from app.dtos.base.base_out_dto import BaseOutDto
from app.dtos.base.paginated_out import PagingData
from app.dtos.cases_dto import (
    CaseClientLinkPayload,
    CaseClientOut,
    CaseCreate,
    CaseDelete,
    CaseDetailOut,
    CaseEdit,
    CaseBasicInfoOut,
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
from app.utils.constants import PAGINATION_DEFAULT_LIMIT, PAGINATION_DEFAULT_PAGE, RECORDS_DEFAULT_LIMIT


class CasesController(BaseController):
    CONTROLLER_NAME = "cases"

    # ── Stats ─────────────────────────────────────────────────────────────

    @BaseController.get(
        "/stats",
        summary="Case summary stats (4 stat cards)",
        response_model=BaseOutDto[CaseSummaryStats],
    )
    async def cases_get_stats(
        self,
        service: CasesService = Depends(get_cases_service),
    ) -> BaseOutDto[CaseSummaryStats]:
        return self.success(result=await service.cases_get_stats())

    # ── List ──────────────────────────────────────────────────────────────

    # ── Stats ─────────────────────────────────────────────────────────────

    @BaseController.get(
        "/cases/lookup",
        summary="Get cases for quick hearing add (dropdown / search)",
        response_model=BaseOutDto[list[CaseBasicInfoOut]],
    )
    async def get_cases_for_lookup(
        self,
        limit: int = Query(RECORDS_DEFAULT_LIMIT, ge=1, le=500),
        search: Optional[str] = Query(
            None,
            description="Search by case number, petitioner, or respondent",
        ),
        service: CasesService = Depends(get_cases_service),
    ) -> BaseOutDto[list[CaseBasicInfoOut]]:
        """
        Returns a lightweight list of cases for quick selection.

        Used in:
        - Quick Hearing Add
        - Case dropdowns / autocomplete

        Supports:
        - Search by case number, petitioner, respondent
        - Limited result set for fast UI response
        """
        return self.success(
            result=await service.list_cases_for_quick_hearing(
                search=search,
                limit=limit,
            )
        )

    @BaseController.get(
        "/paged",
        summary="Get cases (paginated)",
        response_model=BaseOutDto[PagingData[CaseListOut]],
    )
    async def cases_get_paged(
        self,
        page: int = Query(PAGINATION_DEFAULT_PAGE, ge=1),
        limit: int = Query(PAGINATION_DEFAULT_LIMIT, ge=1, le=500),
        search: Optional[str] = Query(None, description="Search case number, petitioner, respondent"),
        status_code: Optional[str] = Query(None, description="AC | ADJ | DIS | CLO | OVD"),
        court_id: Optional[int] = Query(None),
        sort_by: str = Query("updated_date", description="updated_date | hearing_date | case_number"),
        service: CasesService = Depends(get_cases_service),
    ) -> BaseOutDto[PagingData[CaseListOut]]:
        return self.success(result=await service.cases_get_paged(
            page=page, limit=limit, search=search,
            status_code=status_code, court_id=court_id, sort_by=sort_by,
        ))

    # ── Single ────────────────────────────────────────────────────────────

    @BaseController.get(
        "/{case_id}",
        summary="Get case detail",
        response_model=BaseOutDto[CaseDetailOut],
    )
    async def cases_get_by_id(
        self,
        case_id: str = Path(..., min_length=36, max_length=36),
        service: CasesService = Depends(get_cases_service),
    ) -> BaseOutDto[CaseDetailOut]:
        return self.success(result=await service.cases_get_by_id(case_id=case_id))

    # ── Add ───────────────────────────────────────────────────────────────

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
        return self.success(result=await service.cases_add(payload=payload))

    # ── Edit ──────────────────────────────────────────────────────────────

    @BaseController.put(
        "/edit",
        summary="Edit a case",
        response_model=BaseOutDto[CaseDetailOut],
    )
    async def cases_edit(
        self,
        payload: CaseEdit = Body(...),
        service: CasesService = Depends(get_cases_service),
    ) -> BaseOutDto[CaseDetailOut]:
        return self.success(result=await service.cases_edit(payload=payload))

    # ── Delete ────────────────────────────────────────────────────────────

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
        return self.success(result=await service.cases_delete(payload=payload))

    # ── Recent Activity ───────────────────────────────────────────────────

    @BaseController.get(
        "/{case_id}/activity",
        summary="Recent activity for case detail sidebar",
        response_model=BaseOutDto[List[RecentActivityItem]],
    )
    async def cases_get_activity(
        self,
        case_id: str = Path(..., min_length=36, max_length=36),
        limit: int = Query(10, ge=1, le=50),
        service: CasesService = Depends(get_cases_service),
    ) -> BaseOutDto[List[RecentActivityItem]]:
        return self.success(result=await service.cases_get_recent_activity(case_id=case_id, limit=limit))

    # ── Hearings — List ───────────────────────────────────────────────────

    @BaseController.get(
        "/{case_id}/hearings",
        summary="Get all hearings for a case",
        response_model=BaseOutDto[List[HearingOut]],
    )
    async def hearings_get_by_case(
        self,
        case_id: str = Path(..., min_length=36, max_length=36),
        service: CasesService = Depends(get_cases_service),
    ) -> BaseOutDto[List[HearingOut]]:
        return self.success(result=await service.hearings_get_by_case(case_id=case_id))

    # ── Hearings — Add ────────────────────────────────────────────────────

    @BaseController.post(
        "/hearings/add",
        summary="Add a hearing",
        response_model=BaseOutDto[HearingOut],
    )
    async def hearings_add(
        self,
        payload: HearingCreate = Body(...),
        service: CasesService = Depends(get_cases_service),
    ) -> BaseOutDto[HearingOut]:
        return self.success(result=await service.hearings_add(payload=payload))

    # ── Hearings — Edit ───────────────────────────────────────────────────

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
        return self.success(result=await service.hearings_edit(payload=payload))

    # ── Hearings — Delete ─────────────────────────────────────────────────

    @BaseController.delete(
        "/hearings/delete",
        summary="Delete a hearing",
        response_model=BaseOutDto[dict],
    )
    async def hearings_delete(
        self,
        payload: HearingDelete = Body(...),
        service: CasesService = Depends(get_cases_service),
    ) -> BaseOutDto[dict]:
        return self.success(result=await service.hearings_delete(payload=payload))

    # ── Case Notes — List ─────────────────────────────────────────────────

    @BaseController.get(
        "/{case_id}/notes",
        summary="Get notes for a case",
        response_model=BaseOutDto[List[CaseNoteOut]],
    )
    async def case_notes_get(
        self,
        case_id: str = Path(..., min_length=36, max_length=36),
        service: CasesService = Depends(get_cases_service),
    ) -> BaseOutDto[List[CaseNoteOut]]:
        return self.success(result=await service.case_notes_get_by_case(case_id=case_id))

    # ── Case Notes — Add ──────────────────────────────────────────────────

    @BaseController.post(
        "/notes/add",
        summary="Add a case note",
        response_model=BaseOutDto[CaseNoteOut],
    )
    async def case_notes_add(
        self,
        payload: CaseNoteCreate = Body(...),
        service: CasesService = Depends(get_cases_service),
    ) -> BaseOutDto[CaseNoteOut]:
        return self.success(result=await service.case_notes_add(payload=payload))

    # ── Case Notes — Edit ─────────────────────────────────────────────────

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
        return self.success(result=await service.case_notes_edit(payload=payload))

    # ── Case Notes — Delete ───────────────────────────────────────────────

    @BaseController.delete(
        "/notes/delete",
        summary="Delete a case note",
        response_model=BaseOutDto[dict],
    )
    async def case_notes_delete(
        self,
        payload: CaseNoteDelete = Body(...),
        service: CasesService = Depends(get_cases_service),
    ) -> BaseOutDto[dict]:
        return self.success(result=await service.case_notes_delete(payload=payload))

    # ── Case Clients — List ───────────────────────────────────────────────

    @BaseController.get(
        "/{case_id}/clients",
        summary="Get clients linked to a case",
        response_model=BaseOutDto[List[CaseClientOut]],
    )
    async def case_clients_get(
        self,
        case_id: str = Path(..., min_length=36, max_length=36),
        service: CasesService = Depends(get_cases_service),
    ) -> BaseOutDto[List[CaseClientOut]]:
        return self.success(result=await service.case_clients_get(case_id=case_id))

    # ── Case Clients — Link ───────────────────────────────────────────────

    @BaseController.post(
        "/{case_id}/clients/link",
        summary="Link a client to a case",
        response_model=BaseOutDto[CaseClientOut],
    )
    async def case_clients_link(
        self,
        case_id: str = Path(..., min_length=36, max_length=36),
        payload: CaseClientLinkPayload = Body(...),
        service: CasesService = Depends(get_cases_service),
    ) -> BaseOutDto[CaseClientOut]:
        return self.success(result=await service.case_clients_link(case_id=case_id, payload=payload))

    # ── Case Clients — Unlink ─────────────────────────────────────────────

    @BaseController.delete(
        "/{case_id}/clients/{case_client_id}/unlink",
        summary="Unlink a client from a case",
        response_model=BaseOutDto[dict],
    )
    async def case_clients_unlink(
        self,
        case_id: str = Path(..., min_length=36, max_length=36),
        case_client_id: str = Path(..., min_length=36, max_length=36),
        service: CasesService = Depends(get_cases_service),
    ) -> BaseOutDto[dict]:
        return self.success(result=await service.case_clients_unlink(case_id=case_id, case_client_id=case_client_id))
