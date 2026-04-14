from datetime import datetime, timedelta
from typing import Optional


from app.database.models.email_link import EmailLink
from app.database.models.refm_email_templates import RefmEmailTemplatesEnum
from app.database.repositories.email_link_repository import EmailLinkRepository
from app.services.base.base_service import BaseService
from app.utils.email_util import EmailUtil
from app.utils.utilities import parse_lid, generate_lid
from app.validators.validation_errors import ValidationErrorDetail
from app.validators.error_codes import ErrorCodes


class EmailLinkService(BaseService):

    def __init__(
            self, 
            session,            
            email_link_repo: Optional[EmailLinkRepository] = None,
            email_util: Optional[EmailUtil] = None,
            ):
        super().__init__(session)
        self.email_link_repo = email_link_repo or EmailLinkRepository()
        self.email_util = email_util or EmailUtil(session)

    # ─────────────────────────────────────────────
    # 🔗 CREATE LINK
    # ─────────────────────────────────────────────
    async def generate_link(
        self,
        *,
        user_id: str,
        email: str,
        template_code: RefmEmailTemplatesEnum,
        expiry_days: int = 3,
    ) -> str:

        expiry_date = datetime.now() + timedelta(days=expiry_days)
        recipient_email = email.lower()

        # 1. DELETE OLD LINKS
        old_links = await self.email_link_repo.list_all(
            session=self.session,
            filters={
                EmailLink.user_id: user_id,
                EmailLink.template_code: template_code.value,
            }
        )

        for link in old_links:
            await self.email_link_repo.delete(
                session=self.session,
                id_values=link.link_id,
                soft=True
            )

        # 2. CREATE NEW LINK
        link = await self.email_link_repo.create(
            session=self.session,
            data={
                "user_id": user_id,
                "recipient_email": recipient_email,
                "template_code": template_code.value,
                "expiry_date": expiry_date,
            },
        )

        # 3. ENCRYPT
        encrypted_id = generate_lid(link.link_id)

        # 4. BUILD URL
        link_url = f"{self.ui_url}login?lid={encrypted_id}&code={template_code.value}"

        # 5. OPTIONAL: STORE URL
        await self.email_link_repo.update(
            session=self.session,
            id_values=link.link_id,
            data={"link_url": link_url}
        )

        mail_content = await self.email_util.send_email_from_template(
                to_emails=[recipient_email],
                template_code=template_code,
                dynamic_values={
                    "activation_link": link_url,
                    "default_password_message":"Set your new password",
                    "reset_link": link_url,
                },
            )
        return link_url

    # ─────────────────────────────────────────────
    # 🔍 VERIFY LINK
    # ─────────────────────────────────────────────
    async def verify_link(
        self,
        *,
        encrypted_id: str,
    ) -> EmailLink:
        
        link_id = parse_lid(encrypted_id)

        row = await self.email_link_repo.get_first(
            session=self.session,
            where=[
                EmailLink.link_id == link_id,
                (
                    (EmailLink.expiry_date.is_(None)) |
                    (EmailLink.expiry_date > datetime.now())
                )
            ]
        )

        if not row:
            raise ValidationErrorDetail(
                code=ErrorCodes.VALIDATION_ERROR,
                message="Invalid or expired link",
            )

        return row

    # ─────────────────────────────────────────────
    # 🔥 CONSUME LINK (VERIFY + DELETE)
    # ─────────────────────────────────────────────
    async def consume_link(
        self,
        *,
        encrypted_id: str,
    ) -> EmailLink:

        link = await self.verify_link(
            encrypted_id=encrypted_id
        )

        link_id = parse_lid(encrypted_id)

        await self.email_link_repo.delete(
            session=self.session,
            id_values=link.link_id,
            soft=True
        )

        return link