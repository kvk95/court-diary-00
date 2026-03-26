"""clients_service.py — Business logic for the Clients module"""

from typing import List, Optional

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.models.case_clients import CaseClients
from app.database.models.clients import Clients
from app.database.repositories.clients_repository import ClientsRepository
from app.dtos.base.paginated_out import PagingBuilder, PagingData
from app.dtos.clients_dto import (
    ClientCreate,
    ClientDetailOut,
    ClientEdit,
    ClientListOut,
    ClientSearchOut,
)
from app.services.base.secured_base_service import BaseSecuredService
from app.validators import ErrorCodes, ValidationErrorDetail


class ClientsService(BaseSecuredService):
    def __init__(
        self,
        session: AsyncSession,
        clients_repo: Optional[ClientsRepository] = None,
    ):
        super().__init__(session)
        self.clients_repo = clients_repo or ClientsRepository()

    # ─────────────────────────────────────────────────────────────────────
    # HELPERS
    # ─────────────────────────────────────────────────────────────────────

    async def _get_client_or_404(self, client_id: str) -> Clients:
        client = await self.clients_repo.get_by_id(
            session=self.session,
            filters={Clients.client_id: client_id, Clients.chamber_id: self.chamber_id},
        )
        if not client:
            raise ValidationErrorDetail(code=ErrorCodes.NOT_FOUND, message="Client not found")
        return client

    async def _linked_cases_count(self, client_id: str) -> int:
        return await self.session.scalar(
            select(func.count(CaseClients.case_client_id)).where(CaseClients.client_id == client_id)
        ) or 0

    async def _to_detail_out(self, client: Clients) -> ClientDetailOut:
        return ClientDetailOut(
            client_id=client.client_id,
            chamber_id=client.chamber_id,
            client_type=client.client_type,
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
            source_code=client.source_code,
            referral_source=client.referral_source,
            client_since=client.client_since,
            notes=client.notes,
            status_ind=client.status_ind,
            created_date=client.created_date,
            updated_date=client.updated_date,
            linked_cases=await self._linked_cases_count(client.client_id),
        )

    # ─────────────────────────────────────────────────────────────────────
    # SEARCH (for Link Client modal)
    # ─────────────────────────────────────────────────────────────────────

    async def clients_search(self, query: str, limit: int = 20) -> List[ClientSearchOut]:
        if not query or not query.strip():
            return []
        clients = await self.clients_repo.search_clients(
            session=self.session,
            chamber_id=self.chamber_id,
            query=query,
            limit=limit,
        )
        return [
            ClientSearchOut(
                client_id=c.client_id,
                client_name=c.client_name,
                display_name=c.display_name,
                client_type=c.client_type,
                phone=c.phone,
                email=c.email,
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
            Clients.is_deleted.is_(False),
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

        records = [
            ClientListOut(
                client_id=c.client_id,
                client_type=c.client_type,
                client_name=c.client_name,
                display_name=c.display_name,
                contact_person=c.contact_person,
                phone=c.phone,
                email=c.email,
                city=c.city,
                state_code=c.state_code,
                status_ind=c.status_ind,
                linked_cases=case_counts.get(c.client_id, 0),
                created_date=c.created_date,
            )
            for c in clients
        ]
        return PagingBuilder(total_records=total, page=page, limit=limit).build(records=records)

    # ─────────────────────────────────────────────────────────────────────
    # GET BY ID
    # ─────────────────────────────────────────────────────────────────────

    async def clients_get_by_id(self, client_id: str) -> ClientDetailOut:
        return await self._to_detail_out(await self._get_client_or_404(client_id))

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
        await self._get_client_or_404(client_id)
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
        client = await self._get_client_or_404(client_id)
        # Block if linked to active cases
        linked = await self._linked_cases_count(client_id)
        if linked > 0:
            raise ValidationErrorDetail(
                code=ErrorCodes.VALIDATION_ERROR,
                message=f"Cannot delete client: linked to {linked} case(s). Unlink first.",
            )
        await self.clients_repo.delete(session=self.session, id_values=client_id, soft=True)
        return {"client_id": client_id, "deleted": True}
