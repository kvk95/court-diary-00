# app/services/email_service.py

import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.database.models.email_settings import EmailSettings
from app.database.models.email_templates import EmailTemplates
from app.database.models.refm_email_templates import RefmEmailTemplates
from app.core.config import settings
from app.dtos.send_email_dto import InvoiceReceiptEmailDto, SendEmailStatusDto

class SendEmailService:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def _get_smtp_config(self, company_id: int) -> dict:
        stmt = select(EmailSettings).where(
            EmailSettings.company_id == company_id,
            EmailSettings.status == True,
            EmailSettings.is_default == True
        )
        result = await self.session.execute(stmt)
        config = result.scalar_one_or_none()

        if config:
            return {
                "host": config.smtp_host,
                "port": config.smtp_port,
                "username": config.smtp_user,
                "password": config.smtp_password,
                "use_tls": config.encryption_code in ("TLS", "STARTTLS"),
                "from_email": config.email or "no-reply@yourcompany.com",
            }

        # Env fallback
        return {
            "host": settings.SMTP_SERVER,
            "port": settings.SMTP_SERVER_PORT,
            "username": settings.SMTP_SERVER_USERNAME,
            "password": settings.SMTP_SERVER_PASSWORD,
            "use_tls": settings.SMTP_USE_TLS,
            "from_email": "no-reply@yourcompany.com",
        }

    async def _get_invoice_receipt_template(self, company_id: int, override_subject: str | None = None, override_content: str | None = None) -> tuple[str, str]:
        code = "invoice_receipt"

        if override_subject and override_content:
            return override_subject, override_content

        # Try company custom
        stmt = select(EmailTemplates).where(
            EmailTemplates.company_id == company_id,
            EmailTemplates.code == code,
            EmailTemplates.enabled == True
        )
        result = await self.session.execute(stmt)
        custom = result.scalar_one_or_none()

        if custom:
            return custom.subject, custom.content

        # Master
        stmt_master = select(RefmEmailTemplates).where(RefmEmailTemplates.code == code)
        result_master = await self.session.execute(stmt_master)
        master = result_master.scalar_one_or_none()

        if not master:
            raise ValueError(f"Master template '{code}' not found")

        return master.subject, master.description

    def _replace_placeholders(self, text: str, tags: dict) -> str:
        for key, value in tags.items():
            text = text.replace(f"{{{key}}}", str(value))
        return text

    async def send_invoice_receipt_email(self, dto: InvoiceReceiptEmailDto) -> SendEmailStatusDto:
        """
        Core sending logic — only consumes the DTO prepared by FinanceService
        """
        smtp_config = await self._get_smtp_config(dto.company_id)

        subject, html_template = await self._get_invoice_receipt_template(
            dto.company_id,
            dto.subject_template,
            dto.content_template
        )

        # Apply tags from DTO
        final_subject = self._replace_placeholders(subject, dto.tags)
        final_html = self._replace_placeholders(html_template, dto.tags)

        # Build email
        msg = MIMEMultipart()
        msg["From"] = smtp_config["from_email"]
        msg["To"] = dto.recipient_email
        msg["Subject"] = final_subject

        msg.attach(MIMEText(final_html, "html"))

        # Attach PDF
        pdf_part = MIMEApplication(dto.pdf_bytes, _subtype="pdf")
        pdf_part.add_header("Content-Disposition", "attachment", filename=dto.pdf_filename)
        msg.attach(pdf_part)

        # Send
        try:
            with smtplib.SMTP(smtp_config["host"], smtp_config["port"]) as server:
                if smtp_config["use_tls"]:
                    server.starttls()
                server.login(smtp_config["username"], smtp_config["password"])
                server.send_message(msg)

            return SendEmailStatusDto(
                status = "success",
                sent_to = dto.recipient_email,
                subject =final_subject,
                invoice_id = dto.invoice_id)

        except Exception as e:
            raise RuntimeError(f"Failed to send email: {str(e)}")