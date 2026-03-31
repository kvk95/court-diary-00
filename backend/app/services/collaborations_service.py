"""collaborations_service.py — Business logic for Case Collaboration (multi-chamber) module"""

from datetime import datetime
from typing import List, Optional

from sqlalchemy.ext.asyncio import AsyncSession

from app.database.models.case_collaborations import CaseCollaborations
from app.database.models.cases import Cases
from app.database.models.chamber import Chamber
from app.database.models.refm_collab_access import RefmCollabAccess
from app.database.models.refm_invitation_status import RefmInvitationStatus
from app.database.models.users import Users
from app.database.repositories.case_collaborations_repository import CaseCollaborationsRepository
from app.database.repositories.cases_repository import CasesRepository
from app.dtos.base.paginated_out import PagingBuilder, PagingData
from app.dtos.collaborations_dto import (
    CollaborationInvite,
    CollaborationOut,
    CollaborationRespond,
    CollaborationRevoke,
)
from app.services.base.secured_base_service import BaseSecuredService
from app.validators import ErrorCodes, ValidationErrorDetail


class CollaborationsService(BaseSecuredService):
    def __init__(
        self,
        session: AsyncSession,
        collabs_repo: Optional[CaseCollaborationsRepository] = None,
        cases_repo: Optional[CasesRepository] = None,
    ):
        super().__init__(session)
        self.collabs_repo = collabs_repo or CaseCollaborationsRepository()
        self.cases_repo = cases_repo or CasesRepository()

    # ─────────────────────────────────────────────────────────────────────
    # HELPERS
    # ─────────────────────────────────────────────────────────────────────

    async def _get_collab_or_404(self, collaboration_id: str) -> CaseCollaborations:
        c = await self.collabs_repo.get_by_id(
            session=self.session, id_values=collaboration_id
        )
        if not c:
            raise ValidationErrorDetail(code=ErrorCodes.NOT_FOUND, message="Collaboration not found")
        return c

    async def _chamber_name(self, chamber_id: str) -> Optional[str]:
        ch = await self.session.get(Chamber, chamber_id)
        return ch.chamber_name if ch else None

    async def _enrich(self, c: CaseCollaborations) -> CollaborationOut:
        # Case info
        case = await self.session.get(Cases, c.case_id)
        case_number = case.case_number if case else None
        case_title = f"{case.petitioner} vs {case.respondent}" if case else None

        # Chamber names
        owner_name = await self._chamber_name(c.owner_chamber_id)
        collab_name = await self._chamber_name(c.collaborator_chamber_id)

        # Access level description
        access_desc = None
        if c.access_level:
            al = await self.session.get(RefmCollabAccess, c.access_level)
            access_desc = al.description if al else None

        # Status description
        status_desc = None
        if c.status_code:
            st = await self.session.get(RefmInvitationStatus, c.status_code)
            status_desc = st.description if st else None

        # Invited by name
        invited_by_name = None
        if c.invited_by:
            u = await self.session.get(Users, c.invited_by)
            invited_by_name = self.full_name(u.first_name, u.last_name) if u else None

        return CollaborationOut(
            collaboration_id=c.collaboration_id,
            case_id=c.case_id,
            case_number=case_number,
            case_title=case_title,
            owner_chamber_id=c.owner_chamber_id,
            owner_chamber_name=owner_name,
            collaborator_chamber_id=c.collaborator_chamber_id,
            collaborator_chamber_name=collab_name,
            access_level=c.access_level,
            access_level_description=access_desc,
            invited_by=c.invited_by,
            invited_by_name=invited_by_name,
            invited_date=c.invited_date,
            accepted_date=c.accepted_date,
            status_code=c.status_code,
            status_description=status_desc,
            notes=c.notes,
            created_date=c.created_date,
        )

    # ─────────────────────────────────────────────────────────────────────
    # OUTGOING — collaborations this chamber has sent (as owner)
    # ─────────────────────────────────────────────────────────────────────

    async def collabs_get_outgoing(
        self, page: int, limit: int, status: Optional[str] = None
    ) -> PagingData[CollaborationOut]:
        conditions = [CaseCollaborations.owner_chamber_id == self.chamber_id]
        if status:
            conditions.append(CaseCollaborations.status_code == status)

        collabs, total = await self.collabs_repo.list_paginated(
            session=self.session, page=page, limit=limit,
            where=conditions,
            order_by=[CaseCollaborations.invited_date.desc()],
        )
        records = [await self._enrich(c) for c in collabs]
        return PagingBuilder(total_records=total, page=page, limit=limit).build(records=records)

    # ─────────────────────────────────────────────────────────────────────
    # INCOMING — collaborations this chamber has received (as collaborator)
    # ─────────────────────────────────────────────────────────────────────

    async def collabs_get_incoming(
        self, page: int, limit: int, status: Optional[str] = None
    ) -> PagingData[CollaborationOut]:
        conditions = [CaseCollaborations.collaborator_chamber_id == self.chamber_id]
        if status:
            conditions.append(CaseCollaborations.status_code == status)

        collabs, total = await self.collabs_repo.list_paginated(
            session=self.session, page=page, limit=limit,
            where=conditions,
            order_by=[CaseCollaborations.invited_date.desc()],
        )
        records = [await self._enrich(c) for c in collabs]
        return PagingBuilder(total_records=total, page=page, limit=limit).build(records=records)

    # ─────────────────────────────────────────────────────────────────────
    # GET FOR A CASE (both directions)
    # ─────────────────────────────────────────────────────────────────────

    async def collabs_get_by_case(self, case_id: str) -> List[CollaborationOut]:
        """All active collaborations where this chamber is the owner for this case."""
        collabs = await self.collabs_repo.list_all(
            session=self.session,
            where=[
                CaseCollaborations.case_id == case_id,
                CaseCollaborations.owner_chamber_id == self.chamber_id,
            ],
            order_by=[CaseCollaborations.invited_date.desc()],
        )
        return [await self._enrich(c) for c in collabs]

    # ─────────────────────────────────────────────────────────────────────
    # INVITE
    # ─────────────────────────────────────────────────────────────────────

    async def collabs_invite(self, payload: CollaborationInvite) -> CollaborationOut:
        # Verify case belongs to this chamber
        case = await self.cases_repo.get_by_id(
            session=self.session,
            filters={Cases.case_id: payload.case_id, Cases.chamber_id: self.chamber_id},
        )
        if not case:
            raise ValidationErrorDetail(code=ErrorCodes.NOT_FOUND, message="Case not found")

        # Can't invite yourself
        if payload.collaborator_chamber_id == self.chamber_id:
            raise ValidationErrorDetail(
                code=ErrorCodes.VALIDATION_ERROR,
                message="Cannot invite your own chamber",
            )

        # Collaborator chamber must exist
        target = await self.session.get(Chamber, payload.collaborator_chamber_id)
        if not target:
            raise ValidationErrorDetail(
                code=ErrorCodes.NOT_FOUND,
                message="Target chamber not found",
            )

        # Prevent duplicate active/pending invitations
        existing = await self.collabs_repo.get_first(
            session=self.session,
            filters={
                CaseCollaborations.case_id: payload.case_id,
                CaseCollaborations.owner_chamber_id: self.chamber_id,
                CaseCollaborations.collaborator_chamber_id: payload.collaborator_chamber_id,
                CaseCollaborations.status_code: "PN",
            },
        )
        if existing:
            raise ValidationErrorDetail(
                code=ErrorCodes.VALIDATION_ERROR,
                message="A pending invitation already exists for this chamber and case",
            )

        collab = await self.collabs_repo.create(
            session=self.session,
            data={
                "case_id": payload.case_id,
                "owner_chamber_id": self.chamber_id,
                "collaborator_chamber_id": payload.collaborator_chamber_id,
                "access_level": payload.access_level,
                "invited_by": self.user_id,
                "status_code": "PN",
                "notes": payload.notes,
                "created_by": self.user_id,
            },
        )
        return await self._enrich(collab)

    # ─────────────────────────────────────────────────────────────────────
    # RESPOND (accept / reject) — collaborator chamber action
    # ─────────────────────────────────────────────────────────────────────

    async def collabs_respond(self, payload: CollaborationRespond) -> CollaborationOut:
        c = await self._get_collab_or_404(payload.collaboration_id)

        # Only the collaborator chamber can respond
        if c.collaborator_chamber_id != self.chamber_id:
            raise ValidationErrorDetail(
                code=ErrorCodes.VALIDATION_ERROR,
                message="Only the invited chamber can respond to this invitation",
            )

        if c.status_code != "PN":
            raise ValidationErrorDetail(
                code=ErrorCodes.VALIDATION_ERROR,
                message=f"Invitation is already '{c.status_code}', cannot respond",
            )

        new_status = "AC" if payload.action == "accept" else "RJ"
        update: dict = {"status_code": new_status, "updated_by": self.user_id}
        if new_status == "AC":
            update["accepted_date"] = datetime.now()
        if payload.notes:
            update["notes"] = payload.notes

        updated = await self.collabs_repo.update(
            session=self.session, id_values=payload.collaboration_id, data=update
        )
        return await self._enrich(updated)

    # ─────────────────────────────────────────────────────────────────────
    # REVOKE — owner chamber cancels an accepted or pending collaboration
    # ─────────────────────────────────────────────────────────────────────

    async def collabs_revoke(self, payload: CollaborationRevoke) -> CollaborationOut:
        c = await self._get_collab_or_404(payload.collaboration_id)

        if c.owner_chamber_id != self.chamber_id:
            raise ValidationErrorDetail(
                code=ErrorCodes.VALIDATION_ERROR,
                message="Only the owning chamber can revoke a collaboration",
            )

        if c.status_code not in ("PN", "AC"):
            raise ValidationErrorDetail(
                code=ErrorCodes.VALIDATION_ERROR,
                message=f"Collaboration is already '{c.status_code}', cannot revoke",
            )

        updated = await self.collabs_repo.update(
            session=self.session,
            id_values=payload.collaboration_id,
            data={
                "status_code": "RV",
                "notes": payload.notes or c.notes,
                "updated_by": self.user_id,
            },
        )
        return await self._enrich(updated)
