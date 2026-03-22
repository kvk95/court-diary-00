"""billing_service.py — Business logic only; all DB queries delegated to repositories"""

from datetime import date
from typing import List, Optional

from sqlalchemy.ext.asyncio import AsyncSession

from app.database.models.client_bills import ClientBills
from app.database.models.client_documents import ClientDocuments
from app.database.models.client_payments import ClientPayments
from app.database.models.clients import Clients
from app.database.models.refm_billing_status import RefmBillingStatusConstants
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

    async def _recalculate_bill(self, bill_id: int) -> None:
        """After any payment change, ask repo to recompute paid_amount + status."""
        bill = await self.bills_repo.get_by_id(session=self.session, id_values=bill_id)
        if not bill:
            return
        total_paid = await self.payments_repo.get_total_paid_for_bill(
            session=self.session, bill_id=bill_id
        )
        await self.bills_repo.recalculate_paid_amount(
            session=self.session,
            bill_id=bill_id,
            total_paid=total_paid,
            bill=bill,
            today=date.today(),
            paid_code=RefmBillingStatusConstants.PAID,
            pending_code=RefmBillingStatusConstants.PENDING,
            overdue_code=RefmBillingStatusConstants.OVERDUE,
        )

    def _row_to_bill_list_out(self, row: dict) -> BillListOut:
        b: ClientBills = row["bill"]
        total = _f(b.total_amount)
        paid = _f(b.paid_amount)
        return BillListOut(
            bill_id=b.bill_id,
            bill_number=b.bill_number,
            client_id=b.client_id,
            client_name=row["client_name"],
            case_id=b.case_id,
            case_number=row["case_number"],
            bill_date=b.bill_date,
            due_date=b.due_date,
            amount=_f(b.amount),
            tax_amount=_f(b.tax_amount),
            total_amount=total,
            paid_amount=paid,
            balance_amount=round(total - paid, 2),
            status_code=b.status_code,
            status_description=row["status_description"],
            color_code=row["color_code"],
            created_date=b.created_date,
        )

    # ─────────────────────────────────────────────────────────────────────
    # BILLS — Stats
    # ─────────────────────────────────────────────────────────────────────

    async def bills_get_stats(self) -> BillSummaryStats:
        stats = await self.bills_repo.get_billing_stats(
            session=self.session,
            chamber_id=self.chamber_id,
            today=date.today(),
            paid_code=RefmBillingStatusConstants.PAID,
            cancelled_code=RefmBillingStatusConstants.CANCELLED,
            pending_code=RefmBillingStatusConstants.PENDING,
        )
        billed = stats["total"]
        paid = stats["paid"]
        return BillSummaryStats(
            total_billed=round(billed, 2),
            total_paid=round(paid, 2),
            total_outstanding=round(billed - paid, 2),
            total_overdue=round(stats["overdue_amt"], 2),
            bill_count=stats["bill_count"],
            overdue_count=stats["overdue_count"],
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
        rows, total = await self.bills_repo.list_bills_enriched(
            session=self.session,
            chamber_id=self.chamber_id,
            page=page,
            limit=limit,
            client_id=client_id,
            status_code=status_code,
            date_from=date_from,
            date_to=date_to,
        )
        records = [self._row_to_bill_list_out(r) for r in rows]
        return PagingBuilder(total_records=total, page=page, limit=limit).build(records=records)

    # ─────────────────────────────────────────────────────────────────────
    # BILLS — Detail
    # ─────────────────────────────────────────────────────────────────────

    async def bills_get_by_id(self, bill_id: int) -> BillDetailOut:
        b = await self._get_bill_or_404(bill_id)

        # Get status description via session.get (single PK lookup — acceptable in service)
        from app.database.models.refm_billing_status import RefmBillingStatus
        st = await self.session.get(RefmBillingStatus, b.status_code) if b.status_code else None

        # Payments via repo
        payments_raw = await self.payments_repo.list_all(
            session=self.session,
            where=[ClientPayments.bill_id == bill_id],
            order_by=[ClientPayments.payment_date.desc()],
        )
        payments = [
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
            for p in payments_raw
        ]

        # Client name via repo
        client = await self.clients_repo.get_by_id(session=self.session, id_values=b.client_id)
        client_name = client.client_name if client else ""

        # Case number via session.get (acceptable — single PK)
        from app.database.models.cases import Cases
        case = await self.session.get(Cases, b.case_id) if b.case_id else None
        case_number = case.case_number if case else None

        total = _f(b.total_amount)
        paid = _f(b.paid_amount)

        return BillDetailOut(
            bill_id=b.bill_id,
            bill_number=b.bill_number,
            client_id=b.client_id,
            client_name=client_name,
            case_id=b.case_id,
            case_number=case_number,
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
        payment_count = await self.bills_repo.count_payments(
            session=self.session, bill_id=payload.bill_id
        )
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
        payments_raw = await self.payments_repo.list_all(
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
            for p in payments_raw
        ]

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
        rows, total = await self.documents_repo.list_documents_enriched(
            session=self.session,
            chamber_id=self.chamber_id,
            page=page,
            limit=limit,
            client_id=client_id,
            custody_status=custody_status,
        )
        records = [
            DocumentOut(
                document_id=r["doc"].document_id,
                client_id=r["doc"].client_id,
                client_name=r["client_name"],
                case_id=r["doc"].case_id,
                case_number=r["case_number"],
                document_name=r["doc"].document_name,
                document_type=r["doc"].document_type,
                document_category=r["doc"].document_category,
                received_date=r["doc"].received_date,
                received_from=r["doc"].received_from,
                returned_date=r["doc"].returned_date,
                returned_to=r["doc"].returned_to,
                custody_status=r["doc"].custody_status,
                storage_location=r["doc"].storage_location,
                file_number=r["doc"].file_number,
                notes=r["doc"].notes,
                created_date=r["doc"].created_date,
            )
            for r in rows
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
        from app.database.models.cases import Cases
        case = await self.session.get(Cases, doc.case_id) if doc.case_id else None
        return DocumentOut(
            document_id=doc.document_id, client_id=doc.client_id,
            client_name=client.client_name, case_id=doc.case_id,
            case_number=case.case_number if case else None,
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
        client = await self.clients_repo.get_by_id(session=self.session, id_values=doc.client_id)
        from app.database.models.cases import Cases
        case = await self.session.get(Cases, doc.case_id) if doc.case_id else None
        return DocumentOut(
            document_id=doc.document_id, client_id=doc.client_id,
            client_name=client.client_name if client else "",
            case_id=doc.case_id,
            case_number=case.case_number if case else None,
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
