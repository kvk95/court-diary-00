"""aor_service.py — Business logic for Case AOR (Advocate on Record) module"""

from datetime import date
from typing import List, Optional

from sqlalchemy import and_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.models.case_aors import CaseAors
from app.database.models.refm_aor_status import RefmAorStatus, RefmAorStatusConstants
from app.database.models.user_chamber_link import UserChamberLink
from app.database.models.users import Users
from app.database.repositories.case_aors_repository import CaseAorsRepository
from app.database.repositories.cases_repository import CasesRepository
from app.database.repositories.profile_images_repository import ProfileImagesRepository
from app.database.repositories.user_chamber_link_repository import UserChamberLinkRepository
from app.database.repositories.users_repository import UsersRepository
from app.dtos.aor_dto import AorCreate, AorEdit, AorOut, AorWithdraw
from app.dtos.users_dto import UserBasicInfoOut
from app.services.base.secured_base_service import BaseSecuredService
from app.validators import ErrorCodes, ValidationErrorDetail


class AorService(BaseSecuredService):
    def __init__(
        self,
        session: AsyncSession,
        aors_repo: Optional[CaseAorsRepository] = None,
        cases_repo: Optional[CasesRepository] = None,
        users_repo: Optional[UsersRepository] = None,
        users_chamer_repo: Optional[UserChamberLinkRepository] = None,
        profile_images_repo: Optional[ProfileImagesRepository] = None,
    ):
        super().__init__(session)
        self.aors_repo = aors_repo or CaseAorsRepository()
        self.cases_repo = cases_repo or CasesRepository()
        self.users_repo = users_repo or UsersRepository()
        self.users_chamer_repo = users_chamer_repo or UserChamberLinkRepository()
        self.profile_images_repo = profile_images_repo or ProfileImagesRepository()


    # ─────────────────────────────────────────────────────────────────────
    # HELPERS
    # ─────────────────────────────────────────────────────────────────────

    async def _get_aor_case_detail(self, case_aor_id: str) -> CaseAors:
        aor = await self.aors_repo.get_by_id(
            session=self.session,
            filters={CaseAors.case_aor_id: case_aor_id, CaseAors.chamber_id: self.chamber_id},
        )
        if not aor:
            raise ValidationErrorDetail(code=ErrorCodes.NOT_FOUND, message="AOR record not found")
        return aor

    async def _user_name(self, user_id: str) -> str:
        user = await self.users_repo.get_by_id(
            session=self.session,
            id_values=user_id
        )
        if not user:
            raise ValidationErrorDetail(code=ErrorCodes.NOT_FOUND, message="user not found")
        return self.full_name(user.first_name, user.last_name) if user else ""

    async def _to_out(self, aor, advocate_name, img) -> AorOut:

        return AorOut(
            case_aor_id=aor.case_aor_id,
            chamber_id=self.chamber_id,
            case_id=aor.case_id,
            user_id=aor.user_id,
            advocate_name=advocate_name,
            image_id='', #img["image_id"] if img else None,
            image_data='', #img["image_data"] if img else None,
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
        next_aor = await self.aors_repo.get_first(
            session=self.session,
            where = (
                CaseAors.case_id == case_id,
                CaseAors.chamber_id == self.chamber_id,
                CaseAors.status_code == RefmAorStatusConstants.ACTIVE,
            ),
            order_by=[CaseAors.appointment_date.asc()],
        )

        if next_aor:
            next_aor.primary_ind = True

    # ─────────────────────────────────────────────────────────────────────
    # LIST
    # ─────────────────────────────────────────────────────────────────────

    async def aors_get_by_case(self, case_id: str) -> List[AorOut]:
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
            rows = await self.aors_repo.execute( session=self.session, stmt=
                select(Users.user_id, Users.first_name, Users.last_name,)
                .where(Users.user_id.in_(user_ids))
            )
            name_map = {r.user_id: self.full_name(r.first_name, r.last_name) for r in rows}

        user_ids = list({a.user_id for a in aors})

        image_map = await self.profile_images_repo.get_images_by_user_ids(
            session=self.session,
            user_ids=user_ids,
        )

        return [
            await self._to_out(
                a,
                name_map.get(a.user_id, ""),
                image_map.get(a.user_id, ""),
            )
            for a in aors
        ]
    
    async def aors_get_by_chamber(self,search: Optional[str]) -> List[UserBasicInfoOut]:
        rows = await self.aors_repo.aors_get_by_chamber(session=self.session,
                                                        search=search)

        user_ids = [c.user_id for c in rows]

        image_map = await self.profile_images_repo.get_images_by_user_ids(
            session=self.session,
            user_ids=user_ids,
        )
        return [
            UserBasicInfoOut(

                user_id=row.user_id,
                full_name=self.full_name(row.first_name,row.last_name),
                first_name=row.first_name,
                last_name=row.last_name,
                email=row.email,
                phone=row.phone,
                advocate_ind=row.advocate_ind,
                active_ind=row.status_ind,
                image_id=image_map.get(row.user_id, {}).get("image_id"),
                image_data=image_map.get(row.user_id, {}).get("image_data"),
            )
            for row in rows
        ]

    # ─────────────────────────────────────────────────────────────────────
    # ADD
    # ─────────────────────────────────────────────────────────────────────

    async def aors_add(self, payload: AorCreate) -> AorOut:

        # Verify user is an active member of this chamber
        link = await self.users_chamer_repo.get_first(
            session=self.session,
            where=[
                and_(
                    UserChamberLink.user_id == payload.user_id,
                    UserChamberLink.chamber_id == self.chamber_id,
                    UserChamberLink.left_date.is_(None),
                    UserChamberLink.status_ind.is_(True),
                )
            ],
        )
        if not link:
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
            "status_code": RefmAorStatusConstants.ACTIVE,
            "notes": payload.notes,
            "created_by": self.user_id,
        }
        aor = await self.aors_repo.create(
            session=self.session,
            data=self.aors_repo.map_fields_to_db_column(data),
        )        

        image_map = await self.profile_images_repo.get_images_by_user_ids(
            session=self.session,
            user_ids=[aor.user_id],
        )
        return await self._to_out(aor, await self._user_name(aor.user_id), image_map)

    # ─────────────────────────────────────────────────────────────────────
    # EDIT (set primary, change status)
    # ─────────────────────────────────────────────────────────────────────

    async def aors_edit(self, payload: AorEdit) -> AorOut:
        aor = await self._get_aor_case_detail(payload.case_aor_id)

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

        image_map = await self.profile_images_repo.get_images_by_user_ids(
            session=self.session,
            user_ids=[aor.user_id],
        )
        return await self._to_out(aor, await self._user_name(aor.user_id), image_map)

    # ─────────────────────────────────────────────────────────────────────
    # WITHDRAW
    # ─────────────────────────────────────────────────────────────────────

    async def aors_withdraw(self, payload: AorWithdraw) -> AorOut:
        aor = await self._get_aor_case_detail(payload.case_aor_id)
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

        image_map = await self.profile_images_repo.get_images_by_user_ids(
            session=self.session,
            user_ids=[updated.user_id],
        )
        return await self._to_out(aor, await self._user_name(updated.user_id), image_map)

    # ─────────────────────────────────────────────────────────────────────
    # REMOVE
    # ─────────────────────────────────────────────────────────────────────

    async def aors_remove(self, case_aor_id: str) -> dict:
        await self._get_aor_case_detail(case_aor_id)
        await self.aors_repo.delete(session=self.session, id_values=case_aor_id, soft=False)
        return {"case_aor_id": case_aor_id, "deleted": True}

    # ─────────────────────────────────────────────────────────────────────
    # PRIVATE
    # ─────────────────────────────────────────────────────────────────────

    async def _demote_existing_primary(self, case_id: str) -> None:
        """Set primary_ind=False on any currently-primary AOR for this case."""
        existing_primary = await self.aors_repo.list_all(
            session=self.session,
            where = (
                CaseAors.case_id == case_id,
                CaseAors.chamber_id == self.chamber_id,
                CaseAors.primary_ind.is_(True),
                CaseAors.status_code == RefmAorStatusConstants.ACTIVE,
            )
        )
        
        await self.aors_repo.bulk_update(
            session=self.session,
            where=[
                CaseAors.case_id == case_id,
                CaseAors.chamber_id == self.chamber_id,
                CaseAors.primary_ind.is_(True),
                CaseAors.status_code == RefmAorStatusConstants.ACTIVE,
            ],
            data={
                "primary_ind":False,
            },
        )
