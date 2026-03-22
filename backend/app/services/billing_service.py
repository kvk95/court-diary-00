"""billing_service.py — Business logic for Bills, Payments, Documents"""

from datetime import date
from typing import List, Optional

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.models.cases import Cases
from app.database.models.client_bills import ClientBills
from app.database.models.client_documents import ClientDocuments
from app.database.models.client_payments import ClientPayments
from app.database.models.clients import Clients
from app.database.models.refm_billing_status import RefmBillingStatus, RefmBillingStatusConstants
from app.database.repositories.client_bills_repository import ClientBillsRepository
from app.database.repositories.client_documents_repository import ClientDocumentsRepository
from app.database.repositories.client_payments_repository import ClientPaymentsRepository
from app.database.repositories.clients_repository import ClientsRepository
from app.dtos.base.paginated_out import PagingBuilder, PagingData
from app.dtos.billing_dto import (
    BillCreate,
    BillDelete,
    BillDetailOut,
    BillEdit,
    BillListOut,
    BillSummaryStats,
    DocumentCreate,
    DocumentEdit,
    DocumentOut,
    PaymentCreate,
    PaymentDelete,
    PaymentOut,
)
from app.services.base.secured_base_service import BaseSecuredService
from app.validators import ErrorCodes, ValidationErrorDetail


def _f(v) -> float:
    """Safely convert Decimal/None → float."""
    return float(v) if v is not None else 0.0


