"""Support Ticket Service — Business logic"""

import secrets
import string
from datetime import date, datetime, timezone
from typing import List, Optional, Dict, Any, Callable, Iterable, TypeVar

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.models.support_tickets import SupportTickets
from app.database.models.refm_modules import RefmModules
from app.database.models.refm_ticket_status import RefmTicketStatus, RefmTicketStatusConstants
from app.database.models.users import Users
from app.database.repositories.support_tickets_repository import SupportTicketsRepository
from app.dtos.base.paginated_out import PagingBuilder, PagingData
from app.dtos.support_ticket_dto import (
    SupportTicketCreate,
    SupportTicketEdit,
    SupportTicketDelete,
    SupportTicketOut,
    SupportTicketListOut,
    SupportTicketStats,
)
from app.services.base.secured_base_service import BaseSecuredService
from app.validators import ErrorCodes, ValidationErrorDetail


class SupportTicketService(BaseSecuredService):
    """Business logic for Support Tickets"""
    
    def __init__(
        self,
        session: AsyncSession,
        tickets_repo: Optional[SupportTicketsRepository] = None,
    ):
        super().__init__(session)
        self.tickets_repo = tickets_repo or SupportTicketsRepository()
    
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
        """Generic helper to load reference maps"""
        ids = list({i for i in ids if i})
        if not ids:
            return {}
        rows = (await self.session.execute(query_builder(ids))).all()
        return {key_fn(r): value_fn(r) for r in rows}
    
    async def _assert_ticket_exists(self, ticket_id: str) -> SupportTickets:
        """Verify ticket exists and belongs to chamber"""
        ticket = await self.tickets_repo.get_by_id(
            session=self.session,
            filters={
                SupportTickets.ticket_id: ticket_id,
                SupportTickets.chamber_id: self.chamber_id,
            },
        )
        if not ticket:
            raise ValidationErrorDetail(
                code=ErrorCodes.NOT_FOUND,
                message="Support ticket not found",
            )
        return ticket
    
    async def _load_reference_maps(self, tickets: List[SupportTickets]):
        """Batch-load all reference descriptions for tickets"""
        used_modules = {t.module_code for t in tickets if t.module_code}
        used_statuses = {t.status_code for t in tickets if t.status_code}
        used_user_ids = {t.assigned_to for t in tickets if t.assigned_to}
        used_user_ids.update({t.reported_by for t in tickets if t.reported_by})
        
        module_map = {}
        if used_modules:
            rows = await self.session.execute(
                select(RefmModules.code, RefmModules.description)
                .where(RefmModules.code.in_(used_modules))
            )
            module_map = {r.code: r.description for r in rows}
        
        status_map = {}
        if used_statuses:
            rows = await self.session.execute(
                select(RefmTicketStatus.code, RefmTicketStatus.description)
                .where(RefmTicketStatus.code.in_(used_statuses))
            )
            status_map = {r.code: r.description for r in rows}
        
        user_map = {}
        if used_user_ids:
            rows = await self.session.execute(
                select(Users.user_id, Users.first_name, Users.last_name)
                .where(Users.user_id.in_(used_user_ids))
            )
            user_map = {r.user_id: self.full_name(r.first_name, r.last_name) for r in rows}
        
        return {
            "module_map": module_map,
            "status_map": status_map,
            "user_map": user_map,
        }
    
    # ─────────────────────────────────────────────────────────────────────
    # LOG ACTIVITY — HELPER
    # ─────────────────────────────────────────────────────────────────────
    
    async def _log_entity_change(
        self,
        action: str,
        entity_type: str,
        entity_id: str,
        payload: Optional[Any] = None,
        extra_metadata: Optional[Dict] = None,
    ):
        """Standardized logging for ticket CRUD operations"""
        metadata = payload.model_dump(exclude_unset=True, exclude_none=True) if payload else {}
        metadata.update(extra_metadata or {})
        metadata["chamber_id"] = self.chamber_id
        
        target = f"ticket:{entity_id}"
        
        # await log_activity(action=action, target=target, metadata=metadata)

    def _generate_ticket_number(self) -> str:
        """Generate ticket: 8-char timestamp (YYMMDDHH) + 7 random chars."""
        # Timestamp: YYMMDDHH (e.g., "26041714" = 2026-04-17 14:xx UTC)
        ts = datetime.now(timezone.utc).strftime("%y%m%d%H")
        
        # 7 random alphanumeric chars
        alphabet = string.ascii_uppercase + string.digits
        suffix = ''.join(secrets.choice(alphabet) for _ in range(7))
        
        return ts + suffix  # Total: 15 chars
    
    # ─────────────────────────────────────────────────────────────────────
    # STATS
    # ─────────────────────────────────────────────────────────────────────
    
    async def tickets_get_stats(self) -> SupportTicketStats:
        """Get summary statistics for support tickets"""
        today = date.today()
        r = await self.tickets_repo.get_stats(self.session, self.chamber_id, today)
        if not r:
            return SupportTicketStats()
        return SupportTicketStats(
            total=r.total or 0,
            open=r.open or 0,
            in_progress=r.in_progress or 0,
            resolved=r.resolved or 0,
            overdue=r.overdue or 0,
        )
    
    # ─────────────────────────────────────────────────────────────────────
    # LIST / GET
    # ─────────────────────────────────────────────────────────────────────
    
    async def tickets_get_paged(
        self,
        page: int,
        limit: int,
        status_code: Optional[str] = None,
        module_code: Optional[str] = None,
        assigned_to: Optional[str] = None,
        search: Optional[str] = None,
        sort_by: str = "reported_date",
        sort_order: str = "desc",
        is_chamber:bool = False,
    ) -> PagingData[SupportTicketListOut]:
        """Paginated list of support tickets"""

        chamber_id = self.chamber_id if is_chamber else None

        rows, total = await self.tickets_repo.list_by_chamber(
            session=self.session,
            chamber_id=chamber_id,
            status_code=status_code,
            module_code=module_code,
            assigned_to=assigned_to,
            search=search,
            sort_by=sort_by,
            sort_order=sort_order,
        )
        
        # Load reference maps
        maps = await self._load_reference_maps(rows)
        
        records = [
            SupportTicketListOut(
                ticket_id=ticket.ticket_id,
                chamber_id=ticket.chamber_id,
                ticket_number=ticket.ticket_number,
                subject=ticket.subject,
                description=ticket.description,
                module_code=ticket.module_code,
                module_name=maps["module_map"].get(ticket.module_code),
                status_code=ticket.status_code,
                status_description=maps["status_map"].get(ticket.status_code),
                assigned_to=ticket.assigned_to,
                assigned_to_name=maps["user_map"].get(ticket.assigned_to),
                reported_by=ticket.reported_by,
                reported_by_name=maps["user_map"].get(ticket.reported_by),
                reported_date=ticket.reported_date,
                assigned_date=ticket.assigned_date,
                resolved_date=ticket.resolved_date,
                due_date=ticket.due_date,
                created_date=ticket.created_date,
                updated_date=ticket.updated_date,
            )
            for ticket in rows
        ]
        
        return PagingBuilder(total_records=total, page=page, limit=limit).build(records=records)
    
    async def tickets_get_by_id(self, ticket_id: str) -> SupportTicketOut:
        """Get single ticket by ID with enriched references"""
        ticket = await self._assert_ticket_exists(ticket_id)
        maps = await self._load_reference_maps([ticket])
        
        return SupportTicketOut(
            ticket_id=ticket.ticket_id,
            chamber_id=ticket.chamber_id,
            ticket_number=ticket.ticket_number,
            subject=ticket.subject,
            description=ticket.description,
            module_code=ticket.module_code,
            module_name=maps["module_map"].get(ticket.module_code),
            status_code=ticket.status_code,
            status_description=maps["status_map"].get(ticket.status_code),
            assigned_to=ticket.assigned_to,
            assigned_to_name=maps["user_map"].get(ticket.assigned_to),
            reported_by=ticket.reported_by,
            reported_by_name=maps["user_map"].get(ticket.reported_by),
            reported_date=ticket.reported_date,
            assigned_date=ticket.assigned_date,
            resolved_date=ticket.resolved_date,
            due_date=ticket.due_date,
            created_date=ticket.created_date,
            updated_date=ticket.updated_date,
        )
    
    # ─────────────────────────────────────────────────────────────────────
    # CREATE / UPDATE / DELETE
    # ─────────────────────────────────────────────────────────────────────
    
    async def tickets_add(self, payload: SupportTicketCreate) -> SupportTicketOut:
        """Create a new support ticket"""
        # Check for duplicate ticket_number within chamber
        existing = await self.tickets_repo.get_by_ticket_number(
            session=self.session,
            chamber_id=self.chamber_id,
            user_id=self.user_id,
            description=payload.description,
        )
        if existing:
            raise ValidationErrorDetail(
                code=ErrorCodes.VALIDATION_ERROR,
                message=f"Ticket '{payload.description}' already exists",
            )
        
        data = payload.model_dump(exclude_unset=True, exclude_none=True)
        data["ticket_number"] = self._generate_ticket_number()
        data["reported_by"] = self.user_id
        data["status_code"] = RefmTicketStatusConstants.OPEN
        
        ticket = await self.tickets_repo.create(
            session=self.session,
            data=self.tickets_repo.map_fields_to_db_column(data),
        )
        
        await self._log_entity_change(
            action="Support ticket created",
            entity_type="ticket",
            entity_id=ticket.ticket_id,
            payload=payload,
            extra_metadata={"reported_by": self.user_id},
        )
        
        maps = await self._load_reference_maps([ticket])
        return SupportTicketOut(
            ticket_id=ticket.ticket_id,
            chamber_id=ticket.chamber_id,
            ticket_number=ticket.ticket_number,
            subject=ticket.subject,
            description=ticket.description,
            module_code=ticket.module_code,
            module_name=maps["module_map"].get(ticket.module_code),
            status_code=ticket.status_code,
            status_description=maps["status_map"].get(ticket.status_code),
            assigned_to=ticket.assigned_to,
            assigned_to_name=maps["user_map"].get(ticket.assigned_to),
            reported_by=ticket.reported_by,
            reported_by_name=maps["user_map"].get(ticket.reported_by),
            reported_date=ticket.reported_date,
            assigned_date=ticket.assigned_date,
            resolved_date=ticket.resolved_date,
            due_date=ticket.due_date,
            created_date=ticket.created_date,
            updated_date=ticket.updated_date,
        )
    
    async def tickets_edit(self, payload: SupportTicketEdit) -> SupportTicketOut:
        """Update an existing support ticket"""
        ticket = await self._assert_ticket_exists(payload.ticket_id)
        
        data = payload.model_dump(exclude_unset=True, exclude_none=True)
        data.pop("ticket_id", None)
        
        if data:
            # Auto-set resolved_date when status changes to RESL
            if payload.status_code != ticket.status_code:
                data["resolved_date"] = datetime.today()
            
            data["updated_by"] = self.user_id
            await self.tickets_repo.update(
                session=self.session,
                id_values=payload.ticket_id,
                data=self.tickets_repo.map_fields_to_db_column(data),
            )
        
        await self._log_entity_change(
            action="Support ticket updated",
            entity_type="ticket",
            entity_id=payload.ticket_id,
            payload=payload,
            extra_metadata={"updated_fields": list(data.keys())},
        )
        
        return await self.tickets_get_by_id(payload.ticket_id)
    
    async def tickets_delete(self, payload: SupportTicketDelete) -> dict:
        """Soft-delete a support ticket"""
        ticket = await self._assert_ticket_exists(payload.ticket_id)
        
        await self._log_entity_change(
            action="Support ticket deleted",
            entity_type="ticket",
            entity_id=payload.ticket_id,
            extra_metadata={"ticket_number": ticket.ticket_number},
        )
        
        await self.tickets_repo.delete(
            session=self.session,
            id_values=payload.ticket_id,
        )
        
        return {"ticket_id": payload.ticket_id, "deleted": True}