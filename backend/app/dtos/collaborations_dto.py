"""collaborations_dto.py — DTOs for Case Collaboration (multi-chamber) module"""

from datetime import datetime
from typing import Optional

from pydantic import field_validator

from app.dtos.base.base_data import BaseInData, BaseRecordData


# ─────────────────────────────────────────────────────────────────────────────
# Status codes:   PN=Pending  AC=Accepted  RJ=Rejected  RV=Revoked
# Access levels:  RO=Read Only  RW=Read Write  FU=Full Access
# ─────────────────────────────────────────────────────────────────────────────

class CollaborationOut(BaseRecordData):
    collaboration_id: str
    case_id: str
    case_number: Optional[str] = None
    case_title: Optional[str] = None       # petitioner vs respondent
    owner_chamber_id: str
    owner_chamber_name: Optional[str] = None
    collaborator_chamber_id: str
    collaborator_chamber_name: Optional[str] = None
    access_level: Optional[str] = None
    access_level_description: Optional[str] = None
    invited_by: Optional[str] = ""
    invited_by_name: Optional[str] = None
    invited_date: Optional[datetime] = None
    accepted_date: Optional[datetime] = None
    status_code: Optional[str] = None
    status_description: Optional[str] = None
    notes: Optional[str] = None
    created_date: Optional[datetime] = None


class CollaborationInvite(BaseInData):
    """Owner chamber invites a collaborator chamber to access a case."""
    case_id: str
    collaborator_chamber_id: str
    access_level: str = "RO"               # RO | RW | FU
    notes: Optional[str] = None

    @field_validator("access_level")
    @classmethod
    def valid_access(cls, v: str) -> str:
        if v not in ("RO", "RW", "FU"):
            raise ValueError("access_level must be RO, RW, or FU")
        return v


class CollaborationRespond(BaseInData):
    """Collaborator chamber accepts or rejects a pending invitation."""
    collaboration_id: str
    action: str                            # accept | reject
    notes: Optional[str] = None

    @field_validator("action")
    @classmethod
    def valid_action(cls, v: str) -> str:
        if v.lower() not in ("accept", "reject"):
            raise ValueError("action must be 'accept' or 'reject'")
        return v.lower()


class CollaborationRevoke(BaseInData):
    """Owner chamber revokes an accepted collaboration."""
    collaboration_id: str
    notes: Optional[str] = None
