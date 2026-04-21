"""dashboard_controller.py — HTTP routes for Main Dashboard and Admin Dashboard"""


from fastapi import Depends, Query

from app.api.v1.routes.base.base_controller import BaseController
from app.auth.permissions import PType, require_permission
from app.database.models.refm_modules import RefmModulesEnum
from app.dependencies import get_current_user, get_dashboard_service, get_suad_service_dash
from app.dtos.base.base_out_dto import BaseOutDto
from app.dtos.base.paginated_out import PagingData
from app.dtos.dashboard_dto import AdminDashboardOut, MainDashboardOut, SummaryCountsOut
from app.dtos.oauth_dtos import CurrentUserContext
from app.dtos.suad_dto import AnnouncementOut
from app.services.dashboard_service import DashboardService
from app.services.suad_service import SuadService
from app.utils.constants import PAGINATION_DEFAULT_LIMIT, PAGINATION_DEFAULT_PAGE

_DASH = RefmModulesEnum.DASHBOARD
_ADMN = RefmModulesEnum.ADMIN


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
        service: DashboardService = Depends(get_dashboard_service),  # read enforced in factory
    ) -> BaseOutDto[MainDashboardOut]:
        first_name = current_user.first_name or "there"
        return self.success(result=await service.get_main_dashboard(user_first_name=first_name))

    @BaseController.get(
        "/admin",
        summary="Admin dashboard — user stats, recent activity",
        response_model=BaseOutDto[AdminDashboardOut],
        dependencies=[Depends(require_permission(_ADMN, PType.READ))],
    )
    async def get_admin_dashboard(
        self,
        service: DashboardService = Depends(get_dashboard_service),
    ) -> BaseOutDto[AdminDashboardOut]:
        return self.success(result=await service.get_admin_dashboard())

    @BaseController.get(
        "/caseclientcount",
        summary="Dashboard — total cases & clients count",
        response_model=BaseOutDto[SummaryCountsOut],
    )
    async def get_cases_client_counts(
        self,
        service: DashboardService = Depends(get_dashboard_service),
    ) -> BaseOutDto[SummaryCountsOut]:
        return self.success(result=await service.get_cases_client_counts())

    # ---------------------------------------------------------------------
    # announcements
    # ---------------------------------------------------------------------
    
    @BaseController.get(
        "/announcement",
        summary="List announcements",
        response_model=BaseOutDto[PagingData[AnnouncementOut]],
    )
    async def list_announcements(
        self,
        page: int = Query(PAGINATION_DEFAULT_PAGE, ge=1),
        limit: int = Query(PAGINATION_DEFAULT_LIMIT, ge=1, le=500),

        search: str | None = Query(None),
        status: str | None = Query(None),
        type: str | None = Query(None),
        audience: str | None = Query(None),

        service: SuadService = Depends(get_suad_service_dash),
    ) -> BaseOutDto[PagingData[AnnouncementOut]]:

        result = await service.get_announcements(
            page=page,
            limit=limit,
            search=search,
            status=status,
            type_code=type,
            audience_code=audience,
        )

        return self.success(result=result)
    
    @BaseController.get(
        "/announcement/{announcement_id}",
        summary="Get announcement",
        response_model=BaseOutDto[AnnouncementOut],
    )
    async def get_announcement(
        self,
        announcement_id: str,
        service: SuadService = Depends(get_suad_service_dash),
    ):
        return self.success(result=await service.get_announcement(announcement_id))