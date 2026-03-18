from datetime import date
from typing import List, Optional
from sqlalchemy import func, select, or_
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.models.cases import Cases
from app.database.models.hearings import Hearings
from app.database.models.case_notes import CaseNotes
from app.database.models.case_clients import CaseClients
from app.database.models.users import Users
from app.database.models.refm_courts import RefmCourts
from app.database.models.refm_case_types import RefmCaseTypes
from app.database.models.refm_case_status import RefmCaseStatus, RefmCaseStatusConstants
from app.database.models.refm_hearing_status import RefmHearingStatus
from app.database.models.activity_log import ActivityLog
from app.database.repositories.cases_repository import CasesRepository
from app.database.repositories.hearings_repository import HearingsRepository
from app.database.repositories.case_notes_repository import CaseNotesRepository
from app.database.repositories.case_clients_repository import CaseClientsRepository
from app.dtos.base.paginated_out import PagingBuilder, PagingData
from app.dtos.cases_dto import (
    CaseCreate,
    CaseDelete,
    CaseDetailOut,
    CaseEdit,
    CaseListOut,
    CaseNoteCreate,
    CaseNoteDelete,
    CaseNoteEdit,
    CaseNoteOut,
    CaseSummaryStats,
    HearingCreate,
    HearingDelete,
    HearingEdit,
    HearingOut,
    RecentActivityItem,
)
from app.services.base.secured_base_service import BaseSecuredService
from app.utils.logging_framework.activity_logger import log_activity
from app.validators import ErrorCodes, ValidationErrorDetail


def _full_name(first: Optional[str], last: Optional[str]) -> Optional[str]:
    """Helper to concatenate first and last name."""
    parts = [p for p in [first, last] if p]
    return " ".join(parts) if parts else None


