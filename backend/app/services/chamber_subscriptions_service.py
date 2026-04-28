# app/services/chamber_subscriptions_service.py

from datetime import date, datetime, timedelta, timezone
import secrets
import string
from typing import Optional

from sqlalchemy.ext.asyncio import AsyncSession

from app.database.models.chamber_subscriptions import ChamberSubscriptions
from app.database.models.refm_billing_cycle import RefmBillingCycleConstants
from app.database.models.refm_currency import RefmCurrencyConstants
from app.database.models.refm_invoice_status import RefmInvoiceStatusConstants
from app.database.models.refm_subscription_status import RefmSubscriptionStatusConstants
from app.database.repositories.billing_invoices_repository import BillingInvoicesRepository
from app.database.repositories.chamber_repository import ChamberRepository
from app.database.repositories.chamber_subscriptions_repository import ChamberSubscriptionsRepository
from app.dtos.base.paginated_out import PagingBuilder
from app.dtos.chamber_subscriptions_dto import BillingInvoiceItem, ChamberSubscriptionOut, ChangePlanIn, SubscriptionPlanItem, SubscriptionStats, UsageStats
from app.services.base.secured_base_service import BaseSecuredService
from app.database.models.refm_plan_types import RefmPlanTypesConstants
from app.utils.constants import SUPERADMIN_ROLE_CODE
from app.validators.error_codes import ErrorCodes
from app.validators.validation_errors import ValidationErrorDetail


