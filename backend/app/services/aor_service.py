"""aor_service.py — Business logic for Case AOR (Advocate on Record) module"""

from datetime import date
from typing import List, Optional

from sqlalchemy import and_, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.models.case_aors import CaseAors
from app.database.models.cases import Cases
from app.database.models.refm_aor_status import RefmAorStatus, RefmAorStatusConstants
from app.database.models.user_chamber_link import UserChamberLink
from app.database.models.users import Users
from app.database.repositories.case_aors_repository import CaseAorsRepository
from app.database.repositories.cases_repository import CasesRepository
from app.dtos.aor_dto import AorCreate, AorEdit, AorOut, AorWithdraw
from app.services.base.secured_base_service import BaseSecuredService
from app.validators import ErrorCodes, ValidationErrorDetail


def _full_name(first: Optional[str], last: Optional[str]) -> str:
    return " ".join(p for p in [first, last] if p) or ""


class AorService(BaseSecuredService):
    def __init__(
        self,
        session: AsyncSession,
        aors_repo: Optional[CaseAorsRepository] = None,
        cases_repo: Optional[CasesRepository] = None,
    ):
        super().__init__(session)
        self.aors_repo = aors_repo or CaseAorsRepository()
        self.cases_repo = cases_repo or CasesRepository()

    # ─────────────────────────────────────────────────────────────────────
    # HELPERS
    # ─────────────────────────────────────────────────────────────────────

    async def _get_case_details(self, case_id: str) -> Cases:
        stmt = select(Cases).where(Cases.case_id == case_id)

        stmt = self.cases_repo.apply_case_visibility(stmt)

        case = await self.session.scalar(stmt)

        if not case:
            raise ValidationErrorDetail(
                code=ErrorCodes.NOT_FOUND,
                message="Case not found or access denied",
            )

        return case

    async def _get_aor_or_404(self, case_aor_id: str) -> CaseAors:
        aor = await self.aors_repo.get_by_id(
            session=self.session,
            filters={CaseAors.case_aor_id: case_aor_id, CaseAors.chamber_id: self.chamber_id},
        )
        if not aor:
            raise ValidationErrorDetail(code=ErrorCodes.NOT_FOUND, message="AOR record not found")
        return aor

    async def _user_name(self, user_id: str) -> str:
        u = await self.session.get(Users, user_id)
        return _full_name(u.first_name, u.last_name) if u else ""

    async def _to_out(self, aor: CaseAors, advocate_name: str) -> AorOut:
        return AorOut(
            case_aor_id=aor.case_aor_id,
            case_id=aor.case_id,
            user_id=aor.user_id,
            advocate_name=advocate_name,
            primary_ind=bool(aor.primary_ind),
            status_code=aor.status_code or RefmAorStatusConstants.ACTIVE,
            status_description= await self.refm_resolver.from_column(
                column_attr=CaseAors.status_code,
                value_column=RefmAorStatus.description,
                code=aor.status_code,
                default=None
            ),
            appointment_date=aor.appointment_date,
            withdrawal_date=aor.withdrawal_date,
            notes=aor.notes,
            created_date=aor.created_date,
        )
    
    async def _assign_new_primary(self, case_id: str):
        next_aor = await self.session.scalar(
            select(CaseAors)
            .where(
                CaseAors.case_id == case_id,
                CaseAors.chamber_id == self.chamber_id,
                CaseAors.status_code == RefmAorStatusConstants.ACTIVE,
            )
            .order_by(CaseAors.appointment_date.asc())
            .limit(1)
        )

        if next_aor:
            next_aor.primary_ind = True
            await self.session.flush()

    # ─────────────────────────────────────────────────────────────────────
    # LIST
    # ─────────────────────────────────────────────────────────────────────

    async def aors_get_by_case(self, case_id: str) -> List[AorOut]:
        await self._get_case_details(case_id)
        aors = await self.aors_repo.list_all(
            session=self.session,
            where=[
                CaseAors.case_id == case_id,
                CaseAors.chamber_id == self.chamber_id,
            ],
            order_by=[CaseAors.primary_ind.desc(), CaseAors.appointment_date.asc()],
        )
        # Batch-load user names
        user_ids = list({a.user_id for a in aors})
        name_map: dict = {}
        if user_ids:
            rows = await self.session.execute(
                select(Users.user_id, Users.first_name, Users.last_name)
                .where(Users.user_id.in_(user_ids))
            )
            name_map = {r.user_id: _full_name(r.first_name, r.last_name) for r in rows}

        return [await self._to_out(a, name_map.get(a.user_id, "")) for a in aors]

    # ─────────────────────────────────────────────────────────────────────
    # ADD
    # ─────────────────────────────────────────────────────────────────────

    async def aors_add(self, payload: AorCreate) -> AorOut:
        await self._get_case_details(payload.case_id)

        # Verify user is an active member of this chamber
        link = await self.session.execute(
            select(UserChamberLink).where(
                and_(
                    UserChamberLink.user_id == payload.user_id,
                    UserChamberLink.chamber_id == self.chamber_id,
                    UserChamberLink.left_date.is_(None),
                    UserChamberLink.status_ind.is_(True),
                )
            )
        )
        if not link.scalars().first():
            raise ValidationErrorDetail(
                code=ErrorCodes.VALIDATION_ERROR,
                message="User is not an active member of this chamber",
            )

        # Prevent duplicate active AOR for same user on same case
        existing = await self.aors_repo.get_first(
            session=self.session,
            filters={
                CaseAors.case_id: payload.case_id,
                CaseAors.user_id: payload.user_id,
                CaseAors.status_code: RefmAorStatusConstants.ACTIVE,
            },
        )
        if existing:
            raise ValidationErrorDetail(
                code=ErrorCodes.VALIDATION_ERROR,
                message="This advocate is already an active AOR on this case",
            )

        # If new AOR is primary, demote any existing primary
        if payload.primary_ind:
            await self._demote_existing_primary(payload.case_id)

        data = {
            "case_id": payload.case_id,
            "user_id": payload.user_id,
            "chamber_id": self.chamber_id,
            "primary_ind": payload.primary_ind,
            "appointment_date": payload.appointment_date or date.today(),
            "status_code": "AC",
            "notes": payload.notes,
            "created_by": self.user_id,
        }
        aor = await self.aors_repo.create(
            session=self.session,
            data=self.aors_repo.map_fields_to_db_column(data),
        )
        return await self._to_out(aor, await self._user_name(aor.user_id))

    # ─────────────────────────────────────────────────────────────────────
    # EDIT (set primary, change status)
    # ─────────────────────────────────────────────────────────────────────

    async def aors_edit(self, payload: AorEdit) -> AorOut:
        aor = await self._get_aor_or_404(payload.case_aor_id)

        if payload.primary_ind is True and not aor.primary_ind:
            await self._demote_existing_primary(aor.case_id)

        data = payload.model_dump(exclude_unset=True, exclude_none=True)

        data.pop("case_aor_id", None)
        data.pop("status_code", None)
        data.pop("withdrawal_date", None)

        if data:
            aor = await self.aors_repo.update(
                session=self.session,
                id_values=payload.case_aor_id,
                data=self.aors_repo.map_fields_to_db_column(data),
            )
        return await self._to_out(aor, await self._user_name(aor.user_id))

    # ─────────────────────────────────────────────────────────────────────
    # WITHDRAW
    # ─────────────────────────────────────────────────────────────────────

    async def aors_withdraw(self, payload: AorWithdraw) -> AorOut:
        aor = await self._get_aor_or_404(payload.case_aor_id)
        if aor.status_code != RefmAorStatusConstants.ACTIVE:
            raise ValidationErrorDetail(
                code=ErrorCodes.VALIDATION_ERROR,
                message=f"AOR is already '{aor.status_code}', cannot withdraw",
            )
        
        if aor.primary_ind:
            await self._assign_new_primary(aor.case_id)

        updated = await self.aors_repo.update(
            session=self.session,
            id_values=payload.case_aor_id,
            data={
                "status_code": RefmAorStatusConstants.WITHDRAWN,
                "withdrawal_date": payload.withdrawal_date or date.today(),
                "primary_ind": False,
                "notes": payload.notes or aor.notes,
            },
        )
        return await self._to_out(updated, await self._user_name(updated.user_id))

    # ─────────────────────────────────────────────────────────────────────
    # REMOVE
    # ─────────────────────────────────────────────────────────────────────

    async def aors_remove(self, case_aor_id: str) -> dict:
        await self._get_aor_or_404(case_aor_id)
        await self.aors_repo.delete(session=self.session, id_values=case_aor_id, soft=False)
        return {"case_aor_id": case_aor_id, "deleted": True}

    # ─────────────────────────────────────────────────────────────────────
    # PRIVATE
    # ─────────────────────────────────────────────────────────────────────

    async def _demote_existing_primary(self, case_id: str) -> None:
        """Set primary_ind=False on any currently-primary AOR for this case."""
        existing_primary = await self.session.execute(
            select(CaseAors).where(
                CaseAors.case_id == case_id,
                CaseAors.chamber_id == self.chamber_id,
                CaseAors.primary_ind.is_(True),
                CaseAors.status_code == RefmAorStatusConstants.ACTIVE,
            )
        )
        await self.session.execute(
            update(CaseAors)
            .where(
                CaseAors.case_id == case_id,
                CaseAors.chamber_id == self.chamber_id,
                CaseAors.primary_ind.is_(True),
                CaseAors.status_code == RefmAorStatusConstants.ACTIVE,
            )
            .values(primary_ind=False)
        )
        await self.session.flush()
