"""chamber_controller.py — HTTP routes for Chamber / Settings module"""

from fastapi import Body, Depends, Path

from app.api.v1.routes.base.base_controller import BaseController
from app.dependencies import get_chamber_service
from app.dtos.base.base_out_dto import BaseOutDto
from app.dtos.chamber_dto import ChamberEdit, ChamberOut
from app.dtos.oauth_dtos import TokenOut
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

    @BaseController.post(
        "/login/{chamber_id}",
        summary="Login into Chamber",
        response_model=BaseOutDto[TokenOut],
    )
    async def login(
        self,
        chamber_id: str = Path(..., min_length=36, max_length=36),
        service: ChamberService = Depends(get_chamber_service),
    ) -> BaseOutDto[TokenOut]:
        return self.success(
            result=await service.login(chamber_id=chamber_id)
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