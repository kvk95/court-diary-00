"""chamber_service.py — Business logic for the Chamber / Settings module"""

from sqlalchemy.ext.asyncio import AsyncSession

from app.database.models.chamber import Chamber
from app.database.models.refm_modules import RefmModulesConstants
from app.database.repositories.chamber_repository import ChamberRepository
from app.dtos.chamber_dto import ChamberEdit, ChamberOut
from app.services.base.secured_base_service import BaseSecuredService
from app.validators import aggregate_errors
from app.validators.error_codes import ErrorCodes
from app.validators.field_validations import FieldValidator
from app.validators.validation_errors import ValidationErrorDetail

class ChamberService(BaseSecuredService):
    """Service for reading and editing the authenticated user's chamber."""

    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session=session)
        self.chamber_repo = ChamberRepository()

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _assert_read_permission(self) -> None:
        """Raise 403 if the logged-in user lacks read rights on SETT."""
        user = self.userDetails
        # admin_ind bypasses module-level permission checks
        if user.role and user.role.admin_ind:
            return

        perm = next(
            (p for p in user.permissions if p.module_code == RefmModulesConstants.SETTINGS),
            None,
        )
        if not perm or not (perm.read_ind or perm.allow_all_ind):
            raise ValidationErrorDetail(
                code=ErrorCodes.PERMISSION_DENIED,
                message="You do not have permission to view Settings",
            )

    def _assert_write_permission(self) -> None:
        """Raise 403 if the logged-in user lacks write rights on SETT."""
        user = self.userDetails
        if user.role and user.role.admin_ind:
            return

        perm = next(
            (p for p in user.permissions if p.module_code == RefmModulesConstants.SETTINGS),
            None,
        )
        if not perm or not (perm.write_ind or perm.allow_all_ind):
            raise ValidationErrorDetail(
                code=ErrorCodes.PERMISSION_DENIED,
                message="You do not have permission to edit Settings",
            )

    async def _get_chamber(self) -> Chamber:
        """Fetch chamber scoped to the authenticated chamber_id."""
        chamber = await self.chamber_repo.get_by_id(
            session=self.session,
            filters={Chamber.chamber_id: self.chamber_id},
        )
        if not chamber:
            raise ValidationErrorDetail(
                code=ErrorCodes.NOT_FOUND,
                message="Chamber not found",
            )
        return chamber

    @staticmethod
    def _to_out(chamber: Chamber) -> ChamberOut:
        return ChamberOut(
            chamber_id=chamber.chamber_id,
            chamber_name=chamber.chamber_name,
            email=chamber.email,
            phone=chamber.phone,
            address_line1=chamber.address_line1,
            address_line2=chamber.address_line2,
            city=chamber.city,
            state_code=chamber.state_code,
            postal_code=chamber.postal_code,
            country_code=chamber.country_code,
            plan_code=chamber.plan_code,
            subscription_start=chamber.subscription_start,
            subscription_end=chamber.subscription_end,
            status_ind=chamber.status_ind,
            created_date=chamber.created_date,
            updated_date=chamber.updated_date,
        )

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    async def chamber_get_by_id(self) -> ChamberOut:
        """
        GET /settings/chamber/{chamber_id}

        Guards:
          - Requested chamber_id must match the session's chamber_id.
          - User must have SETT read permission.
        """

        # 2. Permission check
        self._assert_read_permission()

        # 3. Fetch & return
        chamber = await self._get_chamber()
        return self._to_out(chamber)

    async def chamber_edit(self, payload: ChamberEdit) -> ChamberOut:
        """
        PUT /settings/chamber/{chamber_id}/edit

        Guards:
          - Requested chamber_id must match the session's chamber_id.
          - User must have SETT write permission.

        Editable fields:
          chamber_name, email, phone,
          address_line1, address_line2, city, state_code, postal_code, country_code

        NOT editable here (managed by billing):
          plan_code, subscription_start, subscription_end, status_ind
        """

        # 2. Permission check
        self._assert_write_permission()

        # 3. Confirm chamber exists
        await self._get_chamber()

        # 4. Field-level validations
        errors = []

        if payload.email and (err := FieldValidator.validate_email(payload.email)):
            errors.append(err)

        if payload.phone and (err := FieldValidator.validate_phone(payload.phone)):
            errors.append(err)

        if payload.state_code and len(payload.state_code.strip()) != 2:
            errors.append(
                ValidationErrorDetail(
                    code=ErrorCodes.VALIDATION_ERROR,
                    message="state_code must be a 2-character code",
                )
            )

        if payload.country_code and len(payload.country_code.strip()) != 2:
            errors.append(
                ValidationErrorDetail(
                    code=ErrorCodes.VALIDATION_ERROR,
                    message="country_code must be a 2-character code",
                )
            )

        if errors:
            aggregate_errors(errors=errors)

        # 5. Build update dict — only fields explicitly supplied in the request
        data = payload.model_dump(exclude_unset=True, exclude_none=True)

        if not data:
            # Nothing to update; return current state
            chamber = await self._get_chamber()
            return self._to_out(chamber)

        # Stamp who last updated
        data["updated_by"] = self.user_id

        updated_chamber = await self.chamber_repo.update(
            session=self.session,
            filters={Chamber.chamber_id: self.chamber_id},
            data=self.chamber_repo.map_fields_to_db_column(data),
        )

        return self._to_out(updated_chamber)