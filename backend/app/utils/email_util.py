import os
import smtplib
import ssl
from email import encoders
from email.mime.base import MIMEBase
from email.mime.image import MIMEImage
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from app.core.config import Settings
from app.database.models.email_link import EmailLink
from app.database.models.refm_email_templates import RefmEmailTemplates, RefmEmailTemplatesEnum
from app.services.base.base_service import BaseService


class EmailUtil (BaseService):

    def __init__(self,                 
            session,
                 ):
        super().__init__(session)
        settings = Settings() 
        self.smtp_server = settings.SMTP_SERVER
        self.smtp_server_port = settings.SMTP_SERVER_PORT
        self.smtp_server_username = settings.SMTP_SERVER_USERNAME
        self.smtp_server_password = settings.SMTP_SERVER_PASSWORD
        # self.smtp_server_use_tls = strtobool(os.getenv("SMTP_USE_TLS"))

    async def get_email_content(self, template_code: RefmEmailTemplatesEnum, dynamic_values):
        """
        Retrieves email subject and body based on template_key and fills in placeholders.
        """
        subject = await self.refm_resolver.from_column(
            column_attr=EmailLink.template_code,
            code=template_code.value,
            value_column=RefmEmailTemplates.subject,
            default=None
        )
        body = await self.refm_resolver.from_column(
            column_attr=EmailLink.template_code,
            code=template_code.value,
            value_column=RefmEmailTemplates.content,
            default=None
        )

        if not body:
            raise ValueError(f"Email template '{template_code}' not found!")
        
        body = body.format(**dynamic_values)  # Fill placeholders
        return subject, body

        return subject, body

    async def send_email_from_template(self, to_emails, template_code: RefmEmailTemplatesEnum, dynamic_values):
        """
        Retrieves email content and sends an email using EmailUtil2.
        """
        subject, body = await self.get_email_content(template_code, dynamic_values)
        self.send_email(to_emails=to_emails, subject=subject, body=body)

    def send_email(self, to_emails, subject, body, attachments=None):
        try:            

            # If partially configured → fail
            if not self.smtp_server or not self.smtp_server_port or not self.smtp_server_username or not self.smtp_server_password:
                raise ValueError(
                    "\n" + "=" * 80 +
                    "\nFATAL CONFIG ERROR: Incomplete SMTP configuration!\n"
                    "All SMTP fields must be provided:\n"
                    "  - SMTP_SERVER\n"
                    "  - SMTP_SERVER_PORT\n"
                    "  - SMTP_SERVER_USERNAME\n"
                    "  - SMTP_SERVER_PASSWORD\n"
                    "=" * 80 + "\n"
                )

            # Create MIME message
            message = MIMEMultipart()
            # Set the sender's email.
            message["From"] = self.smtp_server_username
            # Join the list of recipients into a single string separated by commas.
            message["To"] = ", ".join(to_emails)
            message["BCC"] = self.smtp_server_username
            # Set the subject of the email.
            message["Subject"] = f"Court Diary • {subject}"

            # Load email template and replace {body} with actual content
            template_path = os.path.join("static", "email_template.html")
            with open(template_path, "r", encoding="utf-8") as tfile:
                template_content = tfile.read()

            msg_body = template_content.replace("{body}", body).replace(
                "{tomail}", ", ".join(to_emails)
            )  # Replace placeholder

            part1 = MIMEText(msg_body, "html", "utf-8")
            message.attach(part1)

            # Check if "cid:image1" exists in msg_body before attaching the image
            if "cid:image1" in msg_body:

                with open("static/logo01.png", "rb") as fp:
                    image_data = fp.read()

                image = MIMEImage(image_data)
                image.add_header("Content-ID", "<image1>")
                message.attach(image)

            # Attach files if provided
            if attachments:
                for attachment in attachments:
                    with open(attachment, "rb") as file:
                        part = MIMEBase("application", "octet-stream")
                        part.set_payload(file.read())
                        encoders.encode_base64(part)
                        part.add_header(
                            "Content-Disposition", f"attachment; filename={attachment}"
                        )
                        message.attach(part)

            # Connect to SMTP server using SSL.
            # with smtplib.SMTP(self.smtp_server, self.smtp_server_port) as server:
            context = ssl.create_default_context()
            with smtplib.SMTP_SSL(
                self.smtp_server,
                self.smtp_server_port,
                context=context,
            ) as server:
                # if self.smtp_server_use_tls:
                #     server.starttls()
                # Login to the SMTP server using the sender's credentials.
                server.login(self.smtp_server_username, self.smtp_server_password)
                # Send the email. The sendmail function requires the sender's email, the list of recipients, and the email message as a string.
                server.sendmail(
                    self.smtp_server_username, to_emails, message.as_string()
                )
            print("Email sent successfully!")

        except Exception as e:
            print(f"Failed to send email: {e}")
            raise e