class CasesService(BaseSecuredService):
    def __init__(
        self,
        session: AsyncSession,
        cases_repo: Optional[CasesRepository] = None,
        hearings_repo: Optional[HearingsRepository] = None,
        case_notes_repo: Optional[CaseNotesRepository] = None,
        case_clients_repo: Optional[CaseClientsRepository] = None,
    ):
        super().__init__(session)
        self.cases_repo: CasesRepository = cases_repo or CasesRepository()
        self.hearings_repo: HearingsRepository = hearings_repo or HearingsRepository()
        self.case_notes_repo: CaseNotesRepository = case_notes_repo or CaseNotesRepository()
        self.case_clients_repo: CaseClientsRepository = case_clients_repo or CaseClientsRepository()

    # ─────────────────────────────────────────────────────────────────────────
    # CASES — Stats
    # ─────────────────────────────────────────────────────────────────────────
    async def cases_get_stats(self) -> CaseSummaryStats:
        """
        Returns the four stat cards: total, active, adjourned, overdue.
        Overdue = next_hearing_date < today AND status still active.
        """
        today = date.today()
        chamber_id = self.chamber_id

        # Total cases
        total_q = await self.session.scalar(
            select(func.count(Cases.case_id)).where(
                Cases.chamber_id == chamber_id,
                Cases.is_deleted.is_(False),
            )
        )

        # Active cases (status_code = 'AC')
        active_q = await self.session.scalar(
            select(func.count(Cases.case_id)).where(
                Cases.chamber_id == chamber_id,
                Cases.is_deleted.is_(False),
                Cases.status_code == RefmCaseStatusConstants.ACTIVE,
            )
        )

        # Adjourned cases (status_code = 'ADJ')
        adjourned_q = await self.session.scalar(
            select(func.count(Cases.case_id)).where(
                Cases.chamber_id == chamber_id,
                Cases.is_deleted.is_(False),
                Cases.status_code == RefmCaseStatusConstants.ADJOURNED,
            )
        )

        # Overdue cases (next_hearing_date < today AND status is active)
        overdue_q = await self.session.scalar(
            select(func.count(Cases.case_id)).where(
                Cases.chamber_id == chamber_id,
                Cases.is_deleted.is_(False),
                Cases.status_code == RefmCaseStatusConstants.ACTIVE,
                Cases.next_hearing_date < today,
            )
        )

        return CaseSummaryStats(
            total=total_q or 0,
            active=active_q or 0,
            adjourned=adjourned_q or 0,
            overdue=overdue_q or 0,
        )

    # ─────────────────────────────────────────────────────────────────────────
    # CASES — Paginated list
    # ─────────────────────────────────────────────────────────────────────────
    async def cases_get_paged(
        self,
        page: int,
        limit: int,
        search: Optional[str] = None,
        status_code: Optional[str] = None,
        court_id: Optional[int] = None,
        sort_by: str = "updated_date",
    ) -> PagingData[CaseListOut]:
        """
        Paginated case list with optional search (case number, petitioner, respondent)
        and filters (status, court).
        """
        conditions = [
            Cases.chamber_id == self.chamber_id,
            Cases.is_deleted.is_(False),
        ]

        if status_code and status_code.upper() != "ALL":
            conditions.append(Cases.status_code == status_code.upper())

        if court_id:
            conditions.append(Cases.court_id == court_id)

        if search and search.strip():
            kw = f"%{search.strip()}%"
            conditions.append(
                or_(
                    Cases.case_number.ilike(kw),
                    Cases.petitioner.ilike(kw),
                    Cases.respondent.ilike(kw),
                )
            )

        # Determine sort order
        if sort_by == "hearing_date":
            order_col = Cases.next_hearing_date.asc()
        elif sort_by == "case_number":
            order_col = Cases.case_number.asc()
        else:
            order_col = Cases.updated_date.desc()

        cases, total = await self.cases_repo.list_paginated(
            session=self.session,
            page=page,
            limit=limit,
            where=conditions,
            order_by=[order_col],
        )

        # Enrich with court names and AOR names in one pass
        court_ids = list({c.court_id for c in cases if c.court_id})
        aor_ids = list({c.aor_user_id for c in cases if c.aor_user_id})

        court_map: dict = {}
        if court_ids:
            rows = await self.session.execute(
                select(RefmCourts.court_id, RefmCourts.court_name).where(
                    RefmCourts.court_id.in_(court_ids)
                )
            )
            court_map = {r.court_id: r.court_name for r in rows}

        aor_map: dict = {}
        if aor_ids:
            rows = await self.session.execute(
                select(Users.user_id, Users.first_name, Users.last_name).where(
                    Users.user_id.in_(aor_ids)
                )
            )
            aor_map = {r.user_id: _full_name(r.first_name, r.last_name) for r in rows}

        records = [
            CaseListOut(
                case_id=c.case_id,
                case_number=c.case_number,
                status_code=c.status_code,
                court_name=court_map.get(c.court_id),
                petitioner=c.petitioner,
                respondent=c.respondent,
                aor_name=aor_map.get(c.aor_user_id) if c.aor_user_id else None,
                next_hearing_date=c.next_hearing_date,
                updated_date=c.updated_date,
            )
            for c in cases
        ]

        builder = PagingBuilder(total_records=total, page=page, limit=limit)
        return builder.build(records=records)

    # ─────────────────────────────────────────────────────────────────────────
    # CASES — Detail
    # ─────────────────────────────────────────────────────────────────────────
    async def cases_get_by_id(self, case_id: int) -> CaseDetailOut:
        case = await self.cases_repo.get_by_id(
            session=self.session,
            filters={Cases.case_id: case_id, Cases.chamber_id: self.chamber_id},
        )
        if not case:
            raise ValidationErrorDetail(
                code=ErrorCodes.NOT_FOUND, message="Case not found"
            )

        # Look up court, case type, status, AOR
        court_name: Optional[str] = None
        if case.court_id:
            court = await self.session.get(RefmCourts, case.court_id)
            court_name = court.court_name if court else None

        case_type_desc: Optional[str] = None
        if case.case_type_code:
            ct = await self.session.get(RefmCaseTypes, case.case_type_code)
            case_type_desc = ct.description if ct else None

        status_desc: Optional[str] = None
        if case.status_code:
            st = await self.session.get(RefmCaseStatus, case.status_code)
            status_desc = st.description if st else None

        aor_name: Optional[str] = None
        if case.aor_user_id:
            u = await self.session.get(Users, case.aor_user_id)
            aor_name = _full_name(u.first_name, u.last_name) if u else None

        # Counts for overview panel
        hearing_count = await self.session.scalar(
            select(func.count(Hearings.hearing_id)).where(
                Hearings.case_id == case_id,
                Hearings.is_deleted.is_(False),
            )
        ) or 0

        note_count = await self.session.scalar(
            select(func.count(CaseNotes.note_id)).where(
                CaseNotes.case_id == case_id,
                CaseNotes.is_deleted.is_(False),
            )
        ) or 0

        # Count linked clients
        client_count = await self.session.scalar(
            select(func.count(CaseClients.case_client_id)).where(
                CaseClients.case_id == case_id,
                CaseClients.is_deleted.is_(False),
            )
        ) or 0

        return CaseDetailOut(
            case_id=case.case_id,
            chamber_id=case.chamber_id,
            case_number=case.case_number,
            court_id=case.court_id,
            court_name=court_name,
            case_type_code=case.case_type_code,
            case_type_description=case_type_desc,
            filing_year=case.filing_year,
            petitioner=case.petitioner,
            respondent=case.respondent,
            aor_user_id=case.aor_user_id,
            aor_name=aor_name,
            case_summary=case.case_summary,
            status_code=case.status_code,
            status_description=status_desc,
            next_hearing_date=case.next_hearing_date,
            last_hearing_date=case.last_hearing_date,
            created_date=case.created_date,
            updated_date=case.updated_date,
            total_hearings=hearing_count,
            linked_clients=client_count,
            total_notes=note_count,
        )

    # ─────────────────────────────────────────────────────────────────────────
    # CASES — Create
    # ─────────────────────────────────────────────────────────────────────────
    async def cases_add(self, payload: CaseCreate) -> CaseDetailOut:
        # Duplicate case number check within chamber
        existing = await self.cases_repo.get_first(
            session=self.session,
            filters={
                Cases.chamber_id: self.chamber_id,
                Cases.case_number: payload.case_number,
            },
        )
        if existing:
            raise ValidationErrorDetail(
                code=ErrorCodes.VALIDATION_ERROR,
                message=f"Case number '{payload.case_number}' already exists in this chamber",
            )

        data = payload.model_dump(exclude_unset=True, exclude_none=True)
        data["chamber_id"] = self.chamber_id

        case = await self.cases_repo.create(
            session=self.session,
            data=self.cases_repo.map_fields_to_db_column(data),
        )

        await log_activity(
            action="Case created",
            target=f"case:{case.case_id}:{case.case_number}",
            metadata={"case_id": case.case_id, "case_number": case.case_number},
        )

        return await self.cases_get_by_id(case.case_id)

    # ─────────────────────────────────────────────────────────────────────────
    # CASES — Update
    # ─────────────────────────────────────────────────────────────────────────
    async def cases_edit(self, payload: CaseEdit) -> CaseDetailOut:
        case = await self.cases_repo.get_by_id(
            session=self.session,
            filters={Cases.case_id: payload.case_id, Cases.chamber_id: self.chamber_id},
        )
        if not case:
            raise ValidationErrorDetail(
                code=ErrorCodes.NOT_FOUND, message="Case not found"
            )

        data = payload.model_dump(exclude_unset=True, exclude_none=True)
        data.pop("case_id", None)

        await self.cases_repo.update(
            session=self.session,
            id_values=payload.case_id,
            data=self.cases_repo.map_fields_to_db_column(data),
        )

        await log_activity(
            action=f"Case updated — status: {payload.status_code or case.status_code}",
            target=f"case:{payload.case_id}:{case.case_number}",
            metadata={"case_id": payload.case_id, "updated_fields": list(data.keys())},
        )

        return await self.cases_get_by_id(payload.case_id)

    # ─────────────────────────────────────────────────────────────────────────
    # CASES — Delete (soft)
    # ─────────────────────────────────────────────────────────────────────────
    async def cases_delete(self, payload: CaseDelete) -> dict:
        case = await self.cases_repo.get_by_id(
            session=self.session,
            filters={Cases.case_id: payload.case_id, Cases.chamber_id: self.chamber_id},
        )
        if not case:
            raise ValidationErrorDetail(
                code=ErrorCodes.NOT_FOUND, message="Case not found"
            )

        await self.cases_repo.delete(
            session=self.session,
            id_values=payload.case_id,
            soft=True,
        )

        await log_activity(
            action="Case deleted",
            target=f"case:{payload.case_id}:{case.case_number}",
        )

        return {"case_id": payload.case_id, "deleted": True}

    # ─────────────────────────────────────────────────────────────────────────
    # HEARINGS — List for a case
    # ─────────────────────────────────────────────────────────────────────────
    async def hearings_get_by_case(self, case_id: int) -> List[HearingOut]:
        """All hearings for a case, newest first (by hearing_date DESC)."""
        # Verify case belongs to this chamber
        case = await self.cases_repo.get_by_id(
            session=self.session,
            filters={Cases.case_id: case_id, Cases.chamber_id: self.chamber_id},
        )
        if not case:
            raise ValidationErrorDetail(
                code=ErrorCodes.NOT_FOUND, message="Case not found"
            )

        hearings = await self.hearings_repo.list_all(
            session=self.session,
            where=[
                Hearings.case_id == case_id,
                Hearings.chamber_id == self.chamber_id,
                Hearings.is_deleted.is_(False),
            ],
            order_by=[Hearings.hearing_date.desc()],
        )

        # Enrich with hearing status description
        status_codes = list({h.status_code for h in hearings if h.status_code})
        status_map: dict = {}
        if status_codes:
            rows = await self.session.execute(
                select(RefmHearingStatus.code, RefmHearingStatus.description).where(
                    RefmHearingStatus.code.in_(status_codes)
                )
            )
            status_map = {r.code: r.description for r in rows}

        # Enrich created_by names
        creator_ids = list({h.created_by for h in hearings if h.created_by})
        creator_map: dict = {}
        if creator_ids:
            rows = await self.session.execute(
                select(Users.user_id, Users.first_name, Users.last_name).where(
                    Users.user_id.in_(creator_ids)
                )
            )
            creator_map = {r.user_id: _full_name(r.first_name, r.last_name) for r in rows}

        return [
            HearingOut(
                hearing_id=h.hearing_id,
                case_id=h.case_id,
                hearing_date=h.hearing_date,
                status_code=h.status_code,
                status_description=status_map.get(h.status_code) if h.status_code else None,
                purpose=h.purpose,
                notes=h.notes,
                order_details=h.order_details,
                next_hearing_date=h.next_hearing_date,
                created_by_name=creator_map.get(h.created_by) if h.created_by else None,
                created_date=h.created_date,
                updated_date=h.updated_date,
            )
            for h in hearings
        ]

    # ─────────────────────────────────────────────────────────────────────────
    # HEARINGS — Add
    # ─────────────────────────────────────────────────────────────────────────
    async def hearings_add(self, payload: HearingCreate) -> HearingOut:
        # Verify case belongs to this chamber
        case = await self.cases_repo.get_by_id(
            session=self.session,
            filters={Cases.case_id: payload.case_id, Cases.chamber_id: self.chamber_id},
        )
        if not case:
            raise ValidationErrorDetail(
                code=ErrorCodes.NOT_FOUND, message="Case not found"
            )

        data = payload.model_dump(exclude_unset=True, exclude_none=True)
        data["chamber_id"] = self.chamber_id

        hearing = await self.hearings_repo.create(
            session=self.session,
            data=self.hearings_repo.map_fields_to_db_column(data),
        )

        # Update case.next_hearing_date if the hearing has one
        if payload.next_hearing_date:
            await self.cases_repo.update(
                session=self.session,
                id_values=payload.case_id,
                data={"next_hearing_date": payload.next_hearing_date},
            )

        await log_activity(
            action=f"Hearing added for {payload.hearing_date}",
            target=f"case:{payload.case_id}",
            metadata={"hearing_id": hearing.hearing_id, "case_id": payload.case_id},
        )

        # Return enriched DTO
        status_desc: Optional[str] = None
        if hearing.status_code:
            hs = await self.session.get(RefmHearingStatus, hearing.status_code)
            status_desc = hs.description if hs else None

        return HearingOut(
            hearing_id=hearing.hearing_id,
            case_id=hearing.case_id,
            hearing_date=hearing.hearing_date,
            status_code=hearing.status_code,
            status_description=status_desc,
            purpose=hearing.purpose,
            notes=hearing.notes,
            order_details=hearing.order_details,
            next_hearing_date=hearing.next_hearing_date,
            created_date=hearing.created_date,
            updated_date=hearing.updated_date,
        )

    # ─────────────────────────────────────────────────────────────────────────
    # HEARINGS — Edit
    # ─────────────────────────────────────────────────────────────────────────
    async def hearings_edit(self, payload: HearingEdit) -> HearingOut:
        hearing = await self.hearings_repo.get_by_id(
            session=self.session,
            filters={
                Hearings.hearing_id: payload.hearing_id,
                Hearings.chamber_id: self.chamber_id,
            },
        )
        if not hearing:
            raise ValidationErrorDetail(
                code=ErrorCodes.NOT_FOUND, message="Hearing not found"
            )

        data = payload.model_dump(exclude_unset=True, exclude_none=True)
        data.pop("hearing_id", None)

        updated = await self.hearings_repo.update(
            session=self.session,
            id_values=payload.hearing_id,
            data=self.hearings_repo.map_fields_to_db_column(data),
        )

        await log_activity(
            action=f"Hearing {payload.hearing_id} updated",
            target=f"case:{hearing.case_id}",
        )

        status_desc: Optional[str] = None
        if updated.status_code:
            hs = await self.session.get(RefmHearingStatus, updated.status_code)
            status_desc = hs.description if hs else None

        return HearingOut(
            hearing_id=updated.hearing_id,
            case_id=updated.case_id,
            hearing_date=updated.hearing_date,
            status_code=updated.status_code,
            status_description=status_desc,
            purpose=updated.purpose,
            notes=updated.notes,
            order_details=updated.order_details,
            next_hearing_date=updated.next_hearing_date,
            created_date=updated.created_date,
            updated_date=updated.updated_date,
        )

    # ─────────────────────────────────────────────────────────────────────────
    # HEARINGS — Delete
    # ─────────────────────────────────────────────────────────────────────────
    async def hearings_delete(self, payload: HearingDelete) -> dict:
        hearing = await self.hearings_repo.get_by_id(
            session=self.session,
            filters={
                Hearings.hearing_id: payload.hearing_id,
                Hearings.chamber_id: self.chamber_id,
            },
        )
        if not hearing:
            raise ValidationErrorDetail(
                code=ErrorCodes.NOT_FOUND, message="Hearing not found"
            )

        await self.hearings_repo.delete(
            session=self.session,
            id_values=payload.hearing_id,
            soft=True,
        )

        await log_activity(
            action=f"Hearing {payload.hearing_id} deleted",
            target=f"case:{hearing.case_id}",
        )

        return {"hearing_id": payload.hearing_id, "deleted": True}

    # ─────────────────────────────────────────────────────────────────────────
    # CASE NOTES — List
    # ─────────────────────────────────────────────────────────────────────────
    async def case_notes_get_by_case(self, case_id: int) -> List[CaseNoteOut]:
        case = await self.cases_repo.get_by_id(
            session=self.session,
            filters={Cases.case_id: case_id, Cases.chamber_id: self.chamber_id},
        )
        if not case:
            raise ValidationErrorDetail(
                code=ErrorCodes.NOT_FOUND, message="Case not found"
            )

        notes = await self.case_notes_repo.list_all(
            session=self.session,
            where=[
                CaseNotes.case_id == case_id,
                CaseNotes.chamber_id == self.chamber_id,
                CaseNotes.is_deleted.is_(False),
            ],
            order_by=[CaseNotes.created_date.desc()],
        )

        # Enrich author names
        author_ids = list({n.user_id for n in notes if n.user_id})
        author_map: dict = {}
        if author_ids:
            rows = await self.session.execute(
                select(Users.user_id, Users.first_name, Users.last_name).where(
                    Users.user_id.in_(author_ids)
                )
            )
            author_map = {r.user_id: _full_name(r.first_name, r.last_name) for r in rows}

        return [
            CaseNoteOut(
                note_id=n.note_id,
                case_id=n.case_id,
                user_id=n.user_id,
                author_name=author_map.get(n.user_id),
                note_text=n.note_text,
                is_private=bool(n.is_private),
                created_date=n.created_date,
                updated_date=n.updated_date,
            )
            for n in notes
        ]

    # ─────────────────────────────────────────────────────────────────────────
    # CASE NOTES — Add
    # ─────────────────────────────────────────────────────────────────────────
    async def case_notes_add(self, payload: CaseNoteCreate) -> CaseNoteOut:
        case = await self.cases_repo.get_by_id(
            session=self.session,
            filters={Cases.case_id: payload.case_id, Cases.chamber_id: self.chamber_id},
        )
        if not case:
            raise ValidationErrorDetail(
                code=ErrorCodes.NOT_FOUND, message="Case not found"
            )

        data = payload.model_dump(exclude_unset=True, exclude_none=True)
        data["chamber_id"] = self.chamber_id
        data["user_id"] = self.user_id

        note = await self.case_notes_repo.create(
            session=self.session,
            data=self.case_notes_repo.map_fields_to_db_column(data),
        )

        # Fetch author name
        u = await self.session.get(Users, self.user_id)
        author_name = _full_name(u.first_name, u.last_name) if u else None

        return CaseNoteOut(
            note_id=note.note_id,
            case_id=note.case_id,
            user_id=note.user_id,
            author_name=author_name,
            note_text=note.note_text,
            is_private=bool(note.is_private),
            created_date=note.created_date,
            updated_date=note.updated_date,
        )

    # ─────────────────────────────────────────────────────────────────────────
    # CASE NOTES — Edit
    # ─────────────────────────────────────────────────────────────────────────
    async def case_notes_edit(self, payload: CaseNoteEdit) -> CaseNoteOut:
        note = await self.case_notes_repo.get_by_id(
            session=self.session,
            filters={
                CaseNotes.note_id: payload.note_id,
                CaseNotes.chamber_id: self.chamber_id,
            },
        )
        if not note:
            raise ValidationErrorDetail(
                code=ErrorCodes.NOT_FOUND, message="Note not found"
            )

        # Only the author can edit their own note
        if note.user_id != self.user_id:
            raise ValidationErrorDetail(
                code=ErrorCodes.VALIDATION_ERROR,
                message="You can only edit your own notes",
            )

        data = payload.model_dump(exclude_unset=True, exclude_none=True)
        data.pop("note_id", None)

        updated = await self.case_notes_repo.update(
            session=self.session,
            id_values=payload.note_id,
            data=self.case_notes_repo.map_fields_to_db_column(data),
        )

        u = await self.session.get(Users, updated.user_id)
        author_name = _full_name(u.first_name, u.last_name) if u else None

        return CaseNoteOut(
            note_id=updated.note_id,
            case_id=updated.case_id,
            user_id=updated.user_id,
            author_name=author_name,
            note_text=updated.note_text,
            is_private=bool(updated.is_private),
            created_date=updated.created_date,
            updated_date=updated.updated_date,
        )

    # ─────────────────────────────────────────────────────────────────────────
    # CASE NOTES — Delete
    # ─────────────────────────────────────────────────────────────────────────
    async def case_notes_delete(self, payload: CaseNoteDelete) -> dict:
        note = await self.case_notes_repo.get_by_id(
            session=self.session,
            filters={
                CaseNotes.note_id: payload.note_id,
                CaseNotes.chamber_id: self.chamber_id,
            },
        )
        if not note:
            raise ValidationErrorDetail(
                code=ErrorCodes.NOT_FOUND, message="Note not found"
            )

        await self.case_notes_repo.delete(
            session=self.session,
            id_values=payload.note_id,
            soft=True,
        )

        return {"note_id": payload.note_id, "deleted": True}

    # ─────────────────────────────────────────────────────────────────────────
    # CASE CLIENTS — Link client to case
    # ─────────────────────────────────────────────────────────────────────────
    async def link_client_to_case(
        self,
        case_id: int,
        client_id: int,
        party_role: str,
        is_primary: bool = False,
        engagement_type: Optional[str] = None,
    ) -> dict:
        """Link a client to a case."""
        # Verify case belongs to this chamber
        case = await self.cases_repo.get_by_id(
            session=self.session,
            filters={Cases.case_id: case_id, Cases.chamber_id: self.chamber_id},
        )
        if not case:
            raise ValidationErrorDetail(
                code=ErrorCodes.NOT_FOUND, message="Case not found"
            )

        # Check if client already linked with this role
        existing = await self.case_clients_repo.get_first(
            session=self.session,
            filters={
                CaseClients.case_id: case_id,
                CaseClients.client_id: client_id,
                CaseClients.party_role: party_role,
            },
        )
        if existing:
            raise ValidationErrorDetail(
                code=ErrorCodes.VALIDATION_ERROR,
                message=f"Client already linked to this case as {party_role}",
            )

        # Create link
        await self.case_clients_repo.create(
            session=self.session,
            data={
                "chamber_id": self.chamber_id,
                "case_id": case_id,
                "client_id": client_id,
                "party_role": party_role,
                "is_primary": is_primary,
                "engagement_type": engagement_type,
            },
        )

        await log_activity(
            action=f"Client {client_id} linked to case",
            target=f"case:{case_id}",
            metadata={
                "case_id": case_id,
                "client_id": client_id,
                "party_role": party_role,
            },
        )

        return {
            "case_id": case_id,
            "client_id": client_id,
            "party_role": party_role,
            "message": "Client linked successfully",
        }

    # ─────────────────────────────────────────────────────────────────────────
    # CASE CLIENTS — Unlink client from case
    # ─────────────────────────────────────────────────────────────────────────
    async def unlink_client_from_case(
        self,
        case_id: int,
        client_id: int,
    ) -> dict:
        """Remove a client from a case."""
        # Verify case belongs to this chamber
        case = await self.cases_repo.get_by_id(
            session=self.session,
            filters={Cases.case_id: case_id, Cases.chamber_id: self.chamber_id},
        )
        if not case:
            raise ValidationErrorDetail(
                code=ErrorCodes.NOT_FOUND, message="Case not found"
            )

        # Find the link
        link = await self.case_clients_repo.get_first(
            session=self.session,
            filters={
                CaseClients.case_id: case_id,
                CaseClients.client_id: client_id,
            },
        )
        if not link:
            raise ValidationErrorDetail(
                code=ErrorCodes.NOT_FOUND,
                message="Client not linked to this case",
            )

        await self.case_clients_repo.delete(
            session=self.session,
            id_values=link.case_client_id,
            soft=True,
        )

        await log_activity(
            action=f"Client {client_id} unlinked from case",
            target=f"case:{case_id}",
            metadata={"case_id": case_id, "client_id": client_id},
        )

        return {
            "case_id": case_id,
            "client_id": client_id,
            "message": "Client unlinked successfully",
        }

    # ─────────────────────────────────────────────────────────────────────────
    # CASE CLIENTS — Get clients for a case
    # ─────────────────────────────────────────────────────────────────────────
    async def get_case_clients(self, case_id: int) -> List[dict]:
        """Get all clients linked to a case."""
        # Verify case belongs to this chamber
        case = await self.cases_repo.get_by_id(
            session=self.session,
            filters={Cases.case_id: case_id, Cases.chamber_id: self.chamber_id},
        )
        if not case:
            raise ValidationErrorDetail(
                code=ErrorCodes.NOT_FOUND, message="Case not found"
            )

        # Get clients
        from app.database.models.clients import Clients

        rows = await self.session.execute(
            select(
                CaseClients,
                Clients.client_name,
                Clients.client_type,
                Clients.email,
                Clients.phone,
            )
            .join(Clients, CaseClients.client_id == Clients.client_id)
            .where(
                CaseClients.case_id == case_id,
                CaseClients.chamber_id == self.chamber_id,
                CaseClients.is_deleted.is_(False),
            )
        )

        return [
            {
                "case_client_id": row.CaseClients.case_client_id,
                "client_id": row.CaseClients.client_id,
                "client_name": row.client_name,
                "client_type": row.client_type,
                "party_role": row.CaseClients.party_role,
                "is_primary": row.CaseClients.is_primary,
                "engagement_type": row.CaseClients.engagement_type,
                "email": row.email,
                "phone": row.phone,
            }
            for row in rows
        ]

    # ─────────────────────────────────────────────────────────────────────────
    # RECENT ACTIVITY — Case detail sidebar
    # ─────────────────────────────────────────────────────────────────────────
    async def cases_get_recent_activity(
        self, case_id: int, limit: int = 10
    ) -> List[RecentActivityItem]:
        """
        Pull recent activity_log rows that reference this case.
        Falls back to an empty list if the activity log has no rows yet.
        """
        try:
            rows = await self.session.execute(
                select(
                    ActivityLog.action,
                    ActivityLog.user_id,
                    ActivityLog.timestamp,
                )
                .where(
                    ActivityLog.chamber_id == self.chamber_id,
                    ActivityLog.target.like(f"case:{case_id}%"),
                )
                .order_by(ActivityLog.timestamp.desc())
                .limit(limit)
            )
            activity_rows = rows.fetchall()
        except Exception:
            return []

        user_ids = list({r.user_id for r in activity_rows if r.user_id})
        actor_map: dict = {}
        if user_ids:
            urows = await self.session.execute(
                select(Users.user_id, Users.first_name, Users.last_name).where(
                    Users.user_id.in_(user_ids)
                )
            )
            actor_map = {r.user_id: _full_name(r.first_name, r.last_name) for r in urows}

        return [
            RecentActivityItem(
                action=r.action,
                actor_name=actor_map.get(r.user_id) if r.user_id else None,
                timestamp=r.timestamp,
            )
            for r in activity_rows
        ]