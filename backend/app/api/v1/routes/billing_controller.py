"""billing_controller.py — HTTP routes for Bills, Payments, Documents"""

from typing import Optional

from fastapi import Body, Depends, Path, Query

from app.api.v1.routes.base.base_controller import BaseController
from app.dependencies import get_billing_service
from app.dtos.base.base_out_dto import BaseOutDto
from app.dtos.base.paginated_out import PagingData
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
from app.services.billing_service import BillingService
from app.utils.constants import PAGINATION_DEFAULT_LIMIT, PAGINATION_DEFAULT_PAGE
from datetime import date
from typing import List


class BillingController(BaseController):
    CONTROLLER_NAME = "billing"

    # ── Stats ─────────────────────────────────────────────────────────────

    @BaseController.get(
        "/stats",
        summary="Billing summary stats (4 stat cards)",
        response_model=BaseOutDto[BillSummaryStats],
    )
    async def bills_get_stats(
        self,
        service: BillingService = Depends(get_billing_service),
    ) -> BaseOutDto[BillSummaryStats]:
        return self.success(result=await service.bills_get_stats())

    # ── Bills — List ──────────────────────────────────────────────────────

    @BaseController.get(
        "/bills/paged",
        summary="Get bills (paginated)",
        response_model=BaseOutDto[PagingData[BillListOut]],
    )
    async def bills_get_paged(
        self,
        page: int = Query(PAGINATION_DEFAULT_PAGE, ge=1),
        limit: int = Query(PAGINATION_DEFAULT_LIMIT, ge=1, le=500),
        client_id: Optional[int] = Query(None, description="Filter by client"),
        status_code: Optional[str] = Query(None, description="PN | PD | OV | CN | AD"),
        date_from: Optional[date] = Query(None),
        date_to: Optional[date] = Query(None),
        service: BillingService = Depends(get_billing_service),
    ) -> BaseOutDto[PagingData[BillListOut]]:
        return self.success(result=await service.bills_get_paged(
            page=page, limit=limit, client_id=client_id,
            status_code=status_code, date_from=date_from, date_to=date_to,
        ))

    # ── Bills — Detail ────────────────────────────────────────────────────

    @BaseController.get(
        "/bills/{bill_id}",
        summary="Get bill detail (includes payment history)",
        response_model=BaseOutDto[BillDetailOut],
    )
    async def bills_get_by_id(
        self,
        bill_id: int = Path(..., gt=0),
        service: BillingService = Depends(get_billing_service),
    ) -> BaseOutDto[BillDetailOut]:
        return self.success(result=await service.bills_get_by_id(bill_id=bill_id))

    # ── Bills — Add ───────────────────────────────────────────────────────

    @BaseController.post(
        "/bills/add",
        summary="Create a new bill",
        response_model=BaseOutDto[BillDetailOut],
    )
    async def bills_add(
        self,
        payload: BillCreate = Body(...),
        service: BillingService = Depends(get_billing_service),
    ) -> BaseOutDto[BillDetailOut]:
        return self.success(result=await service.bills_add(payload=payload))

    # ── Bills — Edit ──────────────────────────────────────────────────────

    @BaseController.put(
        "/bills/edit",
        summary="Edit a bill",
        response_model=BaseOutDto[BillDetailOut],
    )
    async def bills_edit(
        self,
        payload: BillEdit = Body(...),
        service: BillingService = Depends(get_billing_service),
    ) -> BaseOutDto[BillDetailOut]:
        return self.success(result=await service.bills_edit(payload=payload))

    # ── Bills — Delete ────────────────────────────────────────────────────

    @BaseController.delete(
        "/bills/delete",
        summary="Delete a bill (blocked if payments exist — use status=CN instead)",
        response_model=BaseOutDto[dict],
    )
    async def bills_delete(
        self,
        payload: BillDelete = Body(...),
        service: BillingService = Depends(get_billing_service),
    ) -> BaseOutDto[dict]:
        return self.success(result=await service.bills_delete(payload=payload))

    # ── Payments — List for a bill ────────────────────────────────────────

    @BaseController.get(
        "/bills/{bill_id}/payments",
        summary="Get all payments for a bill",
        response_model=BaseOutDto[List[PaymentOut]],
    )
    async def payments_get_by_bill(
        self,
        bill_id: int = Path(..., gt=0),
        service: BillingService = Depends(get_billing_service),
    ) -> BaseOutDto[List[PaymentOut]]:
        return self.success(result=await service.payments_get_by_bill(bill_id=bill_id))

    # ── Payments — Record ─────────────────────────────────────────────────

    @BaseController.post(
        "/payments/add",
        summary="Record a payment against a bill",
        response_model=BaseOutDto[PaymentOut],
    )
    async def payments_add(
        self,
        payload: PaymentCreate = Body(...),
        service: BillingService = Depends(get_billing_service),
    ) -> BaseOutDto[PaymentOut]:
        return self.success(result=await service.payments_add(payload=payload))

    # ── Payments — Delete ─────────────────────────────────────────────────

    @BaseController.delete(
        "/payments/delete",
        summary="Delete a payment (recalculates bill balance)",
        response_model=BaseOutDto[dict],
    )
    async def payments_delete(
        self,
        payload: PaymentDelete = Body(...),
        service: BillingService = Depends(get_billing_service),
    ) -> BaseOutDto[dict]:
        return self.success(result=await service.payments_delete(payload=payload))

    # ── Documents — List ──────────────────────────────────────────────────

    @BaseController.get(
        "/documents/paged",
        summary="Get documents (paginated)",
        response_model=BaseOutDto[PagingData[DocumentOut]],
    )
    async def documents_get_paged(
        self,
        page: int = Query(PAGINATION_DEFAULT_PAGE, ge=1),
        limit: int = Query(PAGINATION_DEFAULT_LIMIT, ge=1, le=200),
        client_id: Optional[int] = Query(None),
        custody_status: Optional[str] = Query(None, description="H=Held, R=Returned, L=Lost, D=Destroyed"),
        service: BillingService = Depends(get_billing_service),
    ) -> BaseOutDto[PagingData[DocumentOut]]:
        return self.success(result=await service.documents_get_paged(
            page=page, limit=limit, client_id=client_id, custody_status=custody_status
        ))

    # ── Documents — Add ───────────────────────────────────────────────────

    @BaseController.post(
        "/documents/add",
        summary="Add a document record",
        response_model=BaseOutDto[DocumentOut],
    )
    async def documents_add(
        self,
        payload: DocumentCreate = Body(...),
        service: BillingService = Depends(get_billing_service),
    ) -> BaseOutDto[DocumentOut]:
        return self.success(result=await service.documents_add(payload=payload))

    # ── Documents — Edit ──────────────────────────────────────────────────

    @BaseController.put(
        "/documents/edit",
        summary="Edit a document record",
        response_model=BaseOutDto[DocumentOut],
    )
    async def documents_edit(
        self,
        payload: DocumentEdit = Body(...),
        service: BillingService = Depends(get_billing_service),
    ) -> BaseOutDto[DocumentOut]:
        return self.success(result=await service.documents_edit(payload=payload))

    # ── Documents — Delete ────────────────────────────────────────────────

    @BaseController.delete(
        "/documents/{document_id}/delete",
        summary="Delete a document record",
        response_model=BaseOutDto[dict],
    )
    async def documents_delete(
        self,
        document_id: int = Path(..., gt=0),
        service: BillingService = Depends(get_billing_service),
    ) -> BaseOutDto[dict]:
        return self.success(result=await service.documents_delete(document_id=document_id))
