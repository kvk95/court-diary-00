import smtplib
import ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.image import MIMEImage
import os
from email import encoders
from email.mime.base import MIMEBase


port = 465  # For SSL
smtp_server = "smtp.gmail.com"
sender_email = "lokesh.protech@gmail.com"  # Enter your address
sender_password = "dmsw pfef abql ssor"


data = {"first_name": "John"}
email = "mani.lokesh@gmail.com"


class EmailUtil2:

    email_templates = {
        "welcome_email": {
            "subject": "Welcome to AARIV Resumes! Now What? 🎉",
            "body": """<p class="primarycolor bolder">Dear ! <b>{first_name}</b>,</p>  
                        <p>I hope this message finds you well. </p>  
                        <p>We're writing to extend a heartfelt welcome to you as you begin your journey with us.<br/>We're thrilled that you've chosen our platform to create your resumes, and we're committed to providing you with an exceptional experience. </p>  
                        <p>We can’t wait for you to explore all the exciting features available.</p>  
                        <p class="primarycolor smaller textcenter"><br/>Welcome aboard! 😊</p>  
                        """,
        },
        "activate_account": {
            "subject": "Activate Your Account ✨",
            "body": """<p class="primarycolor bolder">Greetings!,</p>  
                        <p>We’re excited to have you join us! 🎉</p>  
                        <p>Click the <a href="{activation_link}" target="_blank">link</a> below to activate your account and start exploring.</p>
                        <p><a href="{activation_link}" target="_blank" style="font-size:14px;">{activation_link}</a></p>
                        <p>{default_password_message}</p>
                        <p class="primarycolor smaller textcenter"><br/>Welcome aboard! If you have any questions, feel free to reach out.</p>
                        """,
        },
        "reset_password": {
            "subject": "Reset Password 🔑",
            "body": """<p class="primarycolor bolder">Hi !,</p>  
                        <p>We received a request to reset your password.</p>  
                        <p>To proceed, click the link below:</p>  
                        <p><a href="{reset_link}" target="_blank">{reset_link}</a></p>  
                        <p>If you didn’t request a password reset, you can safely ignore this email.</p>  
                        <p class="primarycolor smaller textcenter"><br/>Stay secure, and let us know if you need any help.</p>  
                        """,
        },
    }

    def __init__(self):
        # Use the global variables directly if environment variables are not set
        self.smtp_server = os.getenv("SMTP_SERVER", smtp_server)
        self.smtp_server_port = int(
            os.getenv("SMTP_SERVER_PORT", str(port))
        )  # Ensure port is int
        self.smtp_server_username = os.getenv("SMTP_SERVER_USERNAME", sender_email)
        self.smtp_server_password = os.getenv("SMTP_SERVER_PASSWORD", sender_password)
        # self.smtp_server_use_tls = strtobool(os.getenv("SMTP_USE_TLS"))

    def get_email_content(self, template_key, dynamic_values):
        """
        Retrieves email subject and body based on template_key and fills in placeholders.
        """
        template = self.email_templates.get(template_key)

        if not template:
            raise ValueError(f"Email template '{template_key}' not found!")

        subject = template["subject"]
        body = template["body"].format(**dynamic_values)  # Fill placeholders

        return subject, body

    def send_email_from_template(self, to_emails, template_key, dynamic_values):
        """
        Retrieves email content and sends an email using EmailUtil2.
        """
        subject, body = self.get_email_content(template_key, dynamic_values)
        self.send_email(to_emails=to_emails, subject=subject, body=body)

    def send_email(self, to_emails, subject, body, attachments=None):
        try:
            # Create MIME message
            message = MIMEMultipart()
            # Set the sender's email.
            message["From"] = self.smtp_server_username
            # Join the list of recipients into a single string separated by commas.
            message["To"] = ", ".join(to_emails)
            message["BCC"] = self.smtp_server_username
            # Set the subject of the email.
            message["Subject"] = f"TalSuite.ai • {subject}"

            # Load email template and replace {body} with actual content
            template_path = os.path.join("static", "email_template.html")
            # Ensure static/email_template.html and static/app_logo.png exist
            # For this example, I'll assume they exist or you'll create them.
            # You can create dummy files for testing:
            # echo "<html><body>{body}<p>Contact: {tomail}</p><img src='cid:image1'></body></html>" > static/email_template.html
            # Create an empty app_logo.png or any small image

            with open(template_path, "r", encoding="utf-8") as tfile:
                template_content = tfile.read()

            msg_body = template_content.replace("{body}", body).replace(
                "{tomail}", ", ".join(to_emails)
            )  # Replace placeholder

            part1 = MIMEText(msg_body, "html", "utf-8")
            message.attach(part1)

            # Check if "cid:image1" exists in msg_body before attaching the image
            if "cid:image1" in msg_body:
                with open("static/app_logo.png", "rb") as fp:
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
                            "Content-Disposition",
                            f"attachment; filename={os.path.basename(attachment)}",  # Use basename for filename
                        )
                        message.attach(part)

            context = ssl.create_default_context()
            with smtplib.SMTP_SSL(
                self.smtp_server,
                self.smtp_server_port,
                context=context,
            ) as server:
                server.login(self.smtp_server_username, self.smtp_server_password)
                server.sendmail(
                    self.smtp_server_username, to_emails, message.as_string()
                )
            print("Email sent successfully!")

        except Exception as e:
            print(f"Failed to send email: {e}")
            raise e


email_util = EmailUtil2()
# Send the email
email_util.send_email_from_template(
    to_emails=[email],
    template_key="welcome_email",
    dynamic_values={"first_name": data.get("first_name", "")},
)
