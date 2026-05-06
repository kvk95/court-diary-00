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
from app.dtos.suad_dto import (
    AnnouncementBaseIn, 
    AnnouncementCreate, 
    AnnouncementOut, 
    AnnouncementUpdate, 
    ChamberItem, 
    ChamberStatsOut, 
    GlobalSettingsEdit, 
    GlobalSettingsOut, 
    PermissionCloneIn, 
    PermissionCloneOut, 
    PermissionPushIn, 
    MasterRolePermissionDetail, 
    MasterRolePermissionStats, 
    PermissionUpdateIn, 
    SecurityRoleBaseIn, 
    SecurityRoleCreate, 
    SecurityRoleItem, 
    SecurityRoleStats, 
    SecurityRoleUpdate, 
    SuperAdminDashboardStats, 
    TopChamberItem, 
    UserItem, 
    UserStatsOut
)
from app.services.suad_service import SuadService
from app.utils.constants import PAGINATION_DEFAULT_LIMIT, PAGINATION_DEFAULT_PAGE

_SUAD = RefmModulesEnum.SUPER_USER


class SuadController(BaseController):
    CONTROLLER_NAME = "suad"
    
    @BaseController.get(
        "/gset",
        summary="Get global settings (public)",
        response_model=BaseOutDto[GlobalSettingsOut],
        dependencies=[Depends(require_permission(_SUAD, PType.READ))],
    )
    async def get_settings(
        self,
        service: SuadService = Depends(get_suad_service),
    )->BaseOutDto[GlobalSettingsOut]:
        return self.success(result=await service.get_settings())

    # 🔐 EDIT (SUAD ONLY)
    @BaseController.put(
        "/gset",
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

    # ---------------------------------------------------------------------
    # announcements
    # ---------------------------------------------------------------------
    
    @BaseController.post(
        "/announcement",
        summary="Create announcement",
        response_model=BaseOutDto[AnnouncementOut],
        dependencies=[Depends(require_permission(_SUAD, PType.WRITE))]
    )
    async def create_announcement(
        self,
        payload: AnnouncementCreate = Body(...),
        service: SuadService = Depends(get_suad_service),
    ) -> BaseOutDto[AnnouncementOut]:
        return self.success(result=await service.create_announcement(payload))

    # -----------------------------
    # LIST
    # -----------------------------
    @BaseController.get(
        "/announcement",
        summary="List announcements",
        response_model=BaseOutDto[PagingData[AnnouncementOut]],
        dependencies=[Depends(require_permission(_SUAD, PType.READ))],
    )
    async def list_announcements(
        self,
        page: int = Query(PAGINATION_DEFAULT_PAGE, ge=1),
        limit: int = Query(PAGINATION_DEFAULT_LIMIT, ge=1, le=500),

        search: str | None = Query(None),
        status: str | None = Query(None),
        type: str | None = Query(None),
        audience: str | None = Query(None),

        service: SuadService = Depends(get_suad_service),
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

    # -----------------------------
    # GET BY ID
    # -----------------------------
    @BaseController.get(
        "/announcement/{announcement_id}",
        summary="Get announcement",
        response_model=BaseOutDto[AnnouncementOut],
        dependencies=[Depends(require_permission(_SUAD, PType.READ))]
    )
    async def get_announcement(
        self,
        announcement_id: str,
        service: SuadService = Depends(get_suad_service),
    ) -> BaseOutDto[AnnouncementOut]:
        return self.success(result=await service.get_announcement(announcement_id))

    # -----------------------------
    # UPDATE
    # -----------------------------
    @BaseController.put(
        "/announcement",
        summary="Update announcement",
        response_model=BaseOutDto[AnnouncementOut],
        dependencies=[Depends(require_permission(_SUAD, PType.WRITE))]
    )
    async def update_announcement(
        self,
        payload: AnnouncementUpdate = Body(...),
        service: SuadService = Depends(get_suad_service),
    ) -> BaseOutDto[AnnouncementOut]:
        return self.success(
            result=await service.update_announcement(payload)
        )

    # -----------------------------
    # DELETE (soft)
    # -----------------------------
    @BaseController.delete(
        "/announcement",
        summary="Delete announcement",
        response_model=BaseOutDto[bool],
        dependencies=[Depends(require_permission(_SUAD, PType.DELETE))]
    )
    async def delete_announcement(
        self,
        payload: AnnouncementBaseIn = Body(...),
        service: SuadService = Depends(get_suad_service),
    ) -> BaseOutDto[bool]:
        await service.delete_announcement(payload)
        return self.success(result=True)

    # ---------------------------------------------------------------------
    # SECURITY ROLES
    # ---------------------------------------------------------------------

    @BaseController.get(
        "/roles/stats",
        summary="Global role stats",
        response_model=BaseOutDto[SecurityRoleStats],
        dependencies=[Depends(require_permission(_SUAD, PType.READ))]
    )
    async def get_role_stats(
        self,
        service: SuadService = Depends(get_suad_service),
    ) -> BaseOutDto[SecurityRoleStats]:
        return self.success(result=await service.get_security_role_stats())
    
    @BaseController.get(
        "/roles",
        summary="List global roles",
        response_model=BaseOutDto[PagingData[SecurityRoleItem]],
        dependencies=[Depends(require_permission(_SUAD, PType.READ))]
    )
    async def get_roles(
        self,
        page: int = Query(PAGINATION_DEFAULT_PAGE, ge=1),
        limit: int = Query(PAGINATION_DEFAULT_LIMIT, ge=1, le=500),
        search: str | None = Query(None),
        service: SuadService = Depends(get_suad_service),
    ) -> BaseOutDto[PagingData[SecurityRoleItem]]:
        result = await service.get_security_roles(page, limit, search)
        return self.success(result=result)
    
    @BaseController.post(
        "/roles",
        response_model=BaseOutDto[bool],
        dependencies=[Depends(require_permission(_SUAD, PType.WRITE))]
    )
    async def create_role(
        self, 
        payload: SecurityRoleCreate, 
        service: SuadService = Depends(get_suad_service)
    ) -> BaseOutDto[bool]:
        await service.create_security_role(payload)
        return self.success(result=True)


    @BaseController.put(
        "/roles",
        response_model=BaseOutDto[bool],
        dependencies=[Depends(require_permission(_SUAD, PType.WRITE))]
    )
    async def update_role(self, 
                          payload: SecurityRoleUpdate, 
                          service: SuadService = Depends(get_suad_service)
        ) -> BaseOutDto[bool]:
        await service.update_security_role(payload)
        return self.success(result=True)


    @BaseController.delete(
        "/roles",
        response_model=BaseOutDto[bool],
        dependencies=[Depends(require_permission(_SUAD, PType.DELETE))]
    )
    async def delete_role(self,                           
                          payload: SecurityRoleBaseIn,
                          service: SuadService = Depends(get_suad_service)
        ) -> BaseOutDto[bool]:
        await service.delete_security_role(payload)
        return self.success(result=True)

    # ---------------------------------------------------------------------
    # ROLES PERMISSION MASTER
    # ---------------------------------------------------------------------

    @BaseController.get("/permissions/stats",
        summary="Global Permission stats",
        response_model=BaseOutDto[MasterRolePermissionStats],
        dependencies=[Depends(require_permission(_SUAD, PType.READ))])
    async def get_permission_stats(
        self,
        service: SuadService = Depends(get_suad_service),
    ) -> BaseOutDto[MasterRolePermissionStats]:
        return self.success(
            result=await service.get_permission_stats()
        )
    
    @BaseController.get("/permissions/{role_id}",
        summary="Get Permissions by Role ID",
        response_model=BaseOutDto[List[MasterRolePermissionDetail]],
        dependencies=[Depends(require_permission(_SUAD, PType.READ))])
    async def get_permission_detail(
        self,
        role_id: int,
        service: SuadService = Depends(get_suad_service),
    ) -> BaseOutDto[List[MasterRolePermissionDetail]]:
        return self.success(
            result=await service.get_permission_detail(role_id)
        )
    
    @BaseController.post("/permissions/clone",
        response_model=BaseOutDto[PermissionCloneOut],
        dependencies=[Depends(require_permission(_SUAD, PType.WRITE))]
        )
    async def clone_permission(
        self,
        payload: PermissionCloneIn,
        service: SuadService = Depends(get_suad_service),
    ) -> BaseOutDto[PermissionCloneOut]:
        return self.success(
            result=await service.clone_permission(payload)
        )
    
    @BaseController.put("/permissions",
        summary="Update global permissions",
        response_model=BaseOutDto[PermissionCloneOut],
        dependencies=[Depends(require_permission(RefmModulesEnum.SUPER_USER, PType.WRITE))])
    async def update_permission(
        self,
        payload: PermissionUpdateIn,
        service: SuadService = Depends(get_suad_service),
    )->BaseOutDto[PermissionCloneOut]:
        return self.success(
            result=await service.update_permission(payload)
        )
    
    @BaseController.post("/permissions/push")
    async def push_permission(
        self,
        payload: PermissionPushIn,
        service: SuadService = Depends(get_suad_service),
    ):
        return self.success(
            result=await service.push_permission(payload)
        )  
    
    
    @BaseController.get(
        "/audit-log",
        summary="",
        response_model=BaseOutDto[PagingData[RecentActivityItem]],
        dependencies=[Depends(require_permission(RefmModulesEnum.SUPER_USER, PType.READ))],
    )
    async def get_recent_activity_paged(
        self,
        page: int = Query(PAGINATION_DEFAULT_PAGE, ge=1),
        limit: int = Query(PAGINATION_DEFAULT_LIMIT, ge=1, le=500),
        service: SuadService = Depends(get_suad_service),
    ) -> BaseOutDto[PagingData[RecentActivityItem]]:
        return self.success(result=await service.get_recent_activity_paged(page=page, limit=limit))