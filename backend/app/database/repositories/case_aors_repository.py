
from typing import Optional

from sqlalchemy import func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import aliased

from app.database.models.profile_images import ProfileImages
from app.database.models.users import Users
from app.database.repositories.base.repo_context import apply_repo_context
from app.database.repositories.base.base_repository import BaseRepository
from app.database.models.case_aors import CaseAors

@apply_repo_context
class CaseAorsRepository(BaseRepository[CaseAors]):
    def __init__(self):
        super().__init__(CaseAors)

    async def aors_get_by_chamber(
            self,
            session: AsyncSession,
            chamber_id: str,
            search: Optional[str],
        ):

        # correlated subquery: latest appointment_date per user
        ca2 = aliased(CaseAors)
        latest_appt = (
            select(func.max(ca2.appointment_date))
            .where(ca2.user_id == Users.user_id)
            .correlate(Users)
            .scalar_subquery()
        )

        stmt = (
            select(
                Users.user_id,
                Users.first_name,
                Users.last_name,
                Users.email,
                Users.phone,
                CaseAors.case_aor_id,
                CaseAors.case_id,
                CaseAors.status_code,
                CaseAors.notes,
                CaseAors.withdrawal_date,
                CaseAors.created_date,
                CaseAors.primary_ind,
                CaseAors.appointment_date,
                ProfileImages.image_id,
                ProfileImages.image_data,
            )
            .join(CaseAors, CaseAors.user_id == Users.user_id)
            .outerjoin(ProfileImages, Users.user_id == ProfileImages.user_id)
            .where(
                Users.deleted_ind.is_(False),
                CaseAors.appointment_date == latest_appt,
                CaseAors.chamber_id == chamber_id,
            )
        )

        if search and search.strip():
            kw = f"%{search.strip()}%"
            stmt = stmt.where(
                or_(
                    Users.first_name.ilike(kw),
                    Users.last_name.ilike(kw),
                    Users.email.ilike(kw),
                    Users.phone.ilike(kw),
                )
            )

        stmt = stmt.order_by(
            CaseAors.primary_ind.desc(),
            CaseAors.appointment_date.asc(),
        )

        rows = (await self.execute(session=session, stmt=stmt)).all()
        return rows


