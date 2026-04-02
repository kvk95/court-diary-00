"""clients_service.py — Business logic for the Clients module"""

from typing import List, Optional

from sqlalchemy import func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.models.case_clients import CaseClients
from app.database.models.clients import Clients
from app.database.models.profile_images import ProfileImages
from app.database.models.refm_case_status import RefmCaseStatus
from app.database.models.refm_case_types import RefmCaseTypes
from app.database.models.refm_client_type import RefmClientType
from app.database.models.refm_courts import RefmCourts
from app.database.models.refm_hearing_status import RefmHearingStatus
from app.database.models.refm_img_upload_for import RefmImgUploadForConstants
from app.database.models.refm_party_roles import RefmPartyRoles
from app.database.models.refm_party_type import RefmPartyType
from app.database.repositories.case_clients_repository import CaseClientsRepository
from app.database.repositories.clients_repository import ClientsRepository
from app.database.repositories.profile_images_repository import ProfileImagesRepository
from app.dtos.base.paginated_out import PagingBuilder, PagingData
from app.dtos.cases_dto import CaseListOut
from app.dtos.clients_dto import (
    ClientCreate,
    ClientDetailOut,
    ClientEdit,
    ClientListOut,
    ClientDetailsOut,
    ClientSummaryStats,
)
from app.services.base.secured_base_service import BaseSecuredService
from app.validators import ErrorCodes, ValidationErrorDetail


