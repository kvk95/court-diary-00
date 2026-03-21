"""app/api/v1/routes/anonymous_controller.py"""

from fastapi import Depends

from app.api.v1.routes.base.base_controller import BaseController
from app.database.cache.refm_cache import RefmData
from app.dependencies import (
    get_anonymous_service
)
from app.dtos.anonymous_dtos import ServerDateTimeOut
from app.dtos.base.base_out_dto import BaseOutDto
from app.services.anonymous_service import AnonymousService


class AnonymousController(BaseController):
    CONTROLLER_NAME = "anonymous"

    @BaseController.get(
        "/server_datetime",
        summary="Get current server date & time",
        description="Returns server UTC datetime – useful for client clock sync",
        response_model=BaseOutDto[ServerDateTimeOut],
    )
    async def get_server_datetime(
        self,
        service: AnonymousService = Depends(get_anonymous_service),
    ) -> BaseOutDto[ServerDateTimeOut]:
        result: ServerDateTimeOut = await service.get_server_datetime()
        return self.success(result=result)

    @BaseController.get(
        "/refm",
        summary="Get all reference values",
        description="Returns all available refms",
        response_model=BaseOutDto[RefmData],
    )
    async def get_all_refm(
        self,
        service: AnonymousService = Depends(get_anonymous_service),
    ) -> BaseOutDto[RefmData]:
        result: RefmData = await service.get_all_refm()
        return self.success(result=result)