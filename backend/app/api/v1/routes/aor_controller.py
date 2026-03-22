"""aor_controller.py — HTTP routes for Case AOR (Advocate on Record) module"""

from typing import List

from fastapi import Body, Depends, Path

from app.api.v1.routes.base.base_controller import BaseController
from app.dependencies import get_aor_service
from app.dtos.aor_dto import AorCreate, AorEdit, AorOut, AorWithdraw
from app.dtos.base.base_out_dto import BaseOutDto
from app.services.aor_service import AorService


class AorController(BaseController):
    CONTROLLER_NAME = "aor"

    # ── List AORs for a case ──────────────────────────────────────────────

    @BaseController.get(
        "/cases/{case_id}",
        summary="Get all AORs (advocates on record) for a case",
        response_model=BaseOutDto[List[AorOut]],
    )
    async def aors_get_by_case(
        self,
        case_id: int = Path(..., gt=0),
        service: AorService = Depends(get_aor_service),
    ) -> BaseOutDto[List[AorOut]]:
        return self.success(result=await service.aors_get_by_case(case_id=case_id))

    # ── Add AOR ───────────────────────────────────────────────────────────

    @BaseController.post(
        "/add",
        summary="Add an advocate on record to a case",
        response_model=BaseOutDto[AorOut],
    )
    async def aors_add(
        self,
        payload: AorCreate = Body(...),
        service: AorService = Depends(get_aor_service),
    ) -> BaseOutDto[AorOut]:
        return self.success(result=await service.aors_add(payload=payload))

    # ── Edit AOR (set primary, update notes) ─────────────────────────────

    @BaseController.put(
        "/edit",
        summary="Edit an AOR record (set primary, change status, update notes)",
        response_model=BaseOutDto[AorOut],
    )
    async def aors_edit(
        self,
        payload: AorEdit = Body(...),
        service: AorService = Depends(get_aor_service),
    ) -> BaseOutDto[AorOut]:
        return self.success(result=await service.aors_edit(payload=payload))

    # ── Withdraw AOR ──────────────────────────────────────────────────────

    @BaseController.put(
        "/withdraw",
        summary="Withdraw an AOR (sets status=WD and withdrawal_date)",
        response_model=BaseOutDto[AorOut],
    )
    async def aors_withdraw(
        self,
        payload: AorWithdraw = Body(...),
        service: AorService = Depends(get_aor_service),
    ) -> BaseOutDto[AorOut]:
        return self.success(result=await service.aors_withdraw(payload=payload))

    # ── Remove AOR ────────────────────────────────────────────────────────

    @BaseController.delete(
        "/{case_aor_id}/remove",
        summary="Remove an AOR record entirely",
        response_model=BaseOutDto[dict],
    )
    async def aors_remove(
        self,
        case_aor_id: int = Path(..., gt=0),
        service: AorService = Depends(get_aor_service),
    ) -> BaseOutDto[dict]:
        return self.success(result=await service.aors_remove(case_aor_id=case_aor_id))
