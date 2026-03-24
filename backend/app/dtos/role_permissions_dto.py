from typing import Optional

from pydantic import BaseModel


class RolePermissionBase(BaseModel):
    chamber_module_id: int
    allow_all_ind: bool = False
    read_ind: bool = False
    write_ind: bool = False
    create_ind: bool = False
    delete_ind: bool = False
    # Add these if you have them in schema
    # import_ind: bool = False
    # export_ind: bool = False


class RolePermissionEdit(RolePermissionBase):
    pass


class RolePermissionModuleOut(BaseModel):
    chamber_module_id: int
    chamber_id: int
    chamber_name: str
    module_code: str
    module_name: str
    permission_id: Optional[int] = None
    role_id:int
    allow_all_ind: bool
    read_ind: bool
    write_ind: bool
    create_ind: bool
    delete_ind: bool
    # Add these if you have them in schema
    # import_ind: bool
    # export_ind: bool


class RolePermissionMatrixOut(BaseModel):
    role_id: int
    role_name: str
    role_code: Optional[str]
    permissions: list[RolePermissionModuleOut]