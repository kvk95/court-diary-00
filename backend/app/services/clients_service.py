"""clients_service.py — Business logic for the Clients module"""

from typing import List, Optional

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.models.case_clients import CaseClients
from app.database.models.cases import Cases
from app.database.models.clients import Clients
from app.database.models.hearings import Hearings
from app.database.models.refm_case_status import RefmCaseStatus
from app.database.models.refm_case_types import RefmCaseTypes
from app.database.models.refm_client_type import RefmClientType
from app.database.models.refm_courts import RefmCourts
from app.database.models.refm_hearing_status import RefmHearingStatus
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
    ClientSearchOut,
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
    
    async def _linked_cases(self, 
                            client_id: str,):
        rows, total = await self.case_clients_repo.list_cases_for_client(
            session=self.session,
            chamber_id=self.chamber_id,
            client_id=client_id,
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
                aor_name=self.full_name(first_name, last_name),
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
                next_hearing_status=await self.refm_resolver.from_column(
                    column_attr=Hearings.status_code,
                    code=hearing_status_code,
                    value_column=RefmHearingStatus.description,
                    default=None
                ),
            )
            for (
                c,
                first_name,
                last_name,
                hearing_status_code,
            ) in rows
        ]

        return records , total 

    async def _to_detail_out(self, client: Clients) -> ClientDetailOut:
        records , total = await self._linked_cases(client_id=client.client_id)
        img = await self.profile_images_repo.get_profile_image_by_clientid(session=self.session,
                                                                 client_id=client.client_id)

        return ClientDetailOut(
            client_id=client.client_id,
            chamber_id=client.chamber_id,
            client_type_code=client.client_type_code,
            client_type_description=await self.refm_resolver.from_column(
                column_attr=Clients.client_type_code,
                code=client.client_type_code,
                value_column=RefmClientType.description,
                default=None
            ),
            client_name=client.client_name,
            display_name=client.display_name,
            contact_person=client.contact_person,
            email=client.email,
            phone=client.phone,
            alternate_phone=client.alternate_phone,
            address_line1=client.address_line1,
            address_line2=client.address_line2,
            city=client.city,
            state_code=client.state_code,
            postal_code=client.postal_code,
            country_code=client.country_code,
            id_proof_type=client.id_proof_type,
            id_proof_number=client.id_proof_number,            
            image_id=img["image_id"] if img else None,
            image_data=img["image_data"] if img else None,
            source_code=client.source_code,
            referral_source=client.referral_source,
            client_since=client.client_since,
            notes=client.notes,
            status_ind=client.status_ind,
            created_date=client.created_date,
            updated_date=client.updated_date,
            linked_cases_count=total,
            linked_cases=records,
        )

    # ─────────────────────────────────────────────────────────────────────
    # SEARCH (for Link Client modal)
    # ─────────────────────────────────────────────────────────────────────

    async def clients_search(self, search: Optional[str], limit: int = 20) -> List[ClientSearchOut]:
        clients = await self.clients_repo.search_clients(
            session=self.session,
            chamber_id=self.chamber_id,
            search=search,
            limit=limit,
        )
        client_ids = [c.client_id for c in clients]

        image_map = await self.profile_images_repo.get_images_by_client_ids(
            session=self.session,
            client_ids=client_ids,
        )
        return [
            ClientSearchOut(
                client_id=c.client_id,
                client_name=c.client_name,
                display_name=c.display_name,
                client_type_code=c.client_type_code,
                client_type_description=await self.refm_resolver.from_column(
                    column_attr=Clients.client_type_code,
                    code=c.client_type_code,
                    value_column=RefmClientType.description,
                    default=None
                ),
                phone=c.phone,
                email=c.email,
                image_id=image_map.get(c.client_id, {}).get("image_id"),
                image_data=image_map.get(c.client_id, {}).get("image_data"),
            )
            for c in clients
        ]

    # ─────────────────────────────────────────────────────────────────────
    # PAGINATED LIST
    # ─────────────────────────────────────────────────────────────────────

    async def clients_get_paged(
        self,
        page: int,
        limit: int,
        search: Optional[str] = None,
        client_type: Optional[str] = None,
    ) -> PagingData[ClientListOut]:
        from sqlalchemy import or_
        conditions = [
            Clients.chamber_id == self.chamber_id,
            Clients.deleted_ind.is_(False),
        ]
        if client_type:
            conditions.append(Clients.client_type == client_type.upper())
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

        # Get linked case counts in one query
        client_ids = [c.client_id for c in clients]
        case_counts: dict = {}
        if client_ids:
            rows = await self.session.execute(
                select(CaseClients.client_id, func.count(CaseClients.case_client_id).label("cnt"))
                .where(CaseClients.client_id.in_(client_ids))
                .group_by(CaseClients.client_id)
            )
            case_counts = {r.client_id: r.cnt for r in rows}

            
            client_ids = [c.client_id for c in clients]

            image_map = await self.profile_images_repo.get_images_by_client_ids(
                session=self.session,
                client_ids=client_ids,
            )

        records = [
            ClientListOut(
                client_id=c.client_id,                
                client_type_code=c.client_type_code,
                client_type_description=await self.refm_resolver.from_column(
                    column_attr=Clients.client_type_code,
                    code=c.client_type_code,
                    value_column=RefmClientType.description,
                    default=None
                ),
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
                id_proof_type=c.id_proof_type,
                id_proof_number=c.id_proof_number,                
                image_id=image_map.get(c.client_id, {}).get("image_id"),
                image_data=image_map.get(c.client_id, {}).get("image_data"),
                source_code=c.source_code,
                referral_source=c.referral_source,
                client_since=c.client_since,
                notes=c.notes,
                status_ind=c.status_ind,
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
            active=rows.active or 0,
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
