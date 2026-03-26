"""client_payments_repository.py — All DB operations for ClientPayments"""


from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.models.client_payments import ClientPayments
from app.database.repositories.base.base_repository import BaseRepository
from app.database.repositories.base.repo_context import apply_repo_context


@apply_repo_context
class ClientPaymentsRepository(BaseRepository[ClientPayments]):
    def __init__(self):
        super().__init__(ClientPayments)

    async def get_total_paid_for_bill(self, session: AsyncSession, bill_id: str) -> float:
        """Sum of all payments on a bill — used by recalculate logic."""
        result = await session.scalar(
            select(func.coalesce(func.sum(ClientPayments.amount), 0))
            .where(ClientPayments.bill_id == bill_id)
        )
        return float(result) if result is not None else 0.0
