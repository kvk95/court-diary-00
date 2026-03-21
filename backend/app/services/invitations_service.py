"""invitations_service.py — User invitation flow"""

from datetime import date, timedelta
from typing import Optional

from sqlalchemy import and_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.models.security_roles import SecurityRoles
from app.database.models.user_invitations import UserInvitations
from app.database.models.users import Users
from app.database.repositories.user_invitations_repository import UserInvitationsRepository
from app.dtos.base.paginated_out import PagingBuilder, PagingData
from app.dtos.invitations_dto import InvitationCreate, InvitationOut, InvitationRevoke
from app.database.models.refm_invitation_status import RefmInvitationStatusConstants
from app.services.base.secured_base_service import BaseSecuredService
from app.validators import ErrorCodes, ValidationErrorDetail


class InvitationsService(BaseSecuredService):
    def __init__(
        self,
        session: AsyncSession,
        invitations_repo: Optional[UserInvitationsRepository] = None,
    ):
        super().__init__(session)
        self.invitations_repo = invitations_repo or UserInvitationsRepository()

    async def _to_out(self, inv: UserInvitations) -> InvitationOut:
        role_name = None
        if inv.role_id:
            role = await self.session.get(SecurityRoles, inv.role_id)
            role_name = role.role_name if role else None
        invited_by_name = None
        if inv.invited_by:
            u = await self.session.get(Users, inv.invited_by)
            invited_by_name = f"{u.first_name} {u.last_name or ''}".strip() if u else None
        return InvitationOut(
            invitation_id=inv.invitation_id,
            email=inv.email,
            role_id=inv.role_id,
            role_name=role_name,
            status_code=inv.status_code,
            invited_date=inv.invited_date,
            expires_date=inv.expires_date,
            message=inv.message,
            invited_by_name=invited_by_name,
        )

    async def invitations_get_paged(
        self, page: int, limit: int, status: Optional[str] = None
    ) -> PagingData[InvitationOut]:
        conditions = [UserInvitations.chamber_id == self.chamber_id]
        if status:
            conditions.append(UserInvitations.status_code == status)
        invitations, total = await self.invitations_repo.list_paginated(
            session=self.session, page=page, limit=limit,
            where=conditions,
            order_by=[UserInvitations.invited_date.desc()],
        )
        records = [await self._to_out(i) for i in invitations]
        return PagingBuilder(total_records=total, page=page, limit=limit).build(records=records)

    async def invitations_send(self, payload: InvitationCreate) -> InvitationOut:
        # Check for existing pending invite to same email in this chamber
        existing = await self.invitations_repo.get_first(
            session=self.session,
            filters={
                UserInvitations.chamber_id: self.chamber_id,
                UserInvitations.email: payload.email,
                UserInvitations.status_code: "PN",
            },
        )
        if existing:
            raise ValidationErrorDetail(
                code=ErrorCodes.VALIDATION_ERROR,
                message=f"A pending invitation already exists for {payload.email}",
            )

        # Check if user is already a member
        from app.database.models.user_chamber_link import UserChamberLink
        existing_member = await self.session.execute(
            select(Users)
            .join(UserChamberLink, Users.user_id == UserChamberLink.user_id)
            .where(
                Users.email == payload.email,
                UserChamberLink.chamber_id == self.chamber_id,
                UserChamberLink.left_date.is_(None),
                UserChamberLink.status_ind.is_(True),
            )
        )
        if existing_member.scalars().first():
            raise ValidationErrorDetail(
                code=ErrorCodes.VALIDATION_ERROR,
                message=f"{payload.email} is already a member of this chamber",
            )

        expires = date.today() + timedelta(days=payload.expires_days)
        inv = await self.invitations_repo.create(
            session=self.session,
            data={
                "chamber_id": self.chamber_id,
                "email": payload.email,
                "role_id": payload.role_id,
                "invited_by": self.user_id,
                "expires_date": expires,
                "status_code": "PN",
                "message": payload.message,
                "created_by": self.user_id,
            },
        )
        return await self._to_out(inv)

    async def invitations_revoke(self, payload: InvitationRevoke) -> dict:
        inv = await self.invitations_repo.get_by_id(
            session=self.session,
            filters={
                UserInvitations.invitation_id: payload.invitation_id,
                UserInvitations.chamber_id: self.chamber_id,
            },
        )
        if not inv:
            raise ValidationErrorDetail(code=ErrorCodes.NOT_FOUND, message="Invitation not found")
        if inv.status_code != "PN":
            raise ValidationErrorDetail(
                code=ErrorCodes.VALIDATION_ERROR,
                message=f"Invitation is '{inv.status_code}', cannot revoke",
            )
        await self.invitations_repo.update(
            session=self.session, id_values=payload.invitation_id,
            data={"status_code": "RV" if hasattr(inv, "RV") else "EX"},
        )
        return {"invitation_id": payload.invitation_id, "status": "Revoked"}
