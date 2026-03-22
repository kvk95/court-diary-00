"""dashboard_controller.py — HTTP routes for Main Dashboard and Admin Dashboard"""

from fastapi import Depends

from app.api.v1.routes.base.base_controller import BaseController
from app.auth.deps import get_current_user
from app.dependencies import get_dashboard_service
from app.dtos.base.base_out_dto import BaseOutDto
from app.dtos.dashboard_dto import AdminDashboardOut, MainDashboardOut
from app.dtos.oauth_dtos import CurrentUserContext
from app.services.dashboard_service import DashboardService


class DashboardController(BaseController):
    CONTROLLER_NAME = "dashboard"

    @BaseController.get(
        "/main",
        summary="Main dashboard — greeting, practice overview, chamber stats, overdue + today + tomorrow hearings",
        response_model=BaseOutDto[MainDashboardOut],
    )
    async def get_main_dashboard(
        self,
        current_user: CurrentUserContext = Depends(get_current_user),
        service: DashboardService = Depends(get_dashboard_service),
    ) -> BaseOutDto[MainDashboardOut]:
        first_name = current_user.first_name or "there"
        return self.success(result=await service.get_main_dashboard(user_first_name=first_name))

    @BaseController.get(
        "/admin",
        summary="Admin dashboard — user stats, pending invitations, recent activity",
        response_model=BaseOutDto[AdminDashboardOut],
    )
    async def get_admin_dashboard(
        self,
        service: DashboardService = Depends(get_dashboard_service),
    ) -> BaseOutDto[AdminDashboardOut]:
        return self.success(result=await service.get_admin_dashboard())
