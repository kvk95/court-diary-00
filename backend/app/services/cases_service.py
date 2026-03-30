"""cases_service.py — Business logic for Cases, Hearings, Case Notes, Case Clients"""

from datetime import date
from typing import List, Optional, Any, Callable, Dict, Iterable, TypeVar

from sqlalchemy import case, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.models.activity_log import ActivityLog
from app.database.models.case_clients import CaseClients
from app.database.models.case_notes import CaseNotes
from app.database.models.cases import Cases
from app.database.models.clients import Clients
from app.database.models.hearings import Hearings
from app.database.models.refm_case_status import RefmCaseStatus, RefmCaseStatusConstants
from app.database.models.refm_case_types import RefmCaseTypes
from app.database.models.refm_courts import RefmCourts
from app.database.models.refm_hearing_status import RefmHearingStatus
from app.database.models.refm_hearing_purpose import RefmHearingPurpose
from app.database.models.refm_party_roles import RefmPartyRoles
from app.database.models.users import Users
from app.database.repositories.case_clients_repository import CaseClientsRepository
from app.database.repositories.case_notes_repository import CaseNotesRepository
from app.database.repositories.cases_repository import CasesRepository
from app.database.repositories.hearings_repository import HearingsRepository
from app.dtos.base.paginated_out import PagingBuilder, PagingData
from app.dtos.cases_dto import (
    CaseClientLinkPayload,
    CaseClientOut,
    CaseCreate,
    CaseDelete,
    CaseDetailOut,
    CaseBasicInfoOut,
    CaseListOut,
    CaseEdit,
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
        self.cases_repo = cases_repo or CasesRepository()
        self.hearings_repo = hearings_repo or HearingsRepository()
        self.case_notes_repo = case_notes_repo or CaseNotesRepository()
        self.case_clients_repo = case_clients_repo or CaseClientsRepository()

    # ─────────────────────────────────────────────────────────────────────
    # HELPERS
    # ─────────────────────────────────────────────────────────────────────

    K = TypeVar("K")
    V = TypeVar("V")

    async def _load_map(
        self,
        ids: Iterable[K],
        query_builder: Callable[[list[K]], Any],
        key_fn: Callable[[Any], K],
        value_fn: Callable[[Any], V],
    ) -> Dict[K, V]:
        ids = list({i for i in ids if i})
        if not ids:
            return {}
        rows = (await self.session.execute(query_builder(ids))).all()
        return {key_fn(r): value_fn(r) for r in rows}

    async def _load_counts(
        self,
        field,
        case_ids,
        extra_filters=None,
    ) -> Dict[Any, int]:
        case_ids = list({c for c in case_ids if c})
        if not case_ids:
            return {}
        stmt = select(field, func.count()).where(field.in_(case_ids))
        if extra_filters:
            stmt = stmt.where(*extra_filters)
        stmt = stmt.group_by(field)
        rows = (await self.session.execute(stmt)).all()
        return {r[0]: r[1] for r in rows}

    # ─────────────────────────────────────────────
    # COMMON BULK ENRICHMENT
    # ─────────────────────────────────────────────

    async def _load_common_maps(self, cases: List[Cases]):
        return {
            "court_map": await self._load_map(
                (c.court_id for c in cases),
                lambda ids: select(RefmCourts.court_id, RefmCourts.court_name)
                .where(RefmCourts.court_id.in_(ids)),
                lambda r: r.court_id,
                lambda r: r.court_name,
            ),
            "aor_map": await self._load_map(
                (c.aor_user_id for c in cases),
                lambda ids: select(Users.user_id, Users.first_name, Users.last_name)
                .where(Users.user_id.in_(ids)),
                lambda r: r.user_id,
                lambda r: _full_name(r.first_name, r.last_name),
            ),
            "case_type_map": await self._load_map(
                (c.case_type_code for c in cases),
                lambda ids: select(RefmCaseTypes.code, RefmCaseTypes.description)
                .where(RefmCaseTypes.code.in_(ids)),
                lambda r: r.code,
                lambda r: r.description,
            ),
            "status_map": await self._load_map(
                (c.status_code for c in cases),
                lambda ids: select(RefmCaseStatus.code, RefmCaseStatus.description)
                .where(RefmCaseStatus.code.in_(ids)),
                lambda r: r.code,
                lambda r: r.description,
            ),
        }

    async def _get_case_or_404(self, case_id: str) -> Cases:
        case = await self.cases_repo.get_by_id(
            session=self.session,
            filters={Cases.case_id: case_id, Cases.chamber_id: self.chamber_id},
        )
        if not case:
            raise ValidationErrorDetail(code=ErrorCodes.NOT_FOUND, message="Case not found")
        return case

    # OPTIMISATION: lightweight existence check used when we don't need the full
    # ORM object (e.g. before listing sub-resources).  Avoids hydrating the entire
    # Cases row just to confirm ownership.
    async def _assert_case_exists(self, case_id: str) -> None:
        exists = await self.session.scalar(
            select(func.count(Cases.case_id)).where(
                Cases.case_id == case_id,
                Cases.chamber_id == self.chamber_id,
                Cases.deleted_ind.is_(False),
            )
        )
        if not exists:
            raise ValidationErrorDetail(code=ErrorCodes.NOT_FOUND, message="Case not found")

    async def _enrich_case_detail(self, case: Cases) -> CaseDetailOut:
        maps = await self._load_common_maps([case])

        hearing_map = await self._load_counts(
            Hearings.case_id,
            [case.case_id],
            [Hearings.deleted_ind.is_(False)],
        )
        note_map = await self._load_counts(
            CaseNotes.case_id,
            [case.case_id],
            [CaseNotes.deleted_ind.is_(False)],
        )
        client_map = await self._load_counts(CaseClients.case_id, [case.case_id])

        latest_hearing = await self.session.execute(
            select(Hearings.status_code)
            .where(
                Hearings.case_id == case.case_id,
                Hearings.deleted_ind.is_(False),
            )
            .order_by(Hearings.hearing_date.desc())
            .limit(1)
        )

        row = latest_hearing.first()
        latest_status = row[0] if row else None

        return CaseDetailOut(
            case_id=case.case_id,
            chamber_id=case.chamber_id,
            case_number=case.case_number,
            court_id=case.court_id,
            court_name=maps["court_map"].get(case.court_id),
            case_type_code=case.case_type_code,
            case_type_description=maps["case_type_map"].get(case.case_type_code),
            filing_year=case.filing_year,
            petitioner=case.petitioner,
            respondent=case.respondent,
            aor_user_id=case.aor_user_id,
            aor_name=maps["aor_map"].get(case.aor_user_id),
            case_summary=case.case_summary,
            status_code=case.status_code,
            status_description=maps["status_map"].get(case.status_code),
            next_hearing_date=case.next_hearing_date,
            last_hearing_date=case.last_hearing_date,
            next_hearing_status=latest_status,
            updated_date=case.updated_date,
            total_hearings=hearing_map.get(case.case_id, 0),
            linked_clients=client_map.get(case.case_id, 0),
            total_notes=note_map.get(case.case_id, 0),
        )

    # ─────────────────────────────────────────────────────────────────────
    # CASES — Stats
    # ─────────────────────────────────────────────────────────────────────

    async def cases_get_stats(self) -> CaseSummaryStats:
        # OPTIMISATION: replaced 4 separate scalar queries with a single
        # aggregation using conditional COUNT (CASE WHEN ... END).  One
        # round-trip instead of four.
        today = date.today()
        cid = self.chamber_id
        active_code = RefmCaseStatusConstants.ACTIVE
        adjourned_code = RefmCaseStatusConstants.ADJOURNED

        row = await self.session.execute(
            select(
                func.count(Cases.case_id).label("total"),
                func.count(
                    case((Cases.status_code == active_code, Cases.case_id), else_=None)
                ).label("active"),
                func.count(
                    case((Cases.status_code == adjourned_code, Cases.case_id), else_=None)
                ).label("adjourned"),
                func.count(
                    case(
                        (
                            (Cases.status_code == active_code)
                            & (Cases.next_hearing_date < today),
                            Cases.case_id,
                        ),
                        else_=None,
                    )
                ).label("overdue"),
            ).where(Cases.chamber_id == cid, Cases.deleted_ind.is_(False))
        )
        r = row.one()
        return CaseSummaryStats(
            total=r.total or 0,
            active=r.active or 0,
            adjourned=r.adjourned or 0,
            overdue=r.overdue or 0,
        )

    # ─────────────────────────────────────────────────────────────────────
    # CASES — Chamberwise
    # ─────────────────────────────────────────────────────────────────────

    async def list_cases_for_quick_hearing(
        self,
        search: Optional[str] = None,
        limit: int = 50,
    )->list[CaseBasicInfoOut]:
        
        rows = await self.cases_repo.list_cases_for_quick_hearing(
            session=self.session,
            search=search,
            limit=limit
        )       

        records = [
            CaseBasicInfoOut(
                case_id=c.case_id,
                chamber_id=c.chamber_id,
                case_number=c.case_number,
                court_id=c.court_id,
                court_name=await self.refm_resolver.from_column(
                    column_attr=RefmCourts.court_id,
                    code=c.court_id,
                    value_column=RefmCourts.court_name,
                    default=None
                ),
                status_code = c.status_code,
                status_description = await self.refm_resolver.from_column(
                    column_attr=RefmCaseStatus.code,
                    code=c.status_code,
                    value_column=RefmCaseStatus.description,
                    default=None
                ),
                case_type_code=c.case_type_code,
                case_type_description=await self.refm_resolver.from_column(
                    column_attr=RefmCaseTypes.code,
                    code=c.case_type_code,
                    value_column=RefmCaseTypes.description,
                    default=None
                ),

                filing_year=c.filing_year,

                petitioner=c.petitioner,
                respondent=c.respondent,

                aor_user_id=c.aor_user_id,
                aor_name=_full_name(first_name, last_name),
            )
            for (
                c,
                first_name,
                last_name,
            ) in rows
        ]

        return records

    # ─────────────────────────────────────────────────────────────────────
    # CASES — Paginated list
    # ─────────────────────────────────────────────────────────────────────

    async def cases_get_paged(
        self,
        page: int,
        limit: int,
        search: Optional[str] = None,
        status_code: Optional[str] = None,
        court_id: Optional[int] = None,
        sort_by: str = "updated_date",
    ) -> PagingData[CaseListOut]:

        rows, total = await self.cases_repo.list_cases_with_details(
            session=self.session,
            page=page,
            limit=limit,
            chamber_id=self.chamber_id,
            search=search,
            status_code=status_code,
            court_id=court_id,
            sort_by=sort_by,
        )

        records = [
            CaseListOut(
                case_id=c.case_id,
                chamber_id=c.chamber_id,
                case_number=c.case_number,
                
                status_code = c.status_code,
                status_description = await self.refm_resolver.from_column(
                    column_attr=Cases.status_code,
                    code=c.status_code,
                    value_column=RefmCaseStatus.description,
                    default=None
                ),
                court_id=c.court_id,
                court_name=await self.refm_resolver.from_column(
                    column_attr=Cases.court_id,
                    code=c.court_id,
                    value_column=RefmCourts.court_name,
                    default=None
                ),
                petitioner=c.petitioner,
                respondent=c.respondent,
                aor_user_id=c.aor_user_id,
                aor_name=_full_name(first_name, last_name),
                next_hearing_date=c.next_hearing_date,
                last_hearing_date=c.last_hearing_date,
                updated_date=c.updated_date,
                case_type_code=c.case_type_code,
                case_type_description=await self.refm_resolver.from_column(
                    column_attr=Cases.case_type_code,
                    code=c.case_type_code,
                    value_column=RefmCaseTypes.description,
                    default=None
                ),
                filing_year=c.filing_year,
                case_summary=c.case_summary,
                next_hearing_status=hearing_status_desc,
            )
            for (
                c,
                first_name,
                last_name,
                hearing_status_desc,
            ) in rows
        ]

        return PagingBuilder(total_records=total, page=page, limit=limit).build(records=records)

    # ─────────────────────────────────────────────────────────────────────
    # CASES — Detail / Add / Edit / Delete
    # ─────────────────────────────────────────────────────────────────────

    async def cases_get_by_id(self, case_id: str) -> CaseDetailOut:
        return await self._enrich_case_detail(await self._get_case_or_404(case_id))

    async def cases_add(self, payload: CaseCreate) -> CaseDetailOut:
        existing = await self.cases_repo.get_first(
            session=self.session,
            filters={Cases.chamber_id: self.chamber_id, Cases.case_number: payload.case_number},
        )
        if existing:
            raise ValidationErrorDetail(
                code=ErrorCodes.VALIDATION_ERROR,
                message=f"Case number '{payload.case_number}' already exists",
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
            metadata={"case_id": case.case_id},
        )
        return await self._enrich_case_detail(case)

    async def cases_edit(self, payload: CaseEdit) -> CaseDetailOut:
        case = await self._get_case_or_404(payload.case_id)
        data = payload.model_dump(exclude_unset=True, exclude_none=True)
        data.pop("case_id", None)
        if data:
            await self.cases_repo.update(
                session=self.session,
                id_values=payload.case_id,
                data=self.cases_repo.map_fields_to_db_column(data),
            )
        await log_activity(
            action="Case updated",
            target=f"case:{payload.case_id}:{case.case_number}",
            metadata={"updated_fields": list(data.keys())},
        )
        return await self.cases_get_by_id(payload.case_id)

    async def cases_delete(self, payload: CaseDelete) -> dict:
        case = await self._get_case_or_404(payload.case_id)
        await self.cases_repo.delete(session=self.session, id_values=payload.case_id, soft=True)
        await log_activity(action="Case deleted", target=f"case:{payload.case_id}:{case.case_number}")
        return {"case_id": payload.case_id, "deleted": True}

    # ─────────────────────────────────────────────────────────────────────
    # HEARINGS
    # ─────────────────────────────────────────────────────────────────────

    async def hearings_get_by_case(self, case_id: str) -> List[HearingOut]:
        # OPTIMISATION: use _assert_case_exists (COUNT query) instead of
        # _get_case_or_404 — we don't use the returned object here.
        await self._assert_case_exists(case_id)
        hearings = await self.hearings_repo.list_all(
            session=self.session,
            where=[
                Hearings.case_id == case_id,
                Hearings.chamber_id == self.chamber_id,
                Hearings.deleted_ind.is_(False),
            ],
            order_by=[Hearings.hearing_date.desc()],
        )

        # OPTIMISATION: reuse _load_map instead of duplicating the inline
        # execute/dict-comprehension pattern.
        status_map = await self._load_map(
            (h.status_code for h in hearings),
            lambda ids: select(RefmHearingStatus.code, RefmHearingStatus.description)
            .where(RefmHearingStatus.code.in_(ids)),
            lambda r: r.code,
            lambda r: r.description,
        )
        creator_map = await self._load_map(
            (h.created_by for h in hearings),
            lambda ids: select(Users.user_id, Users.first_name, Users.last_name)
            .where(Users.user_id.in_(ids)),
            lambda r: r.user_id,
            lambda r: _full_name(r.first_name, r.last_name),
        )

        purpose_map = await self._load_map(
            (h.purpose_code for h in hearings),
            lambda ids: select(RefmHearingPurpose.code, RefmHearingPurpose.description)
                .where(RefmHearingPurpose.code.in_(ids)),
            lambda r: r.code,
            lambda r: r.description,
        )

        return [
            HearingOut(
                hearing_id=h.hearing_id,
                case_id=h.case_id,
                hearing_date=h.hearing_date,
                status_code=h.status_code,
                status_description=status_map.get(h.status_code),

                purpose_code=h.purpose_code,                              # ✅
                purpose_description=purpose_map.get(h.purpose_code),      # ✅

                notes=h.notes,
                order_details=h.order_details,
                next_hearing_date=h.next_hearing_date,
                created_by_name=creator_map.get(h.created_by),
            )
            for h in hearings
        ]

    async def hearings_add(self, payload: HearingCreate) -> HearingOut:
        await self._assert_case_exists(payload.case_id)
        data = payload.model_dump(exclude_unset=True, exclude_none=True)
        data["chamber_id"] = self.chamber_id
        hearing = await self.hearings_repo.create(
            session=self.session,
            data=self.hearings_repo.map_fields_to_db_column(data),
        )
        if payload.next_hearing_date:
            await self.cases_repo.update(
                session=self.session,
                id_values=payload.case_id,
                data={
                    "next_hearing_date": payload.next_hearing_date,
                    "last_hearing_date": payload.hearing_date,
                },
            )
        await log_activity(
            action=f"Hearing added for {payload.hearing_date}",
            target=f"case:{payload.case_id}",
            metadata={"hearing_id": hearing.hearing_id},
        )
        status_desc = None
        if hearing.status_code:
            hs = await self.session.get(RefmHearingStatus, hearing.status_code)
            status_desc = hs.description if hs else None

        purpose_desc = None
        if hearing.purpose_code:
            p = await self.session.get(RefmHearingPurpose, hearing.purpose_code)
            purpose_desc = p.description if p else None

        return HearingOut(
            hearing_id=hearing.hearing_id,
            case_id=hearing.case_id,
            hearing_date=hearing.hearing_date,
            status_code=hearing.status_code,
            status_description=status_desc,
            purpose_code=hearing.purpose_code,
            purpose_description=purpose_desc,
            notes=hearing.notes,
            order_details=hearing.order_details,
            next_hearing_date=hearing.next_hearing_date,
        )

    async def hearings_edit(self, payload: HearingEdit) -> HearingOut:
        hearing = await self.hearings_repo.get_by_id(
            session=self.session,
            filters={Hearings.hearing_id: payload.hearing_id, Hearings.chamber_id: self.chamber_id},
        )
        if not hearing:
            raise ValidationErrorDetail(code=ErrorCodes.NOT_FOUND, message="Hearing not found")
        data = payload.model_dump(exclude_unset=True, exclude_none=True)
        data.pop("hearing_id", None)
        updated = (
            await self.hearings_repo.update(
                session=self.session,
                id_values=payload.hearing_id,
                data=self.hearings_repo.map_fields_to_db_column(data),
            )
            if data
            else hearing
        )
        if payload.next_hearing_date:
            await self.cases_repo.update(
                session=self.session,
                id_values=hearing.case_id,
                data={"next_hearing_date": payload.next_hearing_date},
            )
        await log_activity(action="Hearing updated", target=f"case:{hearing.case_id}")
        status_desc = None
        if updated.status_code:
            hs = await self.session.get(RefmHearingStatus, updated.status_code)
            status_desc = hs.description if hs else None        

        purpose_desc = None
        if hearing.purpose_code:
            p = await self.session.get(RefmHearingPurpose, hearing.purpose_code)
            purpose_desc = p.description if p else None

        return HearingOut(
            hearing_id=updated.hearing_id,
            case_id=updated.case_id,
            hearing_date=updated.hearing_date,
            status_code=updated.status_code,
            status_description=status_desc,
            purpose_code=hearing.purpose_code,
            purpose_description=purpose_desc,
            notes=updated.notes,
            order_details=updated.order_details,
            next_hearing_date=updated.next_hearing_date,
        )

    async def hearings_delete(self, payload: HearingDelete) -> dict:
        hearing = await self.hearings_repo.get_by_id(
            session=self.session,
            filters={Hearings.hearing_id: payload.hearing_id, Hearings.chamber_id: self.chamber_id},
        )
        if not hearing:
            raise ValidationErrorDetail(code=ErrorCodes.NOT_FOUND, message="Hearing not found")
        await self.hearings_repo.delete(session=self.session, id_values=payload.hearing_id, soft=True)
        await log_activity(action="Hearing deleted", target=f"case:{hearing.case_id}")
        return {"hearing_id": payload.hearing_id, "deleted": True}

    # ─────────────────────────────────────────────────────────────────────
    # CASE NOTES
    # ─────────────────────────────────────────────────────────────────────

    async def case_notes_get_by_case(self, case_id: str) -> List[CaseNoteOut]:
        # OPTIMISATION: lightweight existence check — result not used.
        await self._assert_case_exists(case_id)
        notes = await self.case_notes_repo.list_all(
            session=self.session,
            where=[
                CaseNotes.case_id == case_id,
                CaseNotes.chamber_id == self.chamber_id,
                CaseNotes.deleted_ind.is_(False),
            ],
            order_by=[CaseNotes.created_date.desc()],
        )
        author_map = await self._load_map(
            (n.user_id for n in notes),
            lambda ids: select(Users.user_id, Users.first_name, Users.last_name)
            .where(Users.user_id.in_(ids)),
            lambda r: r.user_id,
            lambda r: _full_name(r.first_name, r.last_name),
        )
        return [
            CaseNoteOut(
                note_id=n.note_id,
                case_id=n.case_id,
                user_id=n.user_id,
                author_name=author_map.get(n.user_id),
                note_text=n.note_text,
            )
            for n in notes
        ]

    async def case_notes_add(self, payload: CaseNoteCreate) -> CaseNoteOut:
        await self._assert_case_exists(payload.case_id)
        data = payload.model_dump(exclude_unset=True, exclude_none=True)
        data["chamber_id"] = self.chamber_id
        data["user_id"] = self.user_id
        print(f"f=====================data: {data}")
        mapped = self.case_notes_repo.map_fields_to_db_column(data)
        print("AFTER MAP:", mapped)
        note = await self.case_notes_repo.create(
            session=self.session,
            data=self.case_notes_repo.map_fields_to_db_column(data),
        )
        u = await self.session.get(Users, self.user_id)
        return CaseNoteOut(
            note_id=note.note_id,
            case_id=note.case_id,
            user_id=note.user_id,
            author_name=_full_name(u.first_name, u.last_name) if u else None,
            note_text=note.note_text,
            private_ind=bool(note.private_ind),
        )

    async def case_notes_edit(self, payload: CaseNoteEdit) -> CaseNoteOut:
        note = await self.case_notes_repo.get_by_id(
            session=self.session,
            filters={CaseNotes.note_id: payload.note_id, CaseNotes.chamber_id: self.chamber_id},
        )
        if not note:
            raise ValidationErrorDetail(code=ErrorCodes.NOT_FOUND, message="Note not found")
        if note.user_id != self.user_id:
            raise ValidationErrorDetail(
                code=ErrorCodes.VALIDATION_ERROR, message="You can only edit your own notes"
            )
        data = payload.model_dump(exclude_unset=True, exclude_none=True)
        data.pop("note_id", None)
        updated = await self.case_notes_repo.update(
            session=self.session,
            id_values=payload.note_id,
            data=self.case_notes_repo.map_fields_to_db_column(data),
        )
        # OPTIMISATION: fetch user once for the returned DTO; the original
        # code fetched it again even though note.user_id == updated.user_id.
        u = await self.session.get(Users, updated.user_id)
        return CaseNoteOut(
            note_id=updated.note_id,
            case_id=updated.case_id,
            user_id=updated.user_id,
            author_name=_full_name(u.first_name, u.last_name) if u else None,
            note_text=updated.note_text,
            private_ind=bool(updated.private_ind),
        )

    async def case_notes_delete(self, payload: CaseNoteDelete) -> dict:
        note = await self.case_notes_repo.get_by_id(
            session=self.session,
            filters={CaseNotes.note_id: payload.note_id, CaseNotes.chamber_id: self.chamber_id},
        )
        if not note:
            raise ValidationErrorDetail(code=ErrorCodes.NOT_FOUND, message="Note not found")
        await self.case_notes_repo.delete(session=self.session, id_values=payload.note_id, soft=True)
        return {"note_id": payload.note_id, "deleted": True}

    # ─────────────────────────────────────────────────────────────────────
    # CASE CLIENTS
    # ─────────────────────────────────────────────────────────────────────

    async def case_clients_get(self, case_id: str) -> List[CaseClientOut]:
        await self._assert_case_exists(case_id)
        rows = await self.session.execute(
            select(
                CaseClients.case_client_id,
                CaseClients.client_id,
                CaseClients.party_role,
                CaseClients.primary_ind,
                CaseClients.engagement_type,
                Clients.client_name,
                Clients.client_type,
                Clients.email,
                Clients.phone,
            )
            .join(Clients, CaseClients.client_id == Clients.client_id)
            .where(
                CaseClients.case_id == case_id,
                CaseClients.chamber_id == self.chamber_id,
            )
            .order_by(CaseClients.primary_ind.desc(), Clients.client_name.asc())
        )
        result_rows = rows.all()

        # OPTIMISATION: fetch only the role codes actually used in this case
        # rather than the entire RefmPartyRoles table.
        used_roles = {r.party_role for r in result_rows if r.party_role}
        role_map: dict = {}
        if used_roles:
            pr_rows = await self.session.execute(
                select(RefmPartyRoles.code, RefmPartyRoles.description).where(
                    RefmPartyRoles.code.in_(used_roles)
                )
            )
            role_map = {r.code: r.description for r in pr_rows}

        return [
            CaseClientOut(
                case_client_id=r.case_client_id,
                client_id=r.client_id,
                client_name=r.client_name,
                client_type=r.client_type,
                party_role=r.party_role,
                party_role_description=role_map.get(r.party_role),
                primary_ind=bool(r.primary_ind),
                engagement_type=r.engagement_type,
                email=r.email,
                phone=r.phone,
            )
            for r in result_rows
        ]

    async def case_clients_link(self, case_id: str, payload: CaseClientLinkPayload) -> CaseClientOut:
        await self._assert_case_exists(case_id)
        existing = await self.case_clients_repo.get_first(
            session=self.session,
            filters={
                CaseClients.case_id: case_id,
                CaseClients.client_id: payload.client_id,
                CaseClients.party_role: payload.party_role,
            },
        )
        if existing:
            raise ValidationErrorDetail(
                code=ErrorCodes.VALIDATION_ERROR,
                message=f"Client already linked to this case as {payload.party_role}",
            )
        link = await self.case_clients_repo.create(
            session=self.session,
            data={
                "chamber_id": self.chamber_id,
                "case_id": case_id,
                "client_id": payload.client_id,
                "party_role": payload.party_role,
                "primary_ind": payload.primary_ind,
                "engagement_type": payload.engagement_type,
            },
        )
        await log_activity(
            action="Client linked to case",
            target=f"case:{case_id}",
            metadata={"client_id": payload.client_id, "role": payload.party_role},
        )
        client = await self.session.get(Clients, payload.client_id)
        pr = await self.session.get(RefmPartyRoles, payload.party_role)
        return CaseClientOut(
            case_client_id=link.case_client_id,
            client_id=link.client_id,
            client_name=client.client_name if client else "",
            client_type=client.client_type if client else "",
            party_role=link.party_role,
            party_role_description=pr.description if pr else None,
            primary_ind=bool(link.primary_ind),
            engagement_type=link.engagement_type,
            email=client.email if client else None,
            phone=client.phone if client else None,
        )

    async def case_clients_unlink(self, case_id: str, case_client_id: str) -> dict:
        await self._assert_case_exists(case_id)
        link = await self.case_clients_repo.get_by_id(
            session=self.session,
            filters={CaseClients.case_client_id: case_client_id, CaseClients.case_id: case_id},
        )
        if not link:
            raise ValidationErrorDetail(code=ErrorCodes.NOT_FOUND, message="Client link not found")
        await self.case_clients_repo.delete(session=self.session, id_values=case_client_id, soft=False)
        await log_activity(action="Client unlinked from case", target=f"case:{case_id}")
        return {"case_client_id": case_client_id, "deleted": True}

    # ─────────────────────────────────────────────────────────────────────
    # RECENT ACTIVITY
    # ─────────────────────────────────────────────────────────────────────

    async def cases_get_recent_activity(self, case_id: str, limit: int = 10) -> List[RecentActivityItem]:
        try:
            rows = await self.session.execute(
                select(ActivityLog.action, ActivityLog.user_id, ActivityLog.created_date)
                .where(
                    ActivityLog.chamber_id == self.chamber_id,
                    ActivityLog.target.like(f"case:{case_id}%"),
                )
                .order_by(ActivityLog.created_date.desc())
                .limit(limit)
            )
            activity_rows = rows.fetchall()
        except Exception:
            return []

        actor_map = await self._load_map(
            (r.user_id for r in activity_rows),
            lambda ids: select(Users.user_id, Users.first_name, Users.last_name)
            .where(Users.user_id.in_(ids)),
            lambda r: r.user_id,
            lambda r: _full_name(r.first_name, r.last_name),
        )

        return [
            RecentActivityItem(
                action=r.action,
                actor_name=actor_map.get(r.user_id) if r.user_id else None,
                timestamp=r.created_date,
            )
            for r in activity_rows
        ]