class ClientsService(BaseSecuredService):
    def __init__(
        self,
        session: AsyncSession,
        clients_repo: Optional[ClientsRepository] = None,
        case_clients_repo: Optional[CaseClientsRepository] = None,
        profile_images_repo: Optional[ProfileImagesRepository] = None,
    ):
        super().__init__(session)
        self.clients_repo = clients_repo or ClientsRepository()
        self.case_clients_repo = case_clients_repo or CaseClientsRepository()
        self.profile_images_repo = profile_images_repo or ProfileImagesRepository()

    # ─────────────────────────────────────────────────────────────────────
    # HELPERS
    # ─────────────────────────────────────────────────────────────────────

    async def _get_client_details(self, client_id: str) -> Clients:
            client = await self.clients_repo.get_by_id(
                session=self.session,
                filters={Clients.client_id: client_id, Clients.chamber_id: self.chamber_id},
            )
            if not client:
                raise ValidationErrorDetail(code=ErrorCodes.NOT_FOUND, message="Client not found")
            return client
    
    async def _linked_cases_count(self, client_id: str) -> int:
        stmt = select(func.count(CaseClients.case_client_id)).where(CaseClients.client_id == client_id)
        return await self.case_clients_repo.execute_scalar( session=self.session, stmt=stmt)

    async def _linked_cases(self, client_id: str):
        rows, total = await self.case_clients_repo.list_cases_for_client(
            session=self.session,
            chamber_id=self.chamber_id,
            client_id=client_id,
        )

        print(f"[_linked_cases] client_id={client_id} total={total} rows_count={len(rows)}")
        for i, r in enumerate(rows):
            print(f"  row[{i}] Cases={r.Cases.case_id if hasattr(r, 'Cases') else 'NO_CASES'} "
                f"party_role={getattr(r, 'party_role_code', 'MISSING')} "
                f"case_client_id={getattr(r, 'case_client_id', 'MISSING')}")

        used_court_ids      = {r.Cases.court_id       for r in rows if r.Cases.court_id}
        used_case_statuses  = {r.Cases.status_code    for r in rows if r.Cases.status_code}
        used_case_types     = {r.Cases.case_type_code for r in rows if r.Cases.case_type_code}
        used_hearing_status = {r.hearing_status_code  for r in rows if r.hearing_status_code}
        used_party_roles    = {r.party_role_code       for r in rows if r.party_role_code}

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

        records: list[CaseListOut] = []

        for (
            cases,
            first_name,
            last_name,
            aor_user_id,
            hearing_status_code,
            party_role_code,
            case_client_id
        ) in rows:
            records.append(CaseListOut(
                case_id=cases.case_id,
                chamber_id=cases.chamber_id,
                case_number=cases.case_number,
                court_id=cases.court_id,
                court_name=court_map.get(cases.court_id),
                status_code=cases.status_code,
                status_description=status_map.get(cases.status_code),
                case_type_code=cases.case_type_code,
                case_type_description=case_type_map.get(cases.case_type_code),
                filing_year=cases.filing_year,
                case_summary=cases.case_summary,
                petitioner=cases.petitioner,
                respondent=cases.respondent,
                aor_user_id=aor_user_id or "",
                aor_name = self.full_name(first_name, last_name) if aor_user_id else "",
                party_role_code=party_role_code,
                party_role_description=party_role_map.get(party_role_code, ""),
                case_client_id=case_client_id,
                next_hearing_date=cases.next_hearing_date,
                last_hearing_date=cases.last_hearing_date,
                next_hearing_status=hearing_status_map.get(hearing_status_code),
                updated_date=cases.updated_date,
            ))

        return records, total

    async def _to_detail_out(self, client: Clients) -> ClientDetailOut:
        records, total = await self._linked_cases(
            client_id=client.client_id
        )
        img = await self.profile_images_repo.get_profile_image_by_clientid(
            session=self.session,
            client_id=client.client_id,
        )

        client_type_desc = await self.refm_resolver.from_column(
            column_attr=Clients.client_type_code,
            code=client.client_type_code,
            value_column=RefmClientType.description,
            default=None,
        )
        party_type_desc = await self.refm_resolver.from_column(
            column_attr=Clients.party_type_code,
            code=client.party_type_code,
            value_column=RefmPartyType.description,
            default=None,
        )

        return ClientDetailOut(
            client_id=client.client_id,
            chamber_id=client.chamber_id,
            client_name=client.client_name,
            display_name=client.display_name,
            contact_person=client.contact_person,
            client_type_code=client.client_type_code,
            client_type_description=client_type_desc,
            party_type_code=client.party_type_code,
            party_type_description=party_type_desc,
            email=client.email,
            phone=client.phone,
            alternate_phone=client.alternate_phone,
            address_line1=client.address_line1,
            address_line2=client.address_line2,
            city=client.city,
            state_code=client.state_code,
            postal_code=client.postal_code,
            country_code=client.country_code,
            id_proof_code=client.id_proof_code,
            id_proof_number=client.id_proof_number,
            image_id=img["image_id"] if img else None,
            image_data=img["image_data"] if img else None,
            source_code=client.source_code,
            referral_source=client.referral_source,
            client_since=client.client_since,
            notes=client.notes,
            created_date=client.created_date,
            updated_date=client.updated_date,
            linked_cases_count=total,
            linked_cases=records,
            
            case_client_id= '',
            # case_clients=case_clients_out,
        )

    # ─────────────────────────────────────────────────────────────────────
    # SEARCH (for Link Client modal)
    # ─────────────────────────────────────────────────────────────────────

    async def clients_search(self, search: Optional[str], limit: int = 20) -> List[ClientDetailsOut]:
        clients = await self.clients_repo.search_clients(
            session=self.session,
            chamber_id=self.chamber_id,
            search=search,
            limit=limit,
        )

        used_client_types = {c.client_type_code for c in clients if c.client_type_code}
        used_party_types  = {c.party_type_code  for c in clients if c.party_type_code}

        client_type_map = {}
        if used_client_types:
            q = await self.session.execute(
                select(RefmClientType.code, RefmClientType.description)
                .where(RefmClientType.code.in_(used_client_types))
            )
            client_type_map = {r.code: r.description for r in q}

        party_type_map = {}
        if used_party_types:
            q = await self.session.execute(
                select(RefmPartyType.code, RefmPartyType.description)
                .where(RefmPartyType.code.in_(used_party_types))
            )
            party_type_map = {r.code: r.description for r in q}

        client_ids = [c.client_id for c in clients]
        image_map = await self.profile_images_repo.get_images_by_client_ids(
            session=self.session,
            client_ids=client_ids,
        )

        return [
            ClientDetailsOut(
                case_client_id="",
                client_id=c.client_id,
                chamber_id=self.chamber_id,
                client_name=c.client_name,
                display_name=c.display_name,
                client_type_code=c.client_type_code,
                client_type_description=client_type_map.get(c.client_type_code, ''),
                party_type_code=c.party_type_code,
                party_type_description=party_type_map.get(c.party_type_code, ''),
                phone=c.phone,
                email=c.email,
                image_id=image_map.get(c.client_id, {}).get("image_id"),
                image_data=image_map.get(c.client_id, {}).get("image_data"),
            )
            for c in clients
        ]


    async def clients_get_paged(
        self,
        page: int,
        limit: int,
        search: Optional[str] = None,
        client_type_code: Optional[str] = None,
        party_type_code: Optional[str] = None,
    ) -> PagingData[ClientListOut]:

        conditions = [
            Clients.chamber_id == self.chamber_id,
            Clients.deleted_ind.is_(False),
        ]
        if client_type_code:
            conditions.append(Clients.client_type_code == client_type_code.upper())
        if party_type_code:
            conditions.append(Clients.party_type_code == party_type_code.upper())
        if search and search.strip():
            kw = f"%{search.strip()}%"
            conditions.append(
                or_(
                    Clients.client_name.ilike(kw),
                    Clients.phone.ilike(kw),
                    Clients.email.ilike(kw),
                )
            )

        clients, total = await self.clients_repo.list_paginated(
            session=self.session,
            page=page,
            limit=limit,
            where=conditions,
            order_by=[Clients.client_name.asc()],
        )

        client_ids = [c.client_id for c in clients]

        # Batch resolve all lookups
        used_client_types = {c.client_type_code for c in clients if c.client_type_code}
        used_party_types  = {c.party_type_code  for c in clients if c.party_type_code}

        client_type_map = {}
        if used_client_types:
            q = await self.session.execute(
                select(RefmClientType.code, RefmClientType.description)
                .where(RefmClientType.code.in_(used_client_types))
            )
            client_type_map = {r.code: r.description for r in q}

        party_type_map = {}
        if used_party_types:
            q = await self.session.execute(
                select(RefmPartyType.code, RefmPartyType.description)
                .where(RefmPartyType.code.in_(used_party_types))
            )
            party_type_map = {r.code: r.description for r in q}

        case_counts: dict = {}
        image_map: dict = {}
        if client_ids:
            q = await self.session.execute(
                select(CaseClients.client_id, func.count(CaseClients.case_client_id).label("cnt"))
                .where(CaseClients.client_id.in_(client_ids))
                .group_by(CaseClients.client_id)
            )
            case_counts = {r.client_id: r.cnt for r in q}

            image_map = await self.profile_images_repo.get_images_by_client_ids(
                session=self.session,
                client_ids=client_ids,
            )

        records = [
            ClientListOut(
                case_client_id="",
                client_id=c.client_id,
                chamber_id=self.chamber_id,
                client_type_code=c.client_type_code,
                client_type_description=client_type_map.get(c.client_type_code,''),
                party_type_code=c.party_type_code,
                party_type_description=party_type_map.get(c.party_type_code,''),
                client_name=c.client_name,
                contact_person=c.contact_person,
                display_name=c.display_name,
                phone=c.phone,
                email=c.email,
                alternate_phone=c.alternate_phone,
                address_line1=c.address_line1,
                address_line2=c.address_line2,
                city=c.city,
                state_code=c.state_code,
                postal_code=c.postal_code,
                country_code=c.country_code,
                id_proof_code=c.id_proof_code,
                id_proof_number=c.id_proof_number,
                image_id=image_map.get(c.client_id, {}).get("image_id"),
                image_data=image_map.get(c.client_id, {}).get("image_data"),
                source_code=c.source_code,
                referral_source=c.referral_source,
                client_since=c.client_since,
                notes=c.notes,
                linked_cases_count=case_counts.get(c.client_id, 0),
                created_date=c.created_date,
            )
            for c in clients
        ]

        return PagingBuilder(total_records=total, page=page, limit=limit).build(records=records)

    # ─────────────────────────────────────────────────────────────────────
    # STATS
    # ─────────────────────────────────────────────────────────────────────
    
    async def clients_get_stats(self) -> ClientSummaryStats:
        rows = await self.clients_repo.get_client_summary(
            session=self.session,
            chamber_id=self.chamber_id,
        )

        return ClientSummaryStats(
            total=rows.total or 0,
            parties=rows.parties or 0,
            individual=rows.individual or 0,
            corporate=rows.corporate or 0,
            case_associations=rows.case_associations or 0,
        )

    # ─────────────────────────────────────────────────────────────────────
    # GET BY ID
    # ─────────────────────────────────────────────────────────────────────

    async def clients_get_by_id(self, client_id: str) -> ClientDetailOut:
        return await self._to_detail_out(await self._get_client_details(client_id))

    # ─────────────────────────────────────────────────────────────────────
    # CREATE
    # ─────────────────────────────────────────────────────────────────────

    async def clients_add(self, payload: ClientCreate) -> ClientDetailOut:
        data = payload.model_dump(exclude_unset=True, exclude_none=True)
        data["chamber_id"] = self.chamber_id
        client = await self.clients_repo.create(
            session=self.session,
            data=self.clients_repo.map_fields_to_db_column(data),
        )
        if payload.image_data:
            image_details = {
                "client_id":client.client_id,
                "image_upload_code":RefmImgUploadForConstants.CLIENT,
                "image_data":payload.image_data,
                "description":"Client image uploaded"
            }
            img:ProfileImages = await self.profile_images_repo.create(
                session=self.session,
                data=self.profile_images_repo.map_fields_to_db_column(image_details),
            )
        return await self._to_detail_out(client)

    # ─────────────────────────────────────────────────────────────────────
    # EDIT
    # ─────────────────────────────────────────────────────────────────────

    async def clients_edit(self, client_id: str, payload: ClientEdit) -> ClientDetailOut:
        await self._get_client_details(client_id)
        data = payload.model_dump(exclude_unset=True, exclude_none=True)
        if data:
            await self.clients_repo.update(
                session=self.session,
                id_values=client_id,
                data=self.clients_repo.map_fields_to_db_column(data),
            )

        if payload.image_data:
            image_details = {
                "client_id":client_id,
                "image_id":payload.image_id,
                "image_upload_code":RefmImgUploadForConstants.CLIENT,
                "image_data":payload.image_data,
                "description":"Client image uploaded"
            }
            img:ProfileImages = await self.profile_images_repo.upsert(
                filters={
                    ProfileImages.image_id: payload.image_id,
                },
                session=self.session,
                data=self.profile_images_repo.map_fields_to_db_column(image_details),
            )
        return await self.clients_get_by_id(client_id)

    # ─────────────────────────────────────────────────────────────────────
    # DELETE (soft)
    # ─────────────────────────────────────────────────────────────────────

    async def clients_delete(self, client_id: str) -> dict:
        client = await self._get_client_details(client_id)
        # Block if linked to active cases
        linked = await self._linked_cases_count(client_id)
        if linked > 0:
            raise ValidationErrorDetail(
                code=ErrorCodes.VALIDATION_ERROR,
                message=f"Cannot delete client: linked to {linked} case(s). Unlink first.",
            )
        await self.clients_repo.delete(session=self.session, id_values=client_id, soft=True)
        return {"client_id": client_id, "deleted": True}
