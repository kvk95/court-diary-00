# app/database/repositories/support_tickets_repository.py

from typing import Optional, List, Tuple
from datetime import date
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, func

from app.database.models.refm_ticket_status import RefmTicketStatusConstants
from app.database.models.support_tickets import SupportTickets
from app.database.repositories.base.base_repository import BaseRepository
from app.database.repositories.base.repo_context import apply_repo_context


@apply_repo_context
class SupportTicketsRepository(BaseRepository[SupportTickets]):
    """Repository for SupportTickets model."""

    def __init__(self):
        super().__init__(SupportTickets)

    async def get_by_ticket_number(
        self,
        session: AsyncSession,
        chamber_id: str,
        user_id: str,
        description: str,
        exclude_deleted: bool = True,
    ) -> Optional[SupportTickets]:
        """Get ticket by chamber_id + ticket_number (unique constraint)."""
        filters = {
            SupportTickets.chamber_id: chamber_id,
            SupportTickets.description: description,
            SupportTickets.created_by: user_id,
        }
        where = [SupportTickets.deleted_ind == False] if exclude_deleted else []

        return await self.get_first(
            session=session,
            filters=filters,
            where=where
        )

    async def list_by_chamber(
        self,
        session: AsyncSession,
        chamber_id: Optional[str] = None,
        status_code: Optional[str] = None,
        module_code: Optional[str] = None,
        assigned_to: Optional[str] = None,
        search: Optional[str] = None,
        sort_by: str = "reported_date",
        sort_order: str = "desc",
    ) -> Tuple[List[SupportTickets], int]:
        """List tickets with filtering, pagination, and sorting."""

        filters = None
        if chamber_id:
            filters = {SupportTickets.chamber_id: chamber_id}
        where = [SupportTickets.deleted_ind == False]

        if status_code:
            where.append(SupportTickets.status_code == status_code)
        if module_code:
            where.append(SupportTickets.module_code == module_code)
        if assigned_to:
            where.append(SupportTickets.assigned_to == assigned_to)
        if search:
            where.append(
                and_(
                    SupportTickets.subject.ilike(f"%{search}%"),
                    SupportTickets.description.ilike(f"%{search}%"),
                    SupportTickets.ticket_number.ilike(f"%{search}%"),
                )
            )

        # Sorting
        order_col = getattr(SupportTickets, sort_by, SupportTickets.reported_date)
        order_by = order_col.desc() if sort_order.lower() == "desc" else order_col.asc()

        rows = await self.list_all(
            session=session,
            filters=filters,
            where=where,
            order_by=[order_by],
        )

        # Count for pagination
        count_stmt = select(func.count(SupportTickets.ticket_id)).where(
            SupportTickets.chamber_id == chamber_id,
        )
        if status_code:
            count_stmt = count_stmt.where(SupportTickets.status_code == status_code)
        if module_code:
            count_stmt = count_stmt.where(SupportTickets.module_code == module_code)
        if assigned_to:
            count_stmt = count_stmt.where(SupportTickets.assigned_to == assigned_to)
        if search:
            count_stmt = count_stmt.where(
                and_(
                    SupportTickets.subject.ilike(f"%{search}%"),
                    SupportTickets.description.ilike(f"%{search}%"),
                    SupportTickets.ticket_number.ilike(f"%{search}%"),
                )
            )

        total = (await session.execute(count_stmt)).scalar() or 0

        return rows, total

    async def get_stats(
        self,
        session: AsyncSession,
        chamber_id: str,
        today: date,
    ):
        """Get ticket summary statistics for dashboard."""
        from sqlalchemy import case

        stmt = select(
            func.count(SupportTickets.ticket_id).label("total"),
            func.sum(case((SupportTickets.status_code == RefmTicketStatusConstants.OPEN, 1), else_=0)).label("open"),
            func.sum(case((SupportTickets.status_code == RefmTicketStatusConstants.IN_PROGRESS, 1), else_=0)).label("in_progress"),
            func.sum(case((SupportTickets.status_code == RefmTicketStatusConstants.RESOLVED, 1), else_=0)).label("resolved"),
            func.sum(
                case((
                    and_(
                        SupportTickets.due_date < today,
                        SupportTickets.status_code != RefmTicketStatusConstants.RESOLVED,
                    ), 1), else_=0)
            ).label("overdue"),
        ).where(
            SupportTickets.chamber_id == chamber_id,
            SupportTickets.deleted_ind == False,
        )

        result = await session.execute(stmt)
        return result.first()