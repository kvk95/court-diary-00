"""DTOs for Contact Message module"""

from datetime import datetime
from typing import Optional

from pydantic import Field

from app.dtos.base.base_data import BaseInData, BaseRecordData


class ContactMessageBase(BaseInData):
    """Base fields for Contact Message"""

    full_name: str = Field(..., max_length=150)
    email: str = Field(..., max_length=150)
    subject: Optional[str] = Field(None, max_length=255)
    message: str = Field(..., min_length=1)


class ContactMessageCreate(ContactMessageBase):
    """Payload for creating message"""
    pass

class ContactMessageEdit(BaseInData):
    message_id: int
    status_code: str


class ContactMessageDelete(BaseInData):
    """Payload for deleting message"""
    message_id: str


class ContactMessageOut(BaseRecordData):
    message_id: int
    chamber_id: Optional[str]

    full_name: str
    email: str
    subject: Optional[str]
    message: str

    status_code: str
    status_description: Optional[str]

    created_date: datetime
    updated_date: datetime


class ContactMessageListOut(ContactMessageOut):
    pass