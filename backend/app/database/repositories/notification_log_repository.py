# app/database/repositories/notification_repository.py


from sqlalchemy import select

from app.database.models.notification_log import NotificationLog
from app.database.models.users import Users
from app.database.models.notification_settings import NotificationSettings
from app.database.models.user_chamber_link import UserChamberLink
from app.database.models.user_roles import UserRoles
from app.database.models.chamber_roles import ChamberRoles
from app.database.models.cases import Cases
from app.database.models.hearings import Hearings
from app.database.models.courts import Courts
from app.database.models.case_aors import CaseAors
from app.database.models.refm_hearing_purpose import RefmHearingPurpose
from app.database.models.refm_hearing_status import RefmHearingStatus

from app.database.repositories.base.repo_context import apply_repo_context
from app.database.repositories.base.base_repository import BaseRepository


_HEARING_COLS = [
    Cases.case_id,
    Cases.case_number,
    Cases.petitioner,
    Cases.respondent,
    Hearings.hearing_id,
    Hearings.hearing_date,
    Hearings.purpose_code,
    Hearings.status_code,
    Hearings.next_hearing_date,
    Hearings.notes,
    Courts.court_name,
    Users.email,
]


@apply_repo_context
class NotificationRepository(BaseRepository):

    def __init__(self):
        super().__init__(NotificationLog)    

    def __hearings_select_stmt(self):
        return (select(*_HEARING_COLS)
            .join(Hearings, Hearings.case_id == Cases.case_id)
            .join(Courts, Courts.court_code == Cases.court_code)
            .join(CaseAors, CaseAors.case_id == Cases.case_id)
            .join(Users, Users.user_id == CaseAors.user_id))

    # =====================================================
    # 🔹 LOG (DEDUP)
    # =====================================================
    async def create_log(self, session, data: dict):
        return await self.create(session=session, data=data)

    # =====================================================
    # 🔹 USERS
    # =====================================================
    async def get_users_settings(self, session):
        stmt = (
            select(
                Users.user_id,
                Users.email,
                NotificationSettings.email_enabled_ind,
                NotificationSettings.email_summary_frequency_code,
                NotificationSettings.email_remind_before,
                ChamberRoles.role_code,
            )
            .join(NotificationSettings, NotificationSettings.user_id == Users.user_id)
            .join(UserChamberLink, UserChamberLink.user_id == Users.user_id)
            .join(UserRoles, UserRoles.link_id == UserChamberLink.link_id)
            .join(ChamberRoles, ChamberRoles.role_id == UserRoles.role_id)
            .where(
                UserRoles.end_date.is_(None),
                UserChamberLink.left_date.is_(None),
                UserChamberLink.status_ind.is_(True),
            )
        )

        result = await self.execute(session=session, stmt=stmt)
        return result.all()

    # =====================================================
    # 🔹 HEARINGS
    # =====================================================
    async def get_hearings_range(self, session, start, end):
        stmt = (
            self.__hearings_select_stmt()
            .where(
                Hearings.hearing_date.between(start, end),
            )
        )
        result = await self.execute(session=session, stmt=stmt)
        return result.all()

    async def get_hearings_for_reminder(self, session, target_time):
        stmt = (
            self.__hearings_select_stmt()
            .where(
                Hearings.hearing_date == target_time.date(),
            )
        )
        result = await self.execute(session=session, stmt=stmt)
        return result.all()

    # =====================================================
    # 🔹 REFM
    # =====================================================
    async def get_refm_maps(self, session):
        purpose = await self.execute(
            session= session,
            stmt=select(RefmHearingPurpose.code, RefmHearingPurpose.description)
        )
        status = await self.execute(
            session= session,
            stmt=select(RefmHearingStatus.code, RefmHearingStatus.description)
        )

        return (
            {r.code: r.description for r in purpose},
            {r.code: r.description for r in status},
        )