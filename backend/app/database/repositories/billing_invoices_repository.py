from typing import Any, List, Optional, Tuple, Dict

from sqlalchemy import select, func

from app.database.repositories.base.repo_context import apply_repo_context
from app.database.repositories.base.base_repository import BaseRepository
from app.database.models.billing_invoices import BillingInvoices

@apply_repo_context
class BillingInvoicesRepository(BaseRepository[BillingInvoices]):
    def __init__(self):
        super().__init__(BillingInvoices)
    
    async def list_invoices(
        self,
        session,
        chamber_id: str,
        page: int,
        limit: int,
        status: Optional[str],
    ) -> Tuple[List[Dict[str, Any]], int]:

        stmt = (
            select(
                BillingInvoices.invoice_id,
                BillingInvoices.invoice_number,
                BillingInvoices.period_start,
                BillingInvoices.period_end,
                BillingInvoices.amount,
                BillingInvoices.status_code,
                BillingInvoices.created_date.label("invoice_date"),
            )
            .where(BillingInvoices.chamber_id == chamber_id)
            .order_by(BillingInvoices.created_date.desc())
        )

        # 🎯 filter
        if status:
            stmt = stmt.where(BillingInvoices.status_code == status)

        # count
        count_stmt = select(func.count()).select_from(stmt.subquery())
        

        # pagination
        stmt = stmt.offset((page - 1) * limit).limit(limit)        

        rows = (await self.execute(session=session, stmt=stmt)).all()

        result = await self.execute(session=session,stmt=stmt)
        total = await self.execute_scalar(session=session, stmt=count_stmt, default=0)

        result = []
        for r in rows:
            result.append({
                "invoice_id": r.invoice_id,
                "invoice_number": r.invoice_number,
                "period_start": r.period_start,
                "period_end": r.period_end,
                "amount": r.amount,
                "status_code": r.status_code,
                "invoice_date": r.invoice_date,
            })

        return result, total
