from sqlalchemy import select, desc
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.models.user_chamber_link import UserChamberLink
from app.validators import ValidationErrorDetail, ErrorCodes


async def resolve_user_chamber(
    session: AsyncSession,
    user_id: str,
    requested_chamber_id: str | None = None,
):
    stmt = (
        select(UserChamberLink)
        .where(
            UserChamberLink.user_id == user_id,
            UserChamberLink.left_date.is_(None),
            UserChamberLink.status_ind.is_(True),
        )
        .order_by(desc(UserChamberLink.primary_ind))
    )

    result = await session.execute(stmt)
    rows = result.scalars().all()

    if not rows:
        raise ValidationErrorDetail(
            code=ErrorCodes.VALIDATION_ERROR,
            message="User has no active chamber membership",
        )

    chamber_ids = [r.chamber_id for r in rows]

    # ✅ priority logic (same as your OAuth)
    if requested_chamber_id and requested_chamber_id in chamber_ids:
        return requested_chamber_id

    return chamber_ids[0]  # primary (because ordered)