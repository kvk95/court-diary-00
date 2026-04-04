"""cases_service.py — Business logic for Cases, Hearings, Case Notes, Case Clients"""

from datetime import date
from typing import List, Optional, Any, Callable, Dict, Iterable, TypeVar

from sqlalchemy import and_, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.models.activity_log import ActivityLog
from app.database.models.case_aors import CaseAors
from app.database.models.case_clients import CaseClients
from app.database.models.case_notes import CaseNotes
from app.database.models.cases import Cases
from app.database.models.clients import Clients
from app.database.models.hearings import Hearings
from app.database.models.profile_images import ProfileImages
from app.database.models.refm_aor_status import RefmAorStatus
from app.database.models.refm_case_status import RefmCaseStatus
from app.database.models.refm_case_types import RefmCaseTypes
from app.database.models.refm_client_type import RefmClientType
from app.database.models.refm_courts import RefmCourts
from app.database.models.refm_hearing_status import RefmHearingStatus
from app.database.models.refm_hearing_purpose import RefmHearingPurpose
from app.database.models.refm_party_roles import RefmPartyRoles
from app.database.models.refm_party_type import RefmPartyType
from app.database.models.users import Users
from app.database.repositories.case_clients_repository import CaseClientsRepository
from app.database.repositories.case_notes_repository import CaseNotesRepository
from app.database.repositories.cases_repository import CasesRepository
from app.database.repositories.hearings_repository import HearingsRepository
from app.dtos.aor_dto import AorOut
from app.dtos.base.paginated_out import PagingBuilder, PagingData
from app.dtos.cases_dto import (
    CaseClientLinkPayload,
    CaseClientLinkedOut,
    CaseClientOut,
    CaseCreate,
    CaseDelete,
    CaseDetailOut,
    CaseListOut,
    CaseEdit,
    CaseNoteCreate,
    CaseNoteDelete,
    CaseNoteEdit,
    CaseNoteOut,
    CaseQuickHearingOut,
    CaseSummaryStats,
    HearingCreate,
    HearingDelete,
    HearingEdit,
    HearingOut,
    RecentActivityItem,
)
from app.dtos.clients_dto import ClientDetailsOut
from app.services.base.secured_base_service import BaseSecuredService
from app.utils.activity_formatter import format_activity
from app.utils.logging_framework.activity_logger import log_activity
from app.validators import ErrorCodes, ValidationErrorDetail


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
        rows = (await self.cases_repo.execute( session=self.session, stmt=stmt)).all()        
        return {r[0]: r[1] for r in rows}

    # ─────────────────────────────────────────────
    # COMMON BULK ENRICHMENT
    # ─────────────────────────────────────────────

    async def _load_primary_aor_map(self, case_ids):
        case_ids = list({c for c in case_ids if c})
        if not case_ids:
            return {}

        rows = await self.session.execute(
            select(
                CaseAors.case_id,
                Users.user_id,
                Users.first_name,
                Users.last_name,
            )
            .join(Users, CaseAors.user_id == Users.user_id)
            .where(
                CaseAors.case_id.in_(case_ids),
                CaseAors.primary_ind.is_(True),
                CaseAors.withdrawal_date.is_(None),
            )
        )

        return {
            r.case_id: {
                "user_id": r.user_id,
                "name": self.full_name(r.first_name, r.last_name),
            }
            for r in rows
        }

    async def _load_common_maps(self, cases: List[Cases]):
        return {
            "court_map": await self._load_map(
                (c.court_id for c in cases),
                lambda ids: select(RefmCourts.court_id, RefmCourts.court_name)
                .where(RefmCourts.court_id.in_(ids)),
                lambda r: r.court_id,
                lambda r: r.court_name,
            ),
            "aor_map": await self._load_primary_aor_map(
                (c.case_id for c in cases)
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

    async def _get_case_details(self, case_id: str) -> Cases:
        case = await self.cases_repo.get_case_details(
            session=self.session,
            case_id = case_id)
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

        # ── Counts ──────────────────────────────────────────────────────────────
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

        # ── Latest hearing status ────────────────────────────────────────────────
        latest_row = (await self.session.execute(
            select(Hearings.status_code)
            .where(
                Hearings.case_id == case.case_id,
                Hearings.deleted_ind.is_(False),
            )
            .order_by(Hearings.hearing_date.desc())
            .limit(1)
        )).first()
        latest_status = latest_row[0] if latest_row else None

        # ── Case clients + client details ────────────────────────────────────────
        cc_rows = (await self.session.execute(
            select(CaseClients, Clients, ProfileImages.image_id, ProfileImages.image_data)
            .join(Clients, CaseClients.client_id == Clients.client_id)
            .outerjoin(
                ProfileImages,
                and_(
                    ProfileImages.client_id == Clients.client_id,
                    ProfileImages.deleted_ind.is_(False),
                )
            )
            .where(
                CaseClients.case_id == case.case_id,
                CaseClients.chamber_id == self.chamber_id,
            )
            .order_by(CaseClients.primary_ind.desc(), Clients.client_name.asc())
        )).all()

        # Batch-resolve reference codes for clients
        used_party_roles  = {r.CaseClients.party_role_code for r in cc_rows if r.CaseClients.party_role_code}
        used_client_types = {r.Clients.client_type_code    for r in cc_rows if r.Clients.client_type_code}
        used_party_types  = {r.Clients.party_type_code     for r in cc_rows if r.Clients.party_type_code}

        party_role_map = {}
        if used_party_roles:
            pr_rows = await self.session.execute(
                select(RefmPartyRoles.code, RefmPartyRoles.description)
                .where(RefmPartyRoles.code.in_(used_party_roles))
            )
            party_role_map = {r.code: r.description for r in pr_rows}

        client_type_map = {}
        if used_client_types:
            clt_rows = await self.session.execute(
                select(RefmClientType.code, RefmClientType.description)
                .where(RefmClientType.code.in_(used_client_types))
            )
            client_type_map = {r.code: r.description for r in clt_rows}

        party_type_map = {}
        if used_party_types:
            pt_rows = await self.session.execute(
                select(RefmPartyType.code, RefmPartyType.description)
                .where(RefmPartyType.code.in_(used_party_types))
            )
            party_type_map = {r.code: r.description for r in pt_rows}

        case_clients_out: List[CaseClientOut] = []
        clients_out: List[ClientDetailsOut] = []

        for row in cc_rows:
            cc: CaseClients = row.CaseClients
            cl: Clients     = row.Clients

            case_clients_out.append(CaseClientOut(
                case_client_id=cc.case_client_id,
                chamber_id=cc.chamber_id,
                case_id=cc.case_id,
                client_id=cc.client_id,
                party_role_code=cc.party_role_code,
                party_role_description=party_role_map.get(cc.party_role_code, ''),
                primary_ind=bool(cc.primary_ind),
            ))

            clients_out.append(ClientDetailsOut(
                image_id=row.image_id,
                image_data=row.image_data,
                case_client_id=cc.case_client_id,
                client_id=cl.client_id,
                chamber_id=cl.chamber_id,
                client_type_code=cl.client_type_code,
                client_type_description=client_type_map.get(cl.client_type_code,""),
                party_type_code=cl.party_type_code,
                party_type_description=party_type_map.get(cl.party_type_code,""),
                client_name=cl.client_name,
                display_name=cl.display_name,
                contact_person=cl.contact_person,
                phone=cl.phone,
                email=cl.email,
                alternate_phone=cl.alternate_phone,
                address_line1=cl.address_line1,
                address_line2=cl.address_line2,
                city=cl.city,
                state_code=cl.state_code,
                postal_code=cl.postal_code,
                country_code=cl.country_code,
                id_proof_code=cl.id_proof_code,
                id_proof_number=cl.id_proof_number,
                source_code=cl.source_code,
                referral_source=cl.referral_source,
                client_since=cl.client_since,
                notes=cl.notes,
                created_date=cl.created_date,
                updated_date=cl.updated_date,
            ))

        # ── AOR details ──────────────────────────────────────────────────────────
        aor_rows = (await self.session.execute(
            select(
                CaseAors,
                Users.first_name,
                Users.last_name,
                ProfileImages.image_id,
                ProfileImages.image_data,
            )
            .join(Users, CaseAors.user_id == Users.user_id)
            .outerjoin(
                ProfileImages,
                and_(
                    ProfileImages.user_id == CaseAors.user_id,
                    ProfileImages.deleted_ind.is_(False),
                )
            )
            .where(
                CaseAors.case_id == case.case_id,
                CaseAors.chamber_id == self.chamber_id,
                CaseAors.withdrawal_date.is_(None),
            )
            .order_by(CaseAors.primary_ind.desc(), CaseAors.appointment_date.asc())
        )).all()

        used_aor_statuses = {r.CaseAors.status_code for r in aor_rows if r.CaseAors.status_code}
        aor_status_map = {}
        if used_aor_statuses:
            as_rows = await self.session.execute(
                select(RefmAorStatus.code, RefmAorStatus.description)
                .where(RefmAorStatus.code.in_(used_aor_statuses))
            )
            aor_status_map = {r.code: r.description for r in as_rows}

        aor_details_out: List[AorOut] = [
            AorOut(
                case_aor_id=r.CaseAors.case_aor_id,
                case_id=r.CaseAors.case_id,
                chamber_id=r.CaseAors.chamber_id,
                user_id=r.CaseAors.user_id,
                advocate_name=self.full_name(r.first_name, r.last_name),
                primary_ind=bool(r.CaseAors.primary_ind),
                status_code=r.CaseAors.status_code,
                status_description=aor_status_map.get(r.CaseAors.status_code),
                appointment_date=r.CaseAors.appointment_date,
                withdrawal_date=r.CaseAors.withdrawal_date,
                notes=r.CaseAors.notes,
                created_date=r.CaseAors.created_date,
                image_id=r.image_id,
                image_data=r.image_data,
            )
            for r in aor_rows
        ]

        primary_aor = next((a for a in aor_details_out if a.primary_ind), None)
        aor_user_id = primary_aor.user_id if primary_aor else None
        aor_name = primary_aor.advocate_name if primary_aor else ''

        # ── Assemble ─────────────────────────────────────────────────────────────
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
            case_summary=case.case_summary,
            status_code=case.status_code,
            status_description=maps["status_map"].get(case.status_code),
            case_client_id = case_clients_out[0].case_client_id if case_clients_out else '',
            next_hearing_date=case.next_hearing_date,
            last_hearing_date=case.last_hearing_date,
            next_hearing_status=latest_status,
            updated_date=case.updated_date,
            total_hearings=hearing_map.get(case.case_id, 0),
            linked_clients=client_map.get(case.case_id, 0),
            total_notes=note_map.get(case.case_id, 0),
            case_clients=case_clients_out,
            clients=clients_out,
            aor_details=aor_details_out,
            # ── from CaseQuickHearingOut ─────────────────────────────────────────
            aor_user_id=aor_user_id or '',
            aor_name=aor_name or '',
            party_role_code=case_clients_out[0].party_role_code if case_clients_out else '',
            party_role_description=next(
                (cc.party_role_description for cc in case_clients_out if cc.primary_ind),
                case_clients_out[0].party_role_description if case_clients_out else '',
            ),
        )

    # ─────────────────────────────────────────────────────────────────────
    # CASES — Stats
    # ─────────────────────────────────────────────────────────────────────

    async def cases_get_stats(self) -> CaseSummaryStats:
        # OPTIMISATION: replaced 4 separate scalar queries with a single
        # aggregation using conditional COUNT (CASE WHEN ... END).  One
        # round-trip instead of four.
        today = date.today()

        r = await self.cases_repo.get_case_summary(self.session,today)
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
    ) -> list[CaseQuickHearingOut]:

        rows = await self.cases_repo.list_cases_for_quick_hearing(
            session=self.session,
            chamber_id=self.chamber_id,
            search=search,
            limit=limit,
        )

        used_court_ids   = {r.Cases.court_id          for r in rows if r.Cases.court_id}
        used_statuses    = {r.Cases.status_code        for r in rows if r.Cases.status_code}
        used_case_types  = {r.Cases.case_type_code     for r in rows if r.Cases.case_type_code}
        used_party_roles = {r.party_role_code          for r in rows if r.party_role_code}

        print(f"******************{used_party_roles}")
        for party in used_party_roles:
            print(f"***********8party{party}")

        for r in rows:
            print(f"ROW party_role_code={r.party_role_code!r}  aor_user_id={r.aor_user_id!r}")

        court_map = {}
        if used_court_ids:
            q = await self.session.execute(
                select(RefmCourts.court_id, RefmCourts.court_name)
                .where(RefmCourts.court_id.in_(used_court_ids))
            )
            court_map = {r.court_id: r.court_name for r in q}

        status_map = {}
        if used_statuses:
            q = await self.session.execute(
                select(RefmCaseStatus.code, RefmCaseStatus.description)
                .where(RefmCaseStatus.code.in_(used_statuses))
            )
            status_map = {r.code: r.description for r in q}

        case_type_map = {}
        if used_case_types:
            q = await self.session.execute(
                select(RefmCaseTypes.code, RefmCaseTypes.description)
                .where(RefmCaseTypes.code.in_(used_case_types))
            )
            case_type_map = {r.code: r.description for r in q}

        party_role_map = {}
        if used_party_roles:
            q = await self.session.execute(
                select(RefmPartyRoles.code, RefmPartyRoles.description)
                .where(RefmPartyRoles.code.in_(used_party_roles))
            )
            party_role_map = {r.code: r.description for r in q}

        return [
            CaseQuickHearingOut(
                case_id=r.Cases.case_id,
                chamber_id=r.Cases.chamber_id,
                case_number=r.Cases.case_number,
                court_id=r.Cases.court_id,
                court_name=court_map.get(r.Cases.court_id),
                status_code=r.Cases.status_code,
                status_description=status_map.get(r.Cases.status_code),
                case_type_code=r.Cases.case_type_code,
                case_type_description=case_type_map.get(r.Cases.case_type_code),
                filing_year=r.Cases.filing_year,
                petitioner=r.Cases.petitioner,
                respondent=r.Cases.respondent,
                aor_user_id='', #r.aor_user_id,
                aor_name=self.full_name(r.first_name, r.last_name),
                party_role_code='',#r.party_role_code,
                party_role_description=party_role_map.get(r.party_role_code,''),
            )
            for r in rows
        ]

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

        # Batch collect
        used_court_ids      = {r.Cases.court_id              for r in rows if r.Cases.court_id}
        used_case_statuses  = {r.Cases.status_code           for r in rows if r.Cases.status_code}
        used_case_types     = {r.Cases.case_type_code        for r in rows if r.Cases.case_type_code}
        used_hearing_status = {r.hearing_status_code         for r in rows if r.hearing_status_code}
        used_party_roles    = {r.party_role_code             for r in rows if r.party_role_code}

        court_map = {}
        if used_court_ids:
            q = await self.session.execute(
                select(RefmCourts.court_id, RefmCourts.court_name)
                .where(RefmCourts.court_id.in_(used_court_ids))
            )
            court_map = {r.court_id: r.court_name for r in q}

        status_map = {}
        if used_case_statuses:
            q = await self.session.execute(
                select(RefmCaseStatus.code, RefmCaseStatus.description)
                .where(RefmCaseStatus.code.in_(used_case_statuses))
            )
            status_map = {r.code: r.description for r in q}

        case_type_map = {}
        if used_case_types:
            q = await self.session.execute(
                select(RefmCaseTypes.code, RefmCaseTypes.description)
                .where(RefmCaseTypes.code.in_(used_case_types))
            )
            case_type_map = {r.code: r.description for r in q}

        hearing_status_map = {}
        if used_hearing_status:
            q = await self.session.execute(
                select(RefmHearingStatus.code, RefmHearingStatus.description)
                .where(RefmHearingStatus.code.in_(used_hearing_status))
            )
            hearing_status_map = {r.code: r.description for r in q}

        party_role_map = {}
        if used_party_roles:
            q = await self.session.execute(
                select(RefmPartyRoles.code, RefmPartyRoles.description)
                .where(RefmPartyRoles.code.in_(used_party_roles))
            )
            party_role_map = {r.code: r.description for r in q}

        records = [
            CaseListOut(
                case_id=c.case_id,
                chamber_id=c.chamber_id,
                case_number=c.case_number,
                court_id=c.court_id,
                court_name=court_map.get(c.court_id),
                status_code=c.status_code,
                status_description=status_map.get(c.status_code),
                case_type_code=c.case_type_code,
                case_type_description=case_type_map.get(c.case_type_code),
                filing_year=c.filing_year,
                case_summary=c.case_summary,
                petitioner=c.petitioner,
                respondent=c.respondent,
                aor_user_id=aor_user_id or '',
                aor_name=self.full_name(first_name, last_name),
                party_role_code=party_role_code or '',
                party_role_description=party_role_map.get(party_role_code, ""),
                case_client_id=case_client_id or '',
                next_hearing_date=c.next_hearing_date,
                last_hearing_date=c.last_hearing_date,
                next_hearing_status=hearing_status_map.get(hearing_status_code),
                updated_date=c.updated_date,
            )
            for c, first_name, last_name, hearing_status_code, party_role_code,case_client_id, aor_user_id in rows
        ]

        return PagingBuilder(total_records=total, page=page, limit=limit).build(records=records)

    # ─────────────────────────────────────────────────────────────────────
    # CASES — Detail / Add / Edit / Delete
    # ─────────────────────────────────────────────────────────────────────

    async def cases_get_by_id(self, case_id: str) -> CaseDetailOut:
        row = await self._get_case_details(case_id)
        return await self._enrich_case_detail(row)

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
        caseClients = await self.case_clients_repo.get_by_id(
            session=self.session,
            filters={CaseClients.case_id: case.case_id},
        )
        await log_activity(
            action="Case created",
            target=f"case:{case.case_id}:{case.case_number}",
            metadata={"case_id": case.case_id},
        )
        return await self._enrich_case_detail(case)

    async def cases_edit(self, payload: CaseEdit) -> CaseDetailOut:
        case = await self._get_case_details(payload.case_id)
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
        case,_ = await self._get_case_details(payload.case_id)
        await self.cases_repo.delete(session=self.session, id_values=payload.case_id, soft=True)
        await log_activity(action="Case deleted", target=f"case:{payload.case_id}:{case.case_number}")
        return {"case_id": payload.case_id, "deleted": True}

    # ─────────────────────────────────────────────────────────────────────
    # HEARINGS
    # ─────────────────────────────────────────────────────────────────────

    async def _sync_case_hearing_dates(self, case_id: str, today: date):
        # next hearing
        next_hearing = await self.session.scalar(
            select(func.min(Hearings.hearing_date)).where(
                Hearings.case_id == case_id,
                Hearings.deleted_ind.is_(False),
                Hearings.hearing_date >= today,
            )
        )

        # last hearing
        last_hearing = await self.session.scalar(
            select(func.max(Hearings.hearing_date)).where(
                Hearings.case_id == case_id,
                Hearings.deleted_ind.is_(False),
                Hearings.hearing_date < today,
            )
        )

        await self.cases_repo.update(
            session=self.session,
            id_values=case_id,
            data={
                "next_hearing_date": next_hearing,
                "last_hearing_date": last_hearing,
            },
        )

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
        creator_map = await self._load_map(
            (h.created_by for h in hearings),
            lambda ids: select(Users.user_id, Users.first_name, Users.last_name)
            .where(Users.user_id.in_(ids)),
            lambda r: r.user_id,
            lambda r: self.full_name(r.first_name, r.last_name),
        )

        status_map = await self.refm_resolver.get_desc_map(
            column_attr=Cases.status_code,
            value_column=RefmCaseStatus.description,
        )

        purpose_map = await self.refm_resolver.get_desc_map(
            column_attr=Hearings.purpose_code,
            value_column=RefmHearingPurpose.description,
        )

        return [
            HearingOut(
                hearing_id=h.hearing_id,
                case_id=h.case_id,
                hearing_date=h.hearing_date,
                status_code=h.status_code,
                status_description=await self.refm_resolver.get_value(
                    desc_map=status_map,
                    code=h.status_code
                ),

                purpose_code=h.purpose_code, 
                purpose_description=await self.refm_resolver.get_value(
                    desc_map=purpose_map,
                    code=h.status_code
                ),

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
        await self._sync_case_hearing_dates(payload.case_id, payload.hearing_date)
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
            purpose_desc=await self.refm_resolver.from_column(
                    column_attr=Hearings.purpose_code,
                    code=hearing.purpose_code,
                    value_column=RefmHearingPurpose.description,
                    default=None
                )

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
        await self._sync_case_hearing_dates(updated.case_id, updated.hearing_date)
        await log_activity(action="Hearing updated", target=f"case:{hearing.case_id}")
        status_desc = None
        if updated.status_code:
            hs = await self.session.get(RefmHearingStatus, updated.status_code)
            status_desc = hs.description if hs else None        

        purpose_desc = None
        if updated.purpose_code:
            p = await self.session.get(RefmHearingPurpose, hearing.purpose_code)
            purpose_desc = p.description if p else None

        return HearingOut(
            hearing_id=updated.hearing_id,
            case_id=updated.case_id,
            hearing_date=updated.hearing_date,
            status_code=updated.status_code,
            status_description=status_desc,
            purpose_code=updated.purpose_code,
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
        await self._sync_case_hearing_dates(hearing.case_id, date.today())
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
            lambda r: self.full_name(r.first_name, r.last_name),
        )
        return [
            CaseNoteOut(
                note_id=n.note_id,
                case_id=n.case_id,
                user_id=n.user_id,
                author_name=author_map.get(n.user_id),
                note_text=n.note_text,
                created_date = n.created_date
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
            author_name=self.full_name(u.first_name, u.last_name) if u else None,
            note_text=note.note_text,
            private_ind=bool(note.private_ind),
            created_date = note.created_date
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
            author_name=self.full_name(u.first_name, u.last_name) if u else None,
            note_text=updated.note_text,
            private_ind=bool(updated.private_ind),
            created_date = updated.created_date
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

    async def case_clients_get(self, case_id: str) -> List[CaseClientLinkedOut]:
        await self._assert_case_exists(case_id)

        rows = (await self.session.execute(
            select(
                CaseClients,
                Clients,
                Cases,
                CaseAors.user_id.label("aor_user_id"),
                Users.first_name,
                Users.last_name,
                ProfileImages.image_id,
                ProfileImages.image_data,
            )
            .join(Clients, CaseClients.client_id == Clients.client_id)
            .join(Cases, CaseClients.case_id == Cases.case_id)

            # ✅ ADD THIS
            .outerjoin(
                CaseAors,
                and_(
                    CaseAors.case_id == Cases.case_id,
                    CaseAors.primary_ind.is_(True),
                    CaseAors.withdrawal_date.is_(None),
                )
            )
            .outerjoin(
                Users,
                Users.user_id == CaseAors.user_id,
            )

            .outerjoin(
                ProfileImages,
                and_(
                    ProfileImages.client_id == Clients.client_id,
                    ProfileImages.deleted_ind.is_(False),
                )
            )
            .where(
                CaseClients.case_id == case_id,
                CaseClients.chamber_id == self.chamber_id,
            )
            .order_by(CaseClients.primary_ind.desc(), Clients.client_name.asc())
        )).all()

        # Batch-resolve all reference codes used across all rows
        used_party_roles   = {r.CaseClients.party_role_code for r in rows if r.CaseClients.party_role_code}
        used_case_statuses = {r.Cases.status_code           for r in rows if r.Cases.status_code}
        used_case_types    = {r.Cases.case_type_code        for r in rows if r.Cases.case_type_code}
        used_court_ids     = {r.Cases.court_id              for r in rows if r.Cases.court_id}
        used_client_types  = {r.Clients.client_type_code    for r in rows if r.Clients.client_type_code}
        used_party_types   = {r.Clients.party_type_code     for r in rows if r.Clients.party_type_code}

        # Resolve maps
        party_role_map = {}
        if used_party_roles:
            pr_rows = await self.session.execute(
                select(RefmPartyRoles.code, RefmPartyRoles.description)
                .where(RefmPartyRoles.code.in_(used_party_roles))
            )
            party_role_map = {r.code: r.description for r in pr_rows}

        case_status_map = {}
        if used_case_statuses:
            cs_rows = await self.session.execute(
                select(RefmCaseStatus.code, RefmCaseStatus.description)
                .where(RefmCaseStatus.code.in_(used_case_statuses))
            )
            case_status_map = {r.code: r.description for r in cs_rows}

        case_type_map = {}
        if used_case_types:
            ct_rows = await self.session.execute(
                select(RefmCaseTypes.code, RefmCaseTypes.description)
                .where(RefmCaseTypes.code.in_(used_case_types))
            )
            case_type_map = {r.code: r.description for r in ct_rows}

        court_map = {}
        if used_court_ids:
            co_rows = await self.session.execute(
                select(RefmCourts.court_id, RefmCourts.court_name)
                .where(RefmCourts.court_id.in_(used_court_ids))
            )
            court_map = {r.court_id: r.court_name for r in co_rows}

        client_type_map = {}
        if used_client_types:
            clt_rows = await self.session.execute(
                select(RefmClientType.code, RefmClientType.description)
                .where(RefmClientType.code.in_(used_client_types))
            )
            client_type_map = {r.code: r.description for r in clt_rows}

        party_type_map = {}
        if used_party_types:
            pt_rows = await self.session.execute(
                select(RefmPartyType.code, RefmPartyType.description)
                .where(RefmPartyType.code.in_(used_party_types))
            )
            party_type_map = {r.code: r.description for r in pt_rows}

        result = []
        for row in rows:
            cc: CaseClients  = row.CaseClients
            cl: Clients      = row.Clients
            ca: Cases        = row.Cases
            aor_user_id = row.aor_user_id
            aor_name = self.full_name(row.first_name, row.last_name) if row.aor_user_id else ''

            case_detail = CaseListOut(
                case_id=ca.case_id,
                chamber_id=ca.chamber_id,
                case_number=ca.case_number,
                court_id=ca.court_id,
                court_name=court_map.get(ca.court_id),
                case_type_code=ca.case_type_code,
                case_type_description=case_type_map.get(ca.case_type_code),
                filing_year=ca.filing_year,
                petitioner=ca.petitioner,
                respondent=ca.respondent,
                case_summary=ca.case_summary,
                status_code=ca.status_code,
                status_description=case_status_map.get(ca.status_code),
                case_client_id=cc.case_client_id,
                next_hearing_date=ca.next_hearing_date,
                last_hearing_date=ca.last_hearing_date,
                next_hearing_status=None,
                updated_date=ca.updated_date,
                # ── from CaseQuickHearingOut ─────────────────────────────────────
                aor_user_id=aor_user_id or '',
                aor_name=aor_name ,
                party_role_code=cc.party_role_code or '',
                party_role_description=party_role_map.get(cc.party_role_code, ''),
            )

            client_detail = ClientDetailsOut(
                image_id=row.image_id,
                image_data=row.image_data,
                case_client_id=cc.case_client_id,
                client_id=cl.client_id,
                chamber_id=cl.chamber_id,
                client_type_code=cl.client_type_code,
                client_type_description=client_type_map.get(cl.client_type_code, ""),
                party_type_code=cl.party_type_code,
                party_type_description=party_type_map.get(cl.party_type_code, ""),
                client_name=cl.client_name,
                display_name=cl.display_name,
                contact_person=cl.contact_person,
                phone=cl.phone,
                email=cl.email,
                alternate_phone=cl.alternate_phone,
                address_line1=cl.address_line1,
                address_line2=cl.address_line2,
                city=cl.city,
                state_code=cl.state_code,
                postal_code=cl.postal_code,
                country_code=cl.country_code,
                id_proof_code=cl.id_proof_code,
                id_proof_number=cl.id_proof_number,
                source_code=cl.source_code,
                referral_source=cl.referral_source,
                client_since=cl.client_since,
                notes=cl.notes,
                created_date=cl.created_date,
                updated_date=cl.updated_date,
            )

            result.append(CaseClientLinkedOut(
                case_client_id=cc.case_client_id,
                chamber_id=cc.chamber_id,
                case_id=cc.case_id,
                client_id=cc.client_id,
                party_role_code=cc.party_role_code,
                party_role_description=party_role_map.get(cc.party_role_code, ''),
                primary_ind=bool(cc.primary_ind),
                case_detail=case_detail,
                client_detail=client_detail,
            ))

        return result

    async def case_clients_link(
        self,
        case_id: str,
        payload: CaseClientLinkPayload
    ) -> CaseClientOut:

        await self._assert_case_exists(case_id)

        # ✅ Validate FK first
        client = await self.session.get(Clients, payload.client_id)
        if not client:
            raise ValidationErrorDetail(
                code=ErrorCodes.NOT_FOUND,
                message="Client not found",
            )

        # ✅ UPSERT
        link = await self.case_clients_repo.upsert(
            session=self.session,
            filters={
                CaseClients.case_id: case_id,
                CaseClients.client_id: payload.client_id,
                CaseClients.party_role_code: payload.party_role_code,
            },
            data={
                "chamber_id": self.chamber_id,
                "case_id": case_id,
                "client_id": payload.client_id,
                "party_role_code": payload.party_role_code,
                "primary_ind": payload.primary_ind,
            },
        )

        await log_activity(
            action="Client linked to case",
            target=f"case:{case_id}",
            metadata={
                "client_id": payload.client_id,
                "role": payload.party_role_code,
            },
        )

        pr = await self.session.get(RefmPartyRoles, payload.party_role_code)

        return CaseClientOut(
            case_client_id=link.case_client_id,
            chamber_id=self.chamber_id,
            case_id=link.case_id,
            client_id=link.client_id,
            party_role_code=link.party_role_code,
            party_role_description=pr.description if pr else '',
            primary_ind=bool(link.primary_ind),
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

    async def cases_get_recent_activity(
        self, case_id: str, limit: int = 10
    ) -> List[RecentActivityItem]:
        try:
            rows = await self.session.execute(
                select(
                    ActivityLog.action,
                    ActivityLog.user_id,
                    ActivityLog.created_date,
                    ActivityLog.metadata,   # 🔥 IMPORTANT
                )
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

        # ---------------------------------------------
        # 🔹 LOAD ACTOR NAMES (same as before)
        # ---------------------------------------------
        actor_map = await self._load_map(
            (r.user_id for r in activity_rows if r.user_id),
            lambda ids: select(
                Users.user_id, Users.first_name, Users.last_name
            ).where(Users.user_id.in_(ids)),
            lambda r: r.user_id,
            lambda r: self.full_name(r.first_name, r.last_name),
        )

        # ---------------------------------------------
        # 🔹 FORMAT TO TIMELINE (🔥 CORE CHANGE)
        # ---------------------------------------------
        return [
            format_activity(
                log=r,
                actor_name=actor_map.get(r.user_id) if r.user_id else None,
            )
            for r in activity_rows
        ]