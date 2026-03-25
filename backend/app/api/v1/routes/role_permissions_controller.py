# app/api/v1/routes/role_permissions_controller.py

from typing import List

from fastapi import Body, Depends, Path, Query

from app.api.v1.routes.base.base_controller import BaseController
from app.dependencies import get_role_permissions_service
from app.dtos.base.base_out_dto import BaseOutDto
from app.dtos.role_permissions_dto import (
    RolePermissionEdit,
    RolePermissionMatrixOut,
    RolePermissionModuleOut,
    RolePermissionsSummaryOut,
)
from app.services.role_permissions_service import RolePermissionsService


class RolePermissionsController(BaseController):
    CONTROLLER_NAME = "role-permissions"

    # ─────────────────────────────────────────────────────────────────────────
    # 1. Get All Roles with Permission Summary (NEW)
    # ─────────────────────────────────────────────────────────────────────────

    @BaseController.get(
        "/roles/permissions/summary",
        summary="Get all roles with permission summary (admin overview)",
        response_model=BaseOutDto[List[RolePermissionsSummaryOut]],
    )
    async def get_all_roles_permissions_summary(
        self,
        service: RolePermissionsService = Depends(get_role_permissions_service),
    ) -> BaseOutDto[List[RolePermissionsSummaryOut]]:
        result = await service.get_all_roles_permissions_summary()
        return self.success(result=result)

    # ─────────────────────────────────────────────────────────────────────────
    # 2. Get Full Permission Matrix for ALL Roles (NEW)
    # ─────────────────────────────────────────────────────────────────────────

    @BaseController.get(
        "/roles/permissions/matrix",
        summary="Get complete permission matrix for all roles (for admin UI)",
        response_model=BaseOutDto[dict],
    )
    async def get_all_roles_full_matrix(
        self,
        service: RolePermissionsService = Depends(get_role_permissions_service),
    ) -> BaseOutDto[dict]:
        result = await service.get_all_roles_full_matrix()
        return self.success(result=result)

    # ─────────────────────────────────────────────────────────────────────────
    # 3. Get Permission Matrix for Single Role (ORIGINAL)
    # ─────────────────────────────────────────────────────────────────────────

    @BaseController.get(
        "/roles/{role_id}/permissions/matrix",
        summary="Get role permission matrix (for toggle UI)",
        response_model=BaseOutDto[List[RolePermissionModuleOut]],
    )
    async def get_permission_matrix(
        self,
        role_id: int = Path(..., gt=0, description="Role ID"),
        module_name: str | None = Query(None, description="Filter by module name"),
        service: RolePermissionsService = Depends(get_role_permissions_service),
    ) -> BaseOutDto[List[RolePermissionModuleOut]]:
        result = await service.get_permission_matrix(role_id, module_name)
        return self.success(result=result)

    # ─────────────────────────────────────────────────────────────────────────
    # 4. Get Role Permissions Summary (ORIGINAL)
    # ─────────────────────────────────────────────────────────────────────────

    @BaseController.get(
        "/roles/{role_id}/permissions/full",
        summary="Get complete permission matrix with role info",
        response_model=BaseOutDto[RolePermissionMatrixOut],
    )
    async def get_role_permissions_summary(
        self,
        role_id: int = Path(..., gt=0, description="Role ID"),
        service: RolePermissionsService = Depends(get_role_permissions_service),
    ) -> BaseOutDto[RolePermissionMatrixOut]:
        result = await service.get_role_permissions_summary(role_id)
        return self.success(result=result)

    # ─────────────────────────────────────────────────────────────────────────
    # 5. Edit Role Permissions (ORIGINAL)
    # ─────────────────────────────────────────────────────────────────────────

    @BaseController.put(
        "/roles/{role_id}/permissions/edit",
        summary="Edit role permissions (bulk update from matrix)",
        response_model=BaseOutDto[bool],
    )
    async def role_permissions_edit(
        self,
        role_id: int = Path(..., gt=0, description="Role ID"),
        payload: List[RolePermissionEdit] = Body(..., description="Permissions to set"),
        service: RolePermissionsService = Depends(get_role_permissions_service),
    ) -> BaseOutDto[bool]:
        result = await service.role_permissions_edit(role_id, payload)
        return self.success(result=result, description="Permissions updated successfully")