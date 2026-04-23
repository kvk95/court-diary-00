# app/services/notification_settings_service.py

from typing import Optional

from sqlalchemy.ext.asyncio import AsyncSession

from app.database.models.notification_settings import NotificationSettings
from app.database.models.refm_email_summary_frequency import RefmEmailSummaryFrequencyConstants, RefmEmailSummaryFrequencyEnum
from app.dtos.notification_settings_dto import (
    NotificationSettingsOut,
    NotificationSettingsEdit
)
from app.database.repositories.notification_settings_repository import NotificationSettingsRepository
from app.services.base.secured_base_service import BaseSecuredService
from app.validators import (
    ErrorCodes,
    ValidationErrorDetail,
    aggregate_errors,
)
from app.validators.field_validations import FieldValidator


class NotificationSettingsService(BaseSecuredService):

    def __init__(
        self,
        session: AsyncSession,
        notification_repo: Optional[NotificationSettingsRepository] = None
    ):
        super().__init__(session)
        self.notification_repo = notification_repo or NotificationSettingsRepository()

    async def _get_by_id(self):
        row = await self.notification_repo.get_by_id(
                session=self.session,
                filters={NotificationSettings.user_id: self.user_id},
            )
            
        return row

    def _to_notification_out(self, row):
        return NotificationSettingsOut(
            email_enabled_ind=row.email_enabled_ind,
            sms_enabled_ind=row.sms_enabled_ind,
            whatsapp_enabled_ind=row.whatsapp_enabled_ind,
            email_summary_frequency_code=row.email_summary_frequency_code,
            sms_summary_frequency_code=row.sms_summary_frequency_code,
            whatsapp_summary_frequency_code=row.whatsapp_summary_frequency_code,
            email_remind_before=row.email_remind_before or 30,
            sms_remind_before=row.sms_remind_before or 30,
            whatsapp_remind_before=row.whatsapp_remind_before or 30,
        )

    # -------------------------------------------------------
    # GET
    # -------------------------------------------------------
    async def get_settings(self) -> NotificationSettingsOut:
        
        row = await self._get_by_id()

        if not row:
            # 🔥 auto-create
            row = await self.notification_repo.create(
                session=self.session,
                data={
                    "user_id": self.user_id,
                    "created_by": self.user_id
                }
            )

        return self._to_notification_out(row)

    # -------------------------------------------------------
    # UPDATE
    # -------------------------------------------------------
    async def update_settings(self, payload: NotificationSettingsEdit) -> NotificationSettingsOut:

        row = await self._get_by_id()

        if not row:
            raise ValidationErrorDetail(
                code=ErrorCodes.NOT_FOUND,
                message="Notification settings not found"
            )

        errors = []

        # ---------------------------------------------------
        # 🔹 ENUM VALIDATION (centralized)
        # ---------------------------------------------------
        email_freq = FieldValidator.validate_enum(
            RefmEmailSummaryFrequencyEnum,
            payload.email_summary_frequency_code,
            "email_summary_frequency_code",
            errors
        )

        sms_freq = FieldValidator.validate_enum(
            RefmEmailSummaryFrequencyEnum,
            payload.sms_summary_frequency_code,
            "sms_summary_frequency_code",
            errors
        )

        whatsapp_freq = FieldValidator.validate_enum(
            RefmEmailSummaryFrequencyEnum,
            payload.whatsapp_summary_frequency_code,
            "whatsapp_summary_frequency_code",
            errors
        )

        # ---------------------------------------------------
        # 🔹 REMINDER VALIDATION
        # ---------------------------------------------------
        def validate_reminder(value, field):
            if value is None:
                return
            if value < 0 or value > 1440:
                errors.append(
                    ValidationErrorDetail(
                        code=ErrorCodes.VALIDATION_ERROR,
                        message=f"{field} must be between 0 and 1440 minutes"
                    )
                )

        validate_reminder(payload.email_remind_before, "email_remind_before")
        validate_reminder(payload.sms_remind_before, "sms_remind_before")
        validate_reminder(payload.whatsapp_remind_before, "whatsapp_remind_before")

        if errors:
            aggregate_errors(errors)

        # ---------------------------------------------------
        # 🔥 BUILD DATA (your approach)
        # ---------------------------------------------------
        data = payload.model_dump(exclude_unset=True, exclude_none=True)

        # ---------------------------------------------------
        # 🔥 BUSINESS RULES
        # ---------------------------------------------------

        # 👉 Channel OFF → summary NONE
        if payload.email_enabled_ind is False:
            data["email_summary_frequency_code"] = RefmEmailSummaryFrequencyConstants.NONE

        if payload.sms_enabled_ind is False:
            data["sms_summary_frequency_code"] = RefmEmailSummaryFrequencyConstants.NONE

        if payload.whatsapp_enabled_ind is False:
            data["whatsapp_summary_frequency_code"] = RefmEmailSummaryFrequencyConstants.NONE

        # 👉 Summary NONE → remind_before = 0
        if email_freq == RefmEmailSummaryFrequencyEnum.NONE:
            data["email_remind_before"] = 0

        if sms_freq == RefmEmailSummaryFrequencyEnum.NONE:
            data["sms_remind_before"] = 0

        if whatsapp_freq == RefmEmailSummaryFrequencyEnum.NONE:
            data["whatsapp_remind_before"] = 0

        data["updated_by"] = self.user_id

        updated = await self.notification_repo.update(
            session=self.session,
            data=data,
            id_values=row.notification_id
        )

        return self._to_notification_out(updated)