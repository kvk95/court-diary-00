# app/dtos/role_permissions_dto.py

from typing import Optional
from pydantic import BaseModel


class RolePermissionBase(BaseModel):
    """Base permission fields."""
    chamber_module_id: str
    allow_all_ind: bool = False
    read_ind: bool = False
    write_ind: bool = False
    create_ind: bool = False
    delete_ind: bool = False
    import_ind: bool = False
    export_ind: bool = False


class RolePermissionEdit(RolePermissionBase):
    """Permission edit payload."""
    pass


class RolePermissionModuleOut(BaseModel):
    chamber_module_id: str
    chamber_id: str
    chamber_name: str
    module_code: str
    module_name: str
    permission_id: Optional[str] = None
    role_id:int
    allow_all_ind: bool
    read_ind: bool
    write_ind: bool
    create_ind: bool
    delete_ind: bool
    import_ind: bool
    export_ind: bool


class RolePermissionMatrixOut(BaseModel):
    """Full permission matrix for a role."""
    role_id: int
    role_name: str
    permissions: list[RolePermissionModuleOut]

class RolePermissionsSummaryOut(BaseModel):
    """Summary of permissions for all roles (for admin view)."""
    role_id: int
    role_name: str
    description: Optional[str]
    status_ind: bool
    total_modules: int = 0
    modules_with_access: int = 0