"""suad_controller.py — HTTP routes for Main Dashboard and Admin Dashboard"""


from typing import List

from fastapi import Body, Depends, Query

from app.api.v1.routes.base.base_controller import BaseController
from app.auth.permissions import PType, require_permission
from app.database.models.refm_modules import RefmModulesEnum
from app.dependencies import get_suad_service
from app.dtos.base.base_out_dto import BaseOutDto
from app.dtos.base.paginated_out import PagingData
from app.dtos.cases_dto import RecentActivityItem
from app.dtos.suad_dto import ChamberItem, ChamberStatsOut, GlobalSettingsEdit, GlobalSettingsOut, SuperAdminDashboardStats, TopChamberItem, UserItem, UserStatsOut
from app.services.suad_service import SuadService
from app.utils.constants import PAGINATION_DEFAULT_LIMIT, PAGINATION_DEFAULT_PAGE

_SUAD = RefmModulesEnum.SUPER_USER


class SuadController(BaseController):
    CONTROLLER_NAME = "suad"
    
    @BaseController.get(
        "",
        summary="Get global settings (public)",
        response_model=BaseOutDto[GlobalSettingsOut],
    )
    async def get_settings(
        self,
        service: SuadService = Depends(get_suad_service),
    )->BaseOutDto[GlobalSettingsOut]:
        return self.success(result=await service.get_settings())

    # 🔐 EDIT (SUAD ONLY)
    @BaseController.put(
        "",
        summary="Update global settings",
        response_model=BaseOutDto[GlobalSettingsOut],
        dependencies=[Depends(require_permission(RefmModulesEnum.SUPER_USER, PType.WRITE))]
    )
    async def update_settings(
        self,
        payload: GlobalSettingsEdit = Body(...),
        service: SuadService = Depends(get_suad_service),
    )->BaseOutDto[GlobalSettingsOut]:
        return self.success(result=await service.update_settings(payload))

    @BaseController.get(
        "/dashboard/stats",
        summary="Super Admin Dashboard - Stats",
        response_model=BaseOutDto[SuperAdminDashboardStats],
        dependencies=[Depends(require_permission(_SUAD, PType.READ))],
    )
    async def get_dashboard_stats(
        self,
        service: SuadService = Depends(get_suad_service),
    ) -> BaseOutDto[SuperAdminDashboardStats]:
        """Get Super Admin Stats"""
        result = await service.get_dashboard_stats()
        return self.success(result=result)

    @BaseController.get(
        "/dashboard/recentactivity",
        summary="Super Admin Dashboard - Recent Activity",
        response_model=BaseOutDto[List[RecentActivityItem]],
        dependencies=[Depends(require_permission(_SUAD, PType.READ))],
    )
    async def get_recent_activity(
        self,
        service: SuadService = Depends(get_suad_service),
        limit: int = Query(5, ge=1, le=100),
    ) -> BaseOutDto[List[RecentActivityItem]]:
        """Get Super Admin Recent Activity"""
        result = await service.get_recent_activity(
            limit=limit)
        return self.success(result=result)

    @BaseController.get(
        "/dashboard",
        summary="Super Admin Dashboard - Chambers",
        response_model=BaseOutDto[List[TopChamberItem]],
        dependencies=[Depends(require_permission(_SUAD, PType.READ))],
    )
    async def get_superadmin_dashboard(
        self,
        service: SuadService = Depends(get_suad_service),
        search: str | None = Query(None, description="Search chambers"),
    ) -> BaseOutDto[List[TopChamberItem]]:
        """Get Super Admin platform-wide dashboard"""
        result = await service.get_superadmin_dashboard(
            search=search)
        return self.success(result=result)
    
    @BaseController.get(
        "/chambers/stats",
        summary="Chamber Stats",
        response_model=BaseOutDto[ChamberStatsOut],
        dependencies=[Depends(require_permission(_SUAD, PType.READ))],
    )
    async def get_chambers_stats(
        self,
        service: SuadService = Depends(get_suad_service),
    ) -> BaseOutDto[ChamberStatsOut]:
        result = await service.get_chambers_stats()
        return self.success(result=result)
    
    @BaseController.get(
        "/chambers",
        summary="List all chambers",
        response_model=BaseOutDto[PagingData[ChamberItem]],
        dependencies=[Depends(require_permission(_SUAD, PType.READ))],
    )
    async def get_chambers(
        self,
        page: int = Query(PAGINATION_DEFAULT_PAGE, ge=1),
        limit: int = Query(PAGINATION_DEFAULT_LIMIT, ge=1, le=500),
        search: str | None = Query(None),
        status: str | None = Query(None),
        service: SuadService = Depends(get_suad_service),
    )->BaseOutDto[PagingData[ChamberItem]]:
        result = await service.get_chambers(page, limit, search, status)
        return self.success(result=result)
    
    @BaseController.get(
        "/users/stats",
        summary="Global Users Stats",
        response_model=BaseOutDto[UserStatsOut],
        dependencies=[Depends(require_permission(_SUAD, PType.READ))],
    )
    async def get_user_stats(
        self,
        service: SuadService = Depends(get_suad_service),
    )->BaseOutDto[UserStatsOut]:
        result = await service.get_user_stats()
        return self.success(result=result)
    
    @BaseController.get(
        "/users",
        summary="Get All users",
        response_model=BaseOutDto[PagingData[UserItem]],
        dependencies=[Depends(require_permission(_SUAD, PType.READ))],
    )
    async def get_users(
        self,
        page: int = Query(PAGINATION_DEFAULT_PAGE, ge=1),
        limit: int = Query(PAGINATION_DEFAULT_LIMIT, ge=1, le=500),
        search: str | None = Query(None),
        status: str | None = Query(None),
        service: SuadService = Depends(get_suad_service),
    ) -> BaseOutDto[PagingData[UserItem]]:
        result = await service.get_users(page, limit, search, status)
        return self.success(result=result)