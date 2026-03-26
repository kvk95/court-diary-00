from typing import Optional

from pydantic import BaseModel, Field


class RoleBase(BaseModel):
    role_name: str = Field(..., min_length=1, max_length=80)
    description: Optional[str] = None
    status_ind: bool = True


class RoleCreate(RoleBase):
    pass


class RoleUpdate(BaseModel):
    role_name: Optional[str] = Field(None, min_length=1, max_length=80)
    description: Optional[str] = None
    status_ind: Optional[bool] = None


class RoleOut(BaseModel):
    role_id: int
    role_name: str
    description: Optional[str]
    status_ind: bool

    class Config:
        from_attributes = True


class RoleWithStatsOut(RoleOut):
    user_count: int = 0


class RoleUserCountOut(BaseModel):
    role_id: int
    user_count: int


class RoleDelete(BaseModel):
    role_id: int