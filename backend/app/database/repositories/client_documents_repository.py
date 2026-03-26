"""client_documents_repository.py — All DB operations for ClientDocuments"""

from typing import Optional, Tuple

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.models.cases import Cases
from app.database.models.client_documents import ClientDocuments
from app.database.models.clients import Clients
from app.database.repositories.base.base_repository import BaseRepository
from app.database.repositories.base.repo_context import apply_repo_context


@apply_repo_context
class ClientDocumentsRepository(BaseRepository[ClientDocuments]):
    def __init__(self):
        super().__init__(ClientDocuments)

    async def list_documents_enriched(
        self,
        session: AsyncSession,
        chamber_id: str,
        page: int,
        limit: int,
        client_id: Optional[int] = None,
        custody_status: Optional[str] = None,
    ) -> Tuple[list, int]:
        """Returns list of enriched dicts + total count."""
        conditions = [ClientDocuments.chamber_id == chamber_id]
        if client_id:
            conditions.append(ClientDocuments.client_id == client_id)
        if custody_status:
            conditions.append(ClientDocuments.custody_status == custody_status.upper())

        docs, total = await self.list_paginated(
            session=session, page=page, limit=limit,
            where=conditions, order_by=[ClientDocuments.received_date.desc()],
        )
        if not docs:
            return [], 0

        client_ids = list({d.client_id for d in docs})
        case_ids = list({d.case_id for d in docs if d.case_id})

        client_map: dict = {}
        if client_ids:
            rows = await session.execute(
                select(Clients.client_id, Clients.client_name)
                .where(Clients.client_id.in_(client_ids))
            )
            client_map = {r.client_id: r.client_name for r in rows}

        case_map: dict = {}
        if case_ids:
            rows = await session.execute(
                select(Cases.case_id, Cases.case_number)
                .where(Cases.case_id.in_(case_ids))
            )
            case_map = {r.case_id: r.case_number for r in rows}

        return [
            {
                "doc": d,
                "client_name": client_map.get(d.client_id, ""),
                "case_number": case_map.get(d.case_id) if d.case_id else None,
            }
            for d in docs
        ], total
