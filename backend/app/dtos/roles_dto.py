from typing import Optional

from pydantic import BaseModel, Field

from app.dtos.base.base_data import BaseInData, BaseRecordData


class RoleBase(BaseInData):
    role_code: str
    role_name: str = Field(..., min_length=1, max_length=80)
    description: Optional[str] = None
    status_ind: bool = True

class RoleCreate(RoleBase):
    pass

class RoleUpdate(BaseInData):
    role_name: Optional[str] = Field(None, min_length=1, max_length=80)
    description: Optional[str] = None
    status_ind: Optional[bool] = None

class RoleDelete(BaseInData):
    role_id: int

class RoleOut(BaseRecordData):
    role_id: int
    role_code: str
    role_name: str
    description: Optional[str]
    status_ind: bool
    admin_ind: bool

class RoleWithStatsOut(RoleOut):
    user_count: int = 0

class RoleUserCountOut(BaseModel):
    role_id: int
    user_count: int