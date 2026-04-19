"""chamber_controller.py — HTTP routes for Chamber / Settings module"""

from fastapi import Body, Depends, Path

from app.api.v1.routes.base.base_controller import BaseController
from app.database.models.refm_modules import RefmModulesEnum
from app.dependencies import get_chamber_service
from app.dtos.base.base_out_dto import BaseOutDto
from app.dtos.chamber_dto import ChamberAdd, ChamberEdit, ChamberIdInput, ChamberOut, ChamberStatus
from app.services.chamber_service import ChamberService

_ADMN = RefmModulesEnum.ADMIN
_SETT = RefmModulesEnum.SETTINGS


class ChamberController(BaseController):
    CONTROLLER_NAME = "chamber"

    @BaseController.get(
        "",
        summary="Get chamber detail",
        response_model=BaseOutDto[ChamberOut],
        # dependencies=[Depends(require_permission(_SETT, PType.READ))],
    )
    async def chamber_detail(
        self,
        service: ChamberService = Depends(get_chamber_service), 
    ) -> BaseOutDto[ChamberOut]:
        return self.success(result=await service.chamber_get_by_id())

    @BaseController.get(
        "/{chamber_id}",
        summary="Get chamber detail",
        response_model=BaseOutDto[ChamberOut],
        # dependencies=[Depends(require_permission(_SETT, PType.READ))],
    )
    async def chamber_get_by_id(
        self,
        service: ChamberService = Depends(get_chamber_service),
        chamber_id: str = Path(..., min_length=36, max_length=36),
    ) -> BaseOutDto[ChamberOut]:
        return self.success(result=await service.chamber_get_by_id(chamber_id=chamber_id))

    @BaseController.post(
        "",
        summary="Create new chamber",
        response_model=BaseOutDto[ChamberOut],
        # dependencies=[Depends(require_permission(_ADMN, PType.CREATE))],
    )
    async def chamber_add(
        self,
        _: ChamberAdd = Body(...),
        service: ChamberService = Depends(get_chamber_service),
    ) -> BaseOutDto[ChamberOut]:
        return self.success(result=await service.chamber_add())

    @BaseController.put(
        "",
        summary="Edit chamber details",
        response_model=BaseOutDto[ChamberOut],
        # dependencies=[Depends(require_permission(_ADMN, PType.WRITE))],
    )
    async def chamber_edit(
        self,
        payload: ChamberEdit = Body(...),
        service: ChamberService = Depends(get_chamber_service),
    ) -> BaseOutDto[ChamberOut]:
        return self.success(result=await service.chamber_edit(payload=payload))

    @BaseController.put(
        "/status",
        summary="Edit chamber details",
        response_model=BaseOutDto[ChamberOut],
        # dependencies=[Depends(require_permission(_ADMN, PType.WRITE))],
    )
    async def chamber_status(
        self,
        payload: ChamberStatus = Body(...),
        service: ChamberService = Depends(get_chamber_service),
    ) -> BaseOutDto[ChamberOut]:
        return self.success(result=await service.chamber_status(payload=payload))

    @BaseController.put(
        "/undelete",
        summary="undelete chamber",
        response_model=BaseOutDto[ChamberOut],
        # dependencies=[Depends(require_permission(_ADMN, PType.WRITE))],
    )
    async def chamber_undelete(
        self,
        payload: ChamberIdInput = Body(...),
        service: ChamberService = Depends(get_chamber_service),
    ) -> BaseOutDto[ChamberOut]:
        return self.success(result=await service.chamber_undelete(payload=payload))

    @BaseController.delete(
        "",
        summary="delete chamber",
        response_model=BaseOutDto[dict],
        # dependencies=[Depends(require_permission(_ADMN, PType.WRITE))],
    )
    async def chamber_delete(
        self,
        payload: ChamberIdInput = Body(...),
        service: ChamberService = Depends(get_chamber_service),
    ) -> BaseOutDto[dict]:
        return self.success(result=await service.chamber_delete(payload=payload))