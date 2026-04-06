"""chamber_controller.py — HTTP routes for Chamber / Settings module"""

from fastapi import Body, Depends

from app.api.v1.routes.base.base_controller import BaseController
from app.dependencies import get_chamber_service
from app.dtos.base.base_out_dto import BaseOutDto
from app.dtos.chamber_dto import ChamberEdit, ChamberOut
from app.services.chamber_service import ChamberService


class ChamberController(BaseController):
    CONTROLLER_NAME = "chamber"

    @BaseController.get(
        "",
        summary="Get chamber detail",
        response_model=BaseOutDto[ChamberOut],
    )
    async def chamber_get_by_id(
        self,
        service: ChamberService = Depends(get_chamber_service),
    ) -> BaseOutDto[ChamberOut]:
        return self.success(
            result=await service.chamber_get_by_id()
        )

    @BaseController.put(
        "",
        summary="Edit chamber details",
        response_model=BaseOutDto[ChamberOut],
    )
    async def chamber_edit(
        self,
        payload: ChamberEdit = Body(...),
        service: ChamberService = Depends(get_chamber_service),
    ) -> BaseOutDto[ChamberOut]:
        return self.success(
            result=await service.chamber_edit(payload=payload)
        )