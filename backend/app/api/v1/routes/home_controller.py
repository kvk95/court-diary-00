# app/api/v1/routes/anonymous/home_controller.py

from fastapi import Depends

from app.api.v1.routes.base.base_controller import BaseController
from app.dependencies import get_home_service
from app.dtos.base.base_out_dto import BaseOutDto
from app.dtos.home_dtos import HomeStatsOut
from app.services.home_service import HomeService


class HomeController(BaseController):
    CONTROLLER_NAME = "home"

    @BaseController.get(
        "/stats",
        summary="Get home statistics",
        response_model=BaseOutDto[HomeStatsOut],
    )
    async def get_home_stats(
        self,
        service: HomeService = Depends(get_home_service),
    ):
        return self.success(
            result=await service.get_home_stats()
        )