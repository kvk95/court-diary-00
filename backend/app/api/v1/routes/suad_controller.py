"""suad_controller.py — HTTP routes for Main Dashboard and Admin Dashboard"""


from fastapi import Depends, Query

from app.api.v1.routes.base.base_controller import BaseController
from app.auth.permissions import PType, require_permission
from app.database.models.refm_modules import RefmModulesEnum
from app.dependencies import get_suad_service
from app.dtos.base.base_out_dto import BaseOutDto
from app.dtos.suad_dto import ChamberListOut, SuperAdminDashboardOut, UserListOut
from app.services.suad_service import SuadService

_SUAD = RefmModulesEnum.SUPER_USER


class SuadController(BaseController):
    CONTROLLER_NAME = "suad"

    @BaseController.get(
        "/dashboard",
        summary="Super Admin Dashboard - Platform Overview",
        response_model=BaseOutDto[SuperAdminDashboardOut],
        dependencies=[Depends(require_permission(_SUAD, PType.READ))],
    )
    async def get_superadmin_dashboard(
        self,
        service: SuadService = Depends(get_suad_service),
        search: str | None = Query(None, description="Search chambers"),
        limit: int = Query(5, ge=1, le=100),
    ) -> BaseOutDto[SuperAdminDashboardOut]:
        """Get Super Admin platform-wide dashboard"""
        result = await service.get_superadmin_dashboard(
            limit=limit,
            search=search)
        return self.success(result=result)
    
    @BaseController.get(
        "/chambers",
        summary="List all chambers",
        response_model=BaseOutDto[ChamberListOut],
        dependencies=[Depends(require_permission(_SUAD, PType.READ))],
    )
    async def get_chambers(
        self,
        page: int = Query(1),
        limit: int = Query(10),
        search: str | None = Query(None),
        status: str | None = Query(None),
        service: SuadService = Depends(get_suad_service),
    ):
        result = await service.get_chambers(page, limit, search, status)
        return self.success(result=result)
    
    @BaseController.get(
        "/users",
        summary="Global Users (SUAD)",
        response_model=BaseOutDto[UserListOut],
        dependencies=[Depends(require_permission(_SUAD, PType.READ))],
    )
    async def get_users(
        self,
        page: int = Query(1),
        limit: int = Query(10),
        search: str | None = Query(None),
        status: str | None = Query(None),
        service: SuadService = Depends(get_suad_service),
    ):
        result = await service.get_users(page, limit, search, status)
        return self.success(result=result)