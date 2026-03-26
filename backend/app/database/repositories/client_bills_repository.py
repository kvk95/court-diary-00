"""client_bills_repository.py — All DB operations for ClientBills + billing reports"""

from datetime import date
from typing import Optional, Tuple

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.models.cases import Cases
from app.database.models.client_bills import ClientBills
from app.database.models.clients import Clients
from app.database.models.refm_billing_status import RefmBillingStatus
from app.database.repositories.base.base_repository import BaseRepository
from app.database.repositories.base.repo_context import apply_repo_context


@apply_repo_context
class ClientBillsRepository(BaseRepository[ClientBills]):
    def __init__(self):
        super().__init__(ClientBills)

    async def get_billing_stats(
        self,
        session: AsyncSession,
        chamber_id: str,
        today: date,
        paid_code: str,
        cancelled_code: str,
        pending_code: str,
    ) -> dict:
        """Aggregate stats for billing stat cards and reports."""
        row = (await session.execute(
            select(
                func.count(ClientBills.bill_id).label("cnt"),
                func.coalesce(func.sum(ClientBills.total_amount), 0).label("total"),
                func.coalesce(func.sum(ClientBills.paid_amount), 0).label("paid"),
            ).where(ClientBills.chamber_id == chamber_id)
        )).first()

        overdue_row = (await session.execute(
            select(
                func.count(ClientBills.bill_id).label("cnt"),
                func.coalesce(
                    func.sum(ClientBills.total_amount - ClientBills.paid_amount), 0
                ).label("amt"),
            ).where(
                ClientBills.chamber_id == chamber_id,
                ClientBills.status_code.notin_([paid_code, cancelled_code]),
                ClientBills.due_date < today,
            )
        )).first()

        paid_count = await session.scalar(
            select(func.count(ClientBills.bill_id)).where(
                ClientBills.chamber_id == chamber_id,
                ClientBills.status_code == paid_code,
            )
        ) or 0

        pending_count = await session.scalar(
            select(func.count(ClientBills.bill_id)).where(
                ClientBills.chamber_id == chamber_id,
                ClientBills.status_code == pending_code,
            )
        ) or 0

        return {
            "total": float(row.total) if row and row.total is not None else 0.0,
            "paid": float(row.paid) if row and row.paid is not None else 0.0,
            "bill_count": int(row.cnt or 0) if row else 0,
            "overdue_amt": float(overdue_row.amt) if overdue_row and overdue_row.amt is not None else 0.0,
            "overdue_count": int(overdue_row.cnt or 0) if overdue_row else 0,
            "paid_count": paid_count,
            "pending_count": pending_count,
        }

    async def list_bills_enriched(
        self,
        session: AsyncSession,
        chamber_id: str,
        page: int,
        limit: int,
        client_id: Optional[int] = None,
        status_code: Optional[str] = None,
        date_from: Optional[date] = None,
        date_to: Optional[date] = None,
    ) -> Tuple[list, int]:
        """Paginated bills with client/case/status enrichment in one repo call."""
        conditions = [ClientBills.chamber_id == chamber_id]
        if client_id:
            conditions.append(ClientBills.client_id == client_id)
        if status_code and status_code.upper() != "ALL":
            conditions.append(ClientBills.status_code == status_code.upper())
        if date_from:
            conditions.append(ClientBills.bill_date >= date_from)
        if date_to:
            conditions.append(ClientBills.bill_date <= date_to)

        bills, total = await self.list_paginated(
            session=session, page=page, limit=limit,
            where=conditions, order_by=[ClientBills.bill_date.desc()],
        )
        if not bills:
            return [], 0

        client_ids = list({b.client_id for b in bills})
        case_ids = list({b.case_id for b in bills if b.case_id})
        s_codes = list({b.status_code for b in bills if b.status_code})

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

        status_map: dict = {}
        color_map: dict = {}
        if s_codes:
            rows = await session.execute(
                select(RefmBillingStatus.code, RefmBillingStatus.description, RefmBillingStatus.color_code)
                .where(RefmBillingStatus.code.in_(s_codes))
            )
            for r in rows:
                status_map[r.code] = r.description
                color_map[r.code] = r.color_code

        return [
            {
                "bill": b,
                "client_name": client_map.get(b.client_id, ""),
                "case_number": case_map.get(b.case_id) if b.case_id else None,
                "status_description": status_map.get(b.status_code) if b.status_code else None,
                "color_code": color_map.get(b.status_code) if b.status_code else None,
            }
            for b in bills
        ], total

    async def recalculate_paid_amount(
        self,
        session: AsyncSession,
        bill_id: str,
        total_paid: float,
        bill: ClientBills,
        today: date,
        paid_code: str,
        pending_code: str,
        overdue_code: str,
    ) -> None:
        """Update paid_amount + status after any payment change."""
        total = float(bill.total_amount) if bill.total_amount is not None else 0.0
        if total_paid >= total:
            new_status = paid_code
        elif total_paid > 0:
            new_status = pending_code
        elif bill.due_date and bill.due_date < today:
            new_status = overdue_code
        else:
            new_status = bill.status_code or pending_code

        await self.update(
            session=session,
            id_values=bill_id,
            data={"paid_amount": round(total_paid, 2), "status_code": new_status},
        )

    async def count_payments(self, session: AsyncSession, bill_id: str) -> int:
        """Count payments on a bill — used by delete-bill guard."""
        from app.database.models.client_payments import ClientPayments
        return await session.scalar(
            select(func.count(ClientPayments.payment_id))
            .where(ClientPayments.bill_id == bill_id)
        ) or 0

    async def get_billing_by_month(
        self,
        session: AsyncSession,
        chamber_id: str,
        month_start: date,
        month_end: date,
    ) -> dict:
        """Sum of billed and paid for a specific month."""
        row = (await session.execute(
            select(
                func.coalesce(func.sum(ClientBills.total_amount), 0).label("billed"),
                func.coalesce(func.sum(ClientBills.paid_amount), 0).label("paid"),
            ).where(
                ClientBills.chamber_id == chamber_id,
                ClientBills.bill_date >= month_start,
                ClientBills.bill_date < month_end,
            )
        )).first()
        return {
            "billed": float(row.billed) if row and row.billed is not None else 0.0,
            "paid": float(row.paid) if row and row.paid is not None else 0.0,
        }

    async def get_top_clients_billing(
        self,
        session: AsyncSession,
        chamber_id: str,
        limit: int = 10,
    ) -> list:
        """Top clients by total billed amount."""
        result = await session.execute(
            select(
                ClientBills.client_id,
                Clients.client_name,
                func.coalesce(func.sum(ClientBills.total_amount), 0).label("billed"),
                func.coalesce(func.sum(ClientBills.paid_amount), 0).label("paid"),
            )
            .join(Clients, ClientBills.client_id == Clients.client_id)
            .where(ClientBills.chamber_id == chamber_id)
            .group_by(ClientBills.client_id, Clients.client_name)
            .order_by(func.sum(ClientBills.total_amount).desc())
            .limit(limit)
        )
        return list(result.all())