class ChamberSubscriptionService(BaseSecuredService):

    def __init__(
        self,
        session: AsyncSession,
        chamber_repo: Optional[ChamberRepository] = None,
        chamber_subscription_repo: Optional[ChamberSubscriptionsRepository] = None,
        billing_invoice_repo: Optional[BillingInvoicesRepository] = None,
    ):
        super().__init__(session)
        self.chamber_repo = chamber_repo or ChamberRepository()
        self.chamber_subscription_repo = chamber_subscription_repo or ChamberSubscriptionsRepository()
        self.billing_invoice_repo = billing_invoice_repo or BillingInvoicesRepository()        

    def _to_out(self, sub, plan_name, max_users, max_cases):
        return ChamberSubscriptionOut(
            plan_code=sub.plan_code,
            plan_name=plan_name,
            billing_cycle=sub.billing_cycle,
            status_code=sub.status_code,
            next_renewal_date=sub.next_renewal_date,
            next_amount=sub.price_amt,
            max_users=max_users,
            max_cases=max_cases,
        )

    def _generate_invoice_number(self) -> str:
        """Generate ticket: 8-char timestamp (YYMMDDHH) + 7 random chars."""
        # Timestamp: YYMMDDHH (e.g., "26041714" = 2026-04-17 14:xx UTC)
        ts = datetime.now(timezone.utc).strftime("%y%m%d%H")
        
        # 7 random alphanumeric chars
        alphabet = string.ascii_uppercase + string.digits
        suffix = ''.join(secrets.choice(alphabet) for _ in range(7))
        
        return ts + suffix  # Total: 15 chars
    
    async def _create_invoice_for_subscription(
        self,
        subscription,
        billing_cycle: str,
        price: float,
    ):
        today = date.today()

        # 🔹 period calculation
        if billing_cycle == RefmBillingCycleConstants.MONTHLY:
            period_start = today
            period_end = today + timedelta(days=30)

        elif billing_cycle == RefmBillingCycleConstants.ANNUAL:
            period_start = today
            period_end = today + timedelta(days=365)

        else:
            raise ValidationErrorDetail(
                code=ErrorCodes.VALIDATION_ERROR,
                message="Invalid billing cycle"
            )

        # 🔹 generate invoice number (simple for now)
        invoice_number = f"CD-{today.year}-{self._generate_invoice_number()}"

        await self.billing_invoice_repo.create(
            session=self.session,
            data={
                "chamber_id": self.chamber_id,
                "subscription_id": subscription.subscription_id,
                "invoice_number": invoice_number,
                "period_start": period_start,
                "period_end": period_end,
                "amount": price,
                "currency_code": subscription.currency_code,
                "status_code": RefmInvoiceStatusConstants.PENDING,
            }
        )

    async def _update_chamber_subscription_snapshot(self, sub):
        await self.chamber_repo.update(
            session=self.session,
            id_values=self.chamber_id,
            data={
                "plan_code": sub.plan_code,
                "subscription_start": sub.start_date,
                "subscription_end": sub.next_renewal_date,
            }
        )

    # -------------------------------------------------------
    # GET CURRENT SUBSCRIPTION
    # -------------------------------------------------------

    async def get_subscription_stats(self) -> SubscriptionStats:

        row = await self.chamber_subscription_repo.get_subscription_stats(
            self.session,
            self.chamber_id
        )

        if not row:
            raise ValidationErrorDetail(
                code=ErrorCodes.NOT_FOUND,
                message="No Subscription"
            )

        return SubscriptionStats(
            plan_code=row.plan_code,
            plan_name=row.plan_name,
            users_used=row.users_used or 0,
            users_allowed=row.max_users,
            cases_used=row.cases_used or 0,
            cases_allowed=row.max_cases,
            next_renewal_date=row.next_renewal_date,
            next_amount=row.price_amt,
        )

    async def get_current_subscription(self) -> ChamberSubscriptionOut:

        row = await self.chamber_subscription_repo.get_active_subscription(
            session=self.session,
            chamber_id=self.chamber_id
        )        

        if not row:
            raise ValidationErrorDetail(
                code=ErrorCodes.NOT_FOUND,
                message="No Subscription"
            )

        sub, plan_name, max_users, max_cases = row

        return self._to_out(sub, plan_name, max_users, max_cases)

    # -------------------------------------------------------
    # GET ALL PLANS
    # -------------------------------------------------------
    async def get_plans(self):

        rows = await self.chamber_subscription_repo.list_plans(self.session)

        return [
            SubscriptionPlanItem(
                code=r.code,
                description=r.description,
                email_ind=r.email_ind,
                sms_ind=r.sms_ind,
                whatsapp_ind=r.whatsapp_ind,
                max_users=r.max_users,
                max_cases=r.max_cases,
                price_monthly_amt=r.price_monthly_amt,
                price_annual_amt=r.price_annual_amt,
            )
            for r in rows
        ]
    
    async def get_usage(self) -> UsageStats:

        row = await self.chamber_subscription_repo.get_usage_stats(
            self.session,
            self.chamber_id
        )

        if not row:
            raise ValidationErrorDetail(
                code=ErrorCodes.NOT_FOUND,
                message="Usage not found"
            )

        return UsageStats(
            users_used=row.users_used or 0,
            users_allowed=row.max_users,
            cases_used=row.cases_used or 0,
            cases_allowed=row.max_cases,
        )
    
    async def get_billing_history(
        self,
        page: int,
        limit: int,
        status: Optional[str],
    ):

        rows, total = await self.billing_invoice_repo.list_invoices(
            session=self.session,
            chamber_id=self.chamber_id,
            page=page,
            limit=limit,
            status=status,
        )

        records = []

        for r in rows:
            # 🧠 period label (UI friendly)
            period_label = r["period_start"].strftime("%b %Y")
            print(f"*************************** Invoide date :: {r["invoice_date"]}")

            records.append(
                BillingInvoiceItem(
                    invoice_id=r["invoice_id"],
                    invoice_number=r["invoice_number"],
                    period_label=period_label,
                    amount=r["amount"],
                    status_code=r["status_code"],
                    status_label=r["status_label"],
                    invoice_date=r["invoice_date"],
                )
            )

        return PagingBuilder(
            total_records=total,
            page=page,
            limit=limit
        ).build(records=records)
    
    async def create_free_subscription(
        self,
        chamber_id: str,
    ):

        today = date.today()

        await self.chamber_subscription_repo.create(
            session=self.session,
            data={
                "chamber_id": chamber_id,
                "plan_code": RefmPlanTypesConstants.FREE,
                "billing_cycle": RefmBillingCycleConstants.ANNUAL,
                "start_date": today,
                "status_code": RefmSubscriptionStatusConstants.ACTIVE,
                "price_amt": 0.00,
                "currency_code": RefmCurrencyConstants.INDIAN_RUPEE,
            }
        )

    # -------------------------------------------------------
    # CHANGE PLAN (UPGRADE / DOWNGRADE)
    # -------------------------------------------------------
    async def change_plan(self, payload: ChangePlanIn):

        if self.userDetails.role and self.userDetails.role.role_code == SUPERADMIN_ROLE_CODE:
            raise ValidationErrorDetail(
                code=ErrorCodes.VALIDATION_ERROR,
                message="Default System Chamber subscription cannot be modified"
            )

        # 🔹 validate plan using REFM resolver
        plan_map = await self.refm_resolver.get_refm_map(
            column_attr=ChamberSubscriptions.plan_code
        )

        plan = plan_map.get(payload.plan_code)

        if not plan:
            raise ValidationErrorDetail(
                code=ErrorCodes.NOT_FOUND,
                message="Invalid plan"
            )

        today = date.today()

        # 🔹 validate billing cycle + compute pricing
        if payload.billing_cycle == RefmBillingCycleConstants.MONTHLY:
            price = plan.get("price_monthly_amt")
            next_renewal = today + timedelta(days=30)

        elif payload.billing_cycle == RefmBillingCycleConstants.ANNUAL:
            price = plan.get("price_annual_amt")
            next_renewal = today + timedelta(days=365)

        else:
            raise ValidationErrorDetail(
                code=ErrorCodes.VALIDATION_ERROR,
                message="Invalid billing cycle"
            )

        # 🔹 get existing active subscription (always exists)
        existing = await self.chamber_subscription_repo.get_active_subscription(
            self.session,
            self.chamber_id
        )

        if not existing:
            raise ValidationErrorDetail(
                code=ErrorCodes.NOT_FOUND,
                message="Subscription not found"
            )

        sub, *_ = existing

        # 🔥 IMPORTANT OPTIMIZATION
        # avoid unnecessary change
        if (
            sub.plan_code == payload.plan_code
            and sub.billing_cycle == payload.billing_cycle
        ):
            return await self.get_current_subscription()

        # 🔹 deactivate existing
        await self.chamber_subscription_repo.update(
            session=self.session,
            id_values=sub.subscription_id,
            data={
                "status_code": RefmSubscriptionStatusConstants.CANCELLED,
                "updated_by": self.user_id
            }
        )

        # 🔹 create new subscription
        new_sub = await self.chamber_subscription_repo.create(
            session=self.session,
            data={
                "chamber_id": self.chamber_id,
                "plan_code": payload.plan_code,
                "billing_cycle": payload.billing_cycle,
                "start_date": today,
                "next_renewal_date": next_renewal,
                "status_code": RefmSubscriptionStatusConstants.ACTIVE,
                "price_amt": price,
                "currency_code": plan.get("currency_code"),
                "created_by": self.user_id
            }
        )

        # 🔥 UPDATE CHAMBER SNAPSHOT
        await self._update_chamber_subscription_snapshot(new_sub)

        if payload.plan_code != RefmPlanTypesConstants.FREE:
            await self._create_invoice_for_subscription(
                subscription=new_sub,
                billing_cycle=payload.billing_cycle,
                price=price
            )

        return await self.get_current_subscription()
    
    async def cancel_subscription(self) -> ChamberSubscriptionOut:

        if self.userDetails.role and self.userDetails.role.role_code == SUPERADMIN_ROLE_CODE:
            raise ValidationErrorDetail(
                code=ErrorCodes.VALIDATION_ERROR,
                message="System subscription cannot be modified"
            )

        existing = await self.chamber_subscription_repo.get_active_subscription(
            self.session,
            self.chamber_id
        )

        if not existing:
            raise ValidationErrorDetail(
                code=ErrorCodes.NOT_FOUND,
                message="Subscription not found"
            )

        sub, *_ = existing

        # 🔥 Already free? do nothing
        if sub.plan_code == RefmPlanTypesConstants.FREE:
            return await self.get_current_subscription()

        today = date.today()

        # 🔹 cancel current
        await self.chamber_subscription_repo.update(
            session=self.session,
            id_values=sub.subscription_id,
            data={
                "status_code": RefmSubscriptionStatusConstants.CANCELLED,
            }
        )

        # 🔹 fallback to FREE (very important)
        free_plan = RefmPlanTypesConstants.FREE

        new_sub = await self.chamber_subscription_repo.create(
            session=self.session,
            data={
                "chamber_id": self.chamber_id,
                "plan_code": free_plan,
                "billing_cycle": RefmBillingCycleConstants.MONTHLY,
                "start_date": today,
                "status_code": RefmSubscriptionStatusConstants.ACTIVE,
                "price_amt": 0.00,
                "currency_code": RefmCurrencyConstants.INDIAN_RUPEE,
            }
        )

        # 🔥 UPDATE CHAMBER SNAPSHOT
        await self._update_chamber_subscription_snapshot(new_sub)

        return await self.get_current_subscription()