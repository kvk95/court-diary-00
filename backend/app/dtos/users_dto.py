from datetime import datetime
from typing import Optional

from pydantic import EmailStr

from app.dtos.base.base_data import BaseInData, BaseRecordData


# ----- Role DTOs -----
class RoleOut(BaseInData):
    role_id: int
    role_name: str
    status_ind: bool = False
    created_date: Optional[datetime] = None


class RoleCreate(BaseInData):
    role_name: str
    status_ind: bool = False
    description: Optional[str] = None


class RoleUpdate(BaseInData):
    role_id: int
    role_name: Optional[str] = None
    status_ind: bool = False
    description: Optional[str] = None


class RoleDelete(BaseInData):
    role_id: int


# ----- Permission DTOs -----
class RolePermissionOut(BaseRecordData):
    company_module_id: int
    module_name: str
    description: Optional[str] = None
    is_active: bool
    allow_all_ind: bool
    read_ind: bool
    write_ind: bool
    create_ind: bool
    delete_ind: bool
    import_ind: bool
    export_ind: bool


class RolePermissionEdit(BaseInData):
    company_module_id: int
    allow_all_ind: bool | None = None
    read_ind: bool | None = None
    write_ind: bool | None = None
    create_ind: bool | None = None
    delete_ind: bool | None = None
    import_ind: bool | None = None
    export_ind: bool | None = None


# ----- User DTOs -----
class UserOut(BaseRecordData):
    user_id: int
    full_name: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    email: EmailStr
    phone: Optional[str] = None
    role_id: int | None = None
    role_name: Optional[str] = None
    status_ind: bool = False
    image: Optional[str] = None


class UserCreate(BaseInData):
    email: str | None = None
    first_name: str | None = None
    last_name: str | None = None
    phone: str | None = None
    status_ind: bool = False
    image: str | None = None
    role_id: int | None = None
    password: str 


class UserEdit(BaseInData):
    email: str | None = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    phone: Optional[str] = None
    status_ind: bool = False
    image: Optional[str] = None
    role_id: Optional[int] = None
    password: str | None = None
