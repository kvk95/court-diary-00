"""DTOs for Support Ticket module"""

from datetime import date, datetime
from typing import Optional

from pydantic import Field

from app.database.models.refm_modules import RefmModulesConstants
from app.dtos.base.base_data import BaseInData, BaseRecordData


class SupportTicketBase(BaseInData):
    """Base fields for Support Ticket"""
    subject: str = Field(..., max_length=255)
    description: str = Field(..., min_length=1)
    module_code: Optional[str] = Field(RefmModulesConstants.DASHBOARD, max_length=8)


class SupportTicketCreate(SupportTicketBase):
    """Payload for creating a new support ticket"""


class SupportTicketEdit(BaseInData):
    """Payload for updating a support ticket"""
    ticket_id: str
    description: Optional[str] = Field(None, min_length=1)
    status_code: Optional[str] = Field(None, max_length=4)
    assigned_to: Optional[str] = None
    due_date: Optional[date] = None


class SupportTicketDelete(BaseInData):
    """Payload for deleting a support ticket"""
    ticket_id: str


class SupportTicketOut(BaseRecordData):
    
    ticket_id: str
    chamber_id: str
    ticket_number: str
    subject: str
    description: str
    module_code: Optional[str]
    module_name: Optional[str]
    status_code: str
    status_description: Optional[str]
    assigned_to: Optional[str]
    assigned_to_name: Optional[str]
    reported_by: str
    reported_by_name: Optional[str]
    reported_date: Optional[datetime]
    assigned_date: Optional[datetime]
    resolved_date: Optional[datetime]
    due_date: Optional[date]
    created_date: datetime
    updated_date: datetime


class SupportTicketListOut(SupportTicketOut):
    pass


class SupportTicketStats(BaseRecordData):
    """Summary stats for support tickets"""
    total: int = 0
    open: int = 0
    in_progress: int = 0
    resolved: int = 0
    overdue: int = 0