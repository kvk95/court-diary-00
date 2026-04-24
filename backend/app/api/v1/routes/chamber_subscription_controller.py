# app/api/v1/routes/user/chamber_subscription_controller.py

from typing import Optional

from fastapi import Depends, Body, Query

from app.api.v1.routes.base.base_controller import BaseController
from app.auth.permissions import PType, require_permission
from app.database.models.refm_modules import RefmModulesEnum
from app.dependencies import get_chamber_subscription_service
from app.dtos.base.base_out_dto import BaseOutDto
from app.dtos.base.paginated_out import PagingData
from app.dtos.chamber_subscriptions_dto import BillingInvoiceItem, ChamberSubscriptionOut, ChangePlanIn, SubscriptionPlanItem, SubscriptionStats
from app.services.chamber_subscriptions_service import ChamberSubscriptionService

_BILL = RefmModulesEnum.BILLING

class ChamberSubscriptionController(BaseController):
    CONTROLLER_NAME = "chamber-subscription"

    @BaseController.get(
        "/stats",
        summary="Subscription stats",
        response_model=BaseOutDto[SubscriptionStats],
    )
    async def get_subscription_stats(
        self,
        service: ChamberSubscriptionService = Depends(get_chamber_subscription_service),
    ):
        return self.success(result=await service.get_subscription_stats())

    # -------------------------------------------------------
    # GET CURRENT SUBSCRIPTION
    # -------------------------------------------------------
    @BaseController.get(
        "",
        summary="Get current subscription",
        response_model=BaseOutDto[ChamberSubscriptionOut],
    )
    async def get_subscription(
        self,
        service: ChamberSubscriptionService = Depends(get_chamber_subscription_service),
    ):
        return self.success(result=await service.get_current_subscription())
    
    @BaseController.get(
        "/billing-history",
        summary="Billing history",
        response_model=BaseOutDto[PagingData[BillingInvoiceItem]],
    )
    async def get_billing_history(
        self,
        page: int = Query(1, ge=1),
        limit: int = Query(10, ge=1, le=100),
        status: Optional[str] = Query(None),
        service: ChamberSubscriptionService = Depends(get_chamber_subscription_service),
    ):
        return self.success(
            result=await service.get_billing_history(page, limit, status)
        )

    # -------------------------------------------------------
    # GET PLANS
    # -------------------------------------------------------
    @BaseController.get(
        "/plans",
        summary="Get available plans",
        response_model=BaseOutDto[list[SubscriptionPlanItem]],
    )
    async def get_plans(
        self,
        service: ChamberSubscriptionService = Depends(get_chamber_subscription_service),
    ):
        return self.success(result=await service.get_plans())

    # -------------------------------------------------------
    # CHANGE PLAN
    # -------------------------------------------------------
    @BaseController.post(
        "/change",
        summary="Change subscription plan",
        response_model=BaseOutDto[ChamberSubscriptionOut],
        dependencies=[Depends(require_permission(_BILL, permission=PType.CREATE))],
    )
    async def change_plan(
        self,
        payload: ChangePlanIn = Body(...),
        service: ChamberSubscriptionService = Depends(get_chamber_subscription_service),
    ):
        return self.success(
            result=await service.change_plan(payload)
        )
    
    @BaseController.post(
        "/cancel",
        summary="Cancel subscription",
        response_model=BaseOutDto[ChamberSubscriptionOut],
        dependencies=[Depends(require_permission(_BILL, permission=PType.WRITE))],
    )
    async def cancel_subscription(
        self,
        service: ChamberSubscriptionService = Depends(get_chamber_subscription_service),
    ):
        return self.success(result=await service.cancel_subscription())