class BillingService(BaseSecuredService):
    def __init__(
        self,
        session: AsyncSession,
        bills_repo: Optional[ClientBillsRepository] = None,
        payments_repo: Optional[ClientPaymentsRepository] = None,
        documents_repo: Optional[ClientDocumentsRepository] = None,
        clients_repo: Optional[ClientsRepository] = None,
    ):
        super().__init__(session)
        self.bills_repo = bills_repo or ClientBillsRepository()
        self.payments_repo = payments_repo or ClientPaymentsRepository()
        self.documents_repo = documents_repo or ClientDocumentsRepository()
        self.clients_repo = clients_repo or ClientsRepository()

    # ─────────────────────────────────────────────────────────────────────
    # PRIVATE HELPERS
    # ─────────────────────────────────────────────────────────────────────

    async def _get_bill_or_404(self, bill_id: int) -> ClientBills:
        bill = await self.bills_repo.get_by_id(
            session=self.session,
            filters={ClientBills.bill_id: bill_id, ClientBills.chamber_id: self.chamber_id},
        )
        if not bill:
            raise ValidationErrorDetail(code=ErrorCodes.NOT_FOUND, message="Bill not found")
        return bill

    async def _verify_client(self, client_id: int) -> Clients:
        client = await self.clients_repo.get_by_id(
            session=self.session,
            filters={Clients.client_id: client_id, Clients.chamber_id: self.chamber_id},
        )
        if not client:
            raise ValidationErrorDetail(code=ErrorCodes.NOT_FOUND, message="Client not found")
        return client

    async def _client_name(self, client_id: int) -> str:
        c = await self.session.get(Clients, client_id)
        return c.client_name if c else ""

    async def _case_number(self, case_id: Optional[int]) -> Optional[str]:
        if not case_id:
            return None
        c = await self.session.get(Cases, case_id)
        return c.case_number if c else None

    async def _payments_for_bill(self, bill_id: int) -> List[PaymentOut]:
        payments = await self.payments_repo.list_all(
            session=self.session,
            where=[ClientPayments.bill_id == bill_id],
            order_by=[ClientPayments.payment_date.desc()],
        )
        return [
            PaymentOut(
                payment_id=p.payment_id,
                bill_id=p.bill_id,
                client_id=p.client_id,
                payment_date=p.payment_date,
                amount=_f(p.amount),
                payment_mode=p.payment_mode,
                reference_no=p.reference_no,
                bank_name=p.bank_name,
                receipt_number=p.receipt_number,
                receipt_date=p.receipt_date,
                notes=p.notes,
                created_date=p.created_date,
            )
            for p in payments
        ]

    async def _recalculate_bill(self, bill_id: int) -> None:
        """After any payment add/delete, recompute paid_amount and status on the bill."""
        total_paid = _f(
            await self.session.scalar(
                select(func.coalesce(func.sum(ClientPayments.amount), 0))
                .where(ClientPayments.bill_id == bill_id)
            )
        )
        bill = await self.bills_repo.get_by_id(session=self.session, id_values=bill_id)
        if not bill:
            return

        total = _f(bill.total_amount)
        if total_paid >= total:
            new_status = RefmBillingStatusConstants.PAID
        elif total_paid > 0:
            new_status = RefmBillingStatusConstants.PENDING
        elif bill.due_date and bill.due_date < date.today():
            new_status = RefmBillingStatusConstants.OVERDUE
        else:
            new_status = bill.status_code or RefmBillingStatusConstants.PENDING

        await self.bills_repo.update(
            session=self.session,
            id_values=bill_id,
            data={"paid_amount": round(total_paid, 2), "status_code": new_status},
        )

    def _bill_to_list_out(
        self,
        b: ClientBills,
        client_map: dict,
        case_map: dict,
        status_map: dict,
        color_map: dict,
    ) -> BillListOut:
        total = _f(b.total_amount)
        paid = _f(b.paid_amount)
        return BillListOut(
            bill_id=b.bill_id,
            bill_number=b.bill_number,
            client_id=b.client_id,
            client_name=client_map.get(b.client_id, ""),
            case_id=b.case_id,
            case_number=case_map.get(b.case_id) if b.case_id else None,
            bill_date=b.bill_date,
            due_date=b.due_date,
            amount=_f(b.amount),
            tax_amount=_f(b.tax_amount),
            total_amount=total,
            paid_amount=paid,
            balance_amount=round(total - paid, 2),
            status_code=b.status_code,
            status_description=status_map.get(b.status_code) if b.status_code else None,
            color_code=color_map.get(b.status_code) if b.status_code else None,
            created_date=b.created_date,
        )

    # ─────────────────────────────────────────────────────────────────────
    # BILLS — Stats
    # ─────────────────────────────────────────────────────────────────────

    async def bills_get_stats(self) -> BillSummaryStats:
        today = date.today()
        cid = self.chamber_id

        row = (await self.session.execute(
            select(
                func.count(ClientBills.bill_id).label("cnt"),
                func.coalesce(func.sum(ClientBills.total_amount), 0).label("total"),
                func.coalesce(func.sum(ClientBills.paid_amount), 0).label("paid"),
            ).where(ClientBills.chamber_id == cid)
        )).first()

        billed = _f(row.total)
        paid = _f(row.paid)

        overdue_row = (await self.session.execute(
            select(
                func.count(ClientBills.bill_id).label("cnt"),
                func.coalesce(
                    func.sum(ClientBills.total_amount - ClientBills.paid_amount), 0
                ).label("amt"),
            ).where(
                ClientBills.chamber_id == cid,
                ClientBills.status_code.notin_([
                    RefmBillingStatusConstants.PAID,
                    RefmBillingStatusConstants.CANCELLED,
                ]),
                ClientBills.due_date < today,
            )
        )).first()

        return BillSummaryStats(
            total_billed=round(billed, 2),
            total_paid=round(paid, 2),
            total_outstanding=round(billed - paid, 2),
            total_overdue=round(_f(overdue_row.amt), 2),
            bill_count=row.cnt or 0,
            overdue_count=overdue_row.cnt or 0,
        )

    # ─────────────────────────────────────────────────────────────────────
    # BILLS — Paged list
    # ─────────────────────────────────────────────────────────────────────

    async def bills_get_paged(
        self,
        page: int,
        limit: int,
        client_id: Optional[int] = None,
        status_code: Optional[str] = None,
        date_from: Optional[date] = None,
        date_to: Optional[date] = None,
    ) -> PagingData[BillListOut]:
        conditions = [ClientBills.chamber_id == self.chamber_id]
        if client_id:
            conditions.append(ClientBills.client_id == client_id)
        if status_code and status_code.upper() != "ALL":
            conditions.append(ClientBills.status_code == status_code.upper())
        if date_from:
            conditions.append(ClientBills.bill_date >= date_from)
        if date_to:
            conditions.append(ClientBills.bill_date <= date_to)

        bills, total = await self.bills_repo.list_paginated(
            session=self.session, page=page, limit=limit,
            where=conditions, order_by=[ClientBills.bill_date.desc()],
        )

        client_ids = list({b.client_id for b in bills})
        case_ids = list({b.case_id for b in bills if b.case_id})
        s_codes = list({b.status_code for b in bills if b.status_code})

        client_map: dict = {}
        if client_ids:
            rows = await self.session.execute(
                select(Clients.client_id, Clients.client_name)
                .where(Clients.client_id.in_(client_ids))
            )
            client_map = {r.client_id: r.client_name for r in rows}

        case_map: dict = {}
        if case_ids:
            rows = await self.session.execute(
                select(Cases.case_id, Cases.case_number)
                .where(Cases.case_id.in_(case_ids))
            )
            case_map = {r.case_id: r.case_number for r in rows}

        status_map: dict = {}
        color_map: dict = {}
        if s_codes:
            rows = await self.session.execute(
                select(RefmBillingStatus.code, RefmBillingStatus.description, RefmBillingStatus.color_code)
                .where(RefmBillingStatus.code.in_(s_codes))
            )
            for r in rows:
                status_map[r.code] = r.description
                color_map[r.code] = r.color_code

        records = [
            self._bill_to_list_out(b, client_map, case_map, status_map, color_map)
            for b in bills
        ]
        return PagingBuilder(total_records=total, page=page, limit=limit).build(records=records)

    # ─────────────────────────────────────────────────────────────────────
    # BILLS — Detail
    # ─────────────────────────────────────────────────────────────────────

    async def bills_get_by_id(self, bill_id: int) -> BillDetailOut:
        b = await self._get_bill_or_404(bill_id)
        st = await self.session.get(RefmBillingStatus, b.status_code) if b.status_code else None
        payments = await self._payments_for_bill(bill_id)
        total = _f(b.total_amount)
        paid = _f(b.paid_amount)
        return BillDetailOut(
            bill_id=b.bill_id,
            bill_number=b.bill_number,
            client_id=b.client_id,
            client_name=await self._client_name(b.client_id),
            case_id=b.case_id,
            case_number=await self._case_number(b.case_id),
            bill_date=b.bill_date,
            due_date=b.due_date,
            amount=_f(b.amount),
            tax_amount=_f(b.tax_amount),
            total_amount=total,
            paid_amount=paid,
            balance_amount=round(total - paid, 2),
            status_code=b.status_code,
            status_description=st.description if st else None,
            color_code=st.color_code if st else None,
            service_description=b.service_description,
            notes=b.notes,
            created_date=b.created_date,
            payments=[p.model_dump() for p in payments],
        )

    # ─────────────────────────────────────────────────────────────────────
    # BILLS — Create / Edit / Delete
    # ─────────────────────────────────────────────────────────────────────

    async def bills_add(self, payload: BillCreate) -> BillDetailOut:
        await self._verify_client(payload.client_id)
        data = payload.model_dump(exclude_unset=True, exclude_none=True)
        data["chamber_id"] = self.chamber_id
        bill = await self.bills_repo.create(
            session=self.session,
            data=self.bills_repo.map_fields_to_db_column(data),
        )
        return await self.bills_get_by_id(bill.bill_id)

    async def bills_edit(self, payload: BillEdit) -> BillDetailOut:
        await self._get_bill_or_404(payload.bill_id)
        data = payload.model_dump(exclude_unset=True, exclude_none=True)
        data.pop("bill_id", None)
        if data:
            await self.bills_repo.update(
                session=self.session,
                id_values=payload.bill_id,
                data=self.bills_repo.map_fields_to_db_column(data),
            )
        return await self.bills_get_by_id(payload.bill_id)

    async def bills_delete(self, payload: BillDelete) -> dict:
        await self._get_bill_or_404(payload.bill_id)
        payment_count = await self.session.scalar(
            select(func.count(ClientPayments.payment_id))
            .where(ClientPayments.bill_id == payload.bill_id)
        ) or 0
        if payment_count > 0:
            raise ValidationErrorDetail(
                code=ErrorCodes.VALIDATION_ERROR,
                message=f"Cannot delete: {payment_count} payment(s) recorded. Mark as cancelled instead.",
            )
        await self.bills_repo.delete(session=self.session, id_values=payload.bill_id, soft=False)
        return {"bill_id": payload.bill_id, "deleted": True}

    # ─────────────────────────────────────────────────────────────────────
    # PAYMENTS — Get for bill
    # ─────────────────────────────────────────────────────────────────────

    async def payments_get_by_bill(self, bill_id: int) -> List[PaymentOut]:
        await self._get_bill_or_404(bill_id)
        return await self._payments_for_bill(bill_id)

    # ─────────────────────────────────────────────────────────────────────
    # PAYMENTS — Record
    # ─────────────────────────────────────────────────────────────────────

    async def payments_add(self, payload: PaymentCreate) -> PaymentOut:
        bill = await self._get_bill_or_404(payload.bill_id)
        balance = round(_f(bill.total_amount) - _f(bill.paid_amount), 2)
        if round(payload.amount, 2) > balance:
            raise ValidationErrorDetail(
                code=ErrorCodes.VALIDATION_ERROR,
                message=f"Payment ₹{payload.amount} exceeds outstanding balance ₹{balance}",
            )
        data = payload.model_dump(exclude_unset=True, exclude_none=True)
        data["chamber_id"] = self.chamber_id
        data["client_id"] = bill.client_id
        payment = await self.payments_repo.create(
            session=self.session,
            data=self.payments_repo.map_fields_to_db_column(data),
        )
        await self._recalculate_bill(payload.bill_id)
        return PaymentOut(
            payment_id=payment.payment_id,
            bill_id=payment.bill_id,
            client_id=payment.client_id,
            payment_date=payment.payment_date,
            amount=_f(payment.amount),
            payment_mode=payment.payment_mode,
            reference_no=payment.reference_no,
            bank_name=payment.bank_name,
            receipt_number=payment.receipt_number,
            receipt_date=payment.receipt_date,
            notes=payment.notes,
            created_date=payment.created_date,
        )

    # ─────────────────────────────────────────────────────────────────────
    # PAYMENTS — Delete
    # ─────────────────────────────────────────────────────────────────────

    async def payments_delete(self, payload: PaymentDelete) -> dict:
        payment = await self.payments_repo.get_by_id(
            session=self.session,
            filters={
                ClientPayments.payment_id: payload.payment_id,
                ClientPayments.chamber_id: self.chamber_id,
            },
        )
        if not payment:
            raise ValidationErrorDetail(code=ErrorCodes.NOT_FOUND, message="Payment not found")
        bill_id = payment.bill_id
        await self.payments_repo.delete(session=self.session, id_values=payload.payment_id, soft=False)
        await self._recalculate_bill(bill_id)
        return {"payment_id": payload.payment_id, "deleted": True}

    # ─────────────────────────────────────────────────────────────────────
    # DOCUMENTS — Paged list
    # ─────────────────────────────────────────────────────────────────────

    async def documents_get_paged(
        self,
        page: int,
        limit: int,
        client_id: Optional[int] = None,
        custody_status: Optional[str] = None,
    ) -> PagingData[DocumentOut]:
        conditions = [ClientDocuments.chamber_id == self.chamber_id]
        if client_id:
            conditions.append(ClientDocuments.client_id == client_id)
        if custody_status:
            conditions.append(ClientDocuments.custody_status == custody_status.upper())

        docs, total = await self.documents_repo.list_paginated(
            session=self.session, page=page, limit=limit,
            where=conditions, order_by=[ClientDocuments.received_date.desc()],
        )

        client_ids = list({d.client_id for d in docs})
        case_ids = list({d.case_id for d in docs if d.case_id})

        client_map: dict = {}
        if client_ids:
            rows = await self.session.execute(
                select(Clients.client_id, Clients.client_name)
                .where(Clients.client_id.in_(client_ids))
            )
            client_map = {r.client_id: r.client_name for r in rows}

        case_map: dict = {}
        if case_ids:
            rows = await self.session.execute(
                select(Cases.case_id, Cases.case_number)
                .where(Cases.case_id.in_(case_ids))
            )
            case_map = {r.case_id: r.case_number for r in rows}

        records = [
            DocumentOut(
                document_id=d.document_id, client_id=d.client_id,
                client_name=client_map.get(d.client_id, ""),
                case_id=d.case_id,
                case_number=case_map.get(d.case_id) if d.case_id else None,
                document_name=d.document_name, document_type=d.document_type,
                document_category=d.document_category, received_date=d.received_date,
                received_from=d.received_from, returned_date=d.returned_date,
                returned_to=d.returned_to, custody_status=d.custody_status,
                storage_location=d.storage_location, file_number=d.file_number,
                notes=d.notes, created_date=d.created_date,
            )
            for d in docs
        ]
        return PagingBuilder(total_records=total, page=page, limit=limit).build(records=records)

    # ─────────────────────────────────────────────────────────────────────
    # DOCUMENTS — Add / Edit / Delete
    # ─────────────────────────────────────────────────────────────────────

    async def documents_add(self, payload: DocumentCreate) -> DocumentOut:
        client = await self._verify_client(payload.client_id)
        data = payload.model_dump(exclude_unset=True, exclude_none=True)
        data["chamber_id"] = self.chamber_id
        doc = await self.documents_repo.create(
            session=self.session,
            data=self.documents_repo.map_fields_to_db_column(data),
        )
        return DocumentOut(
            document_id=doc.document_id, client_id=doc.client_id,
            client_name=client.client_name, case_id=doc.case_id,
            case_number=await self._case_number(doc.case_id),
            document_name=doc.document_name, document_type=doc.document_type,
            document_category=doc.document_category, received_date=doc.received_date,
            received_from=doc.received_from, returned_date=doc.returned_date,
            returned_to=doc.returned_to, custody_status=doc.custody_status,
            storage_location=doc.storage_location, file_number=doc.file_number,
            notes=doc.notes, created_date=doc.created_date,
        )

    async def documents_edit(self, payload: DocumentEdit) -> DocumentOut:
        doc = await self.documents_repo.get_by_id(
            session=self.session,
            filters={ClientDocuments.document_id: payload.document_id, ClientDocuments.chamber_id: self.chamber_id},
        )
        if not doc:
            raise ValidationErrorDetail(code=ErrorCodes.NOT_FOUND, message="Document not found")
        data = payload.model_dump(exclude_unset=True, exclude_none=True)
        data.pop("document_id", None)
        if data:
            doc = await self.documents_repo.update(
                session=self.session, id_values=payload.document_id,
                data=self.documents_repo.map_fields_to_db_column(data),
            )
        return DocumentOut(
            document_id=doc.document_id, client_id=doc.client_id,
            client_name=await self._client_name(doc.client_id), case_id=doc.case_id,
            case_number=await self._case_number(doc.case_id),
            document_name=doc.document_name, document_type=doc.document_type,
            document_category=doc.document_category, received_date=doc.received_date,
            received_from=doc.received_from, returned_date=doc.returned_date,
            returned_to=doc.returned_to, custody_status=doc.custody_status,
            storage_location=doc.storage_location, file_number=doc.file_number,
            notes=doc.notes, created_date=doc.created_date,
        )

    async def documents_delete(self, document_id: int) -> dict:
        doc = await self.documents_repo.get_by_id(
            session=self.session,
            filters={ClientDocuments.document_id: document_id, ClientDocuments.chamber_id: self.chamber_id},
        )
        if not doc:
            raise ValidationErrorDetail(code=ErrorCodes.NOT_FOUND, message="Document not found")
        await self.documents_repo.delete(session=self.session, id_values=document_id, soft=False)
        return {"document_id": document_id, "deleted": True}
