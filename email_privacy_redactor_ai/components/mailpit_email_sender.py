import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
import base64
from io import BytesIO

# ============================================================
# You need to download Mailpit.exe (https://mailpit.axllent.org) and add it to your User Path like this: C:\Users\Vlad\DevTools\mailpit
# Running locally on port 1025
# It has Inbox on: http://localhost:8025/ where you can see all emails sent and received.
# It is a free SMTP server that can be used to test emails locally.
# It is a good way to test emails locally before sending them to the real world.
# It doesn't send emails outside of your local machine.
# ============================================================
# FREE

class MailpitEmailSender:
    """Sends emails via Mailpit (local SMTP testing server)."""

    @staticmethod
    def deduplicate_email_addresses(
        to_email: str, cc_email: str = ""
    ) -> tuple[str, str]:
        """
        Remove duplicate email addresses between to and cc fields.
        Applied for consistency with production email services (SendGrid/Resend).
        """
        to_normalized = to_email.lower().strip() if to_email else ""
        cc_normalized = cc_email.lower().strip() if cc_email else ""

        if cc_normalized and cc_normalized == to_normalized:
            return to_email, ""

        return to_email, cc_email

    def send_email(
        self,
        from_email: str,
        to_email: str,
        subject: str,
        body_text: str,
        cc_email: str = "",
        images: list | None = None,
    ) -> bool:
        """Send email via Mailpit."""
        try:
            cleaned_to_email, cleaned_cc_email = self.deduplicate_email_addresses(
                to_email, cc_email
            )
            msg = MIMEMultipart()
            msg["From"] = from_email
            msg["To"] = cleaned_to_email
            msg["Subject"] = subject

            if cleaned_cc_email:
                msg["Cc"] = cleaned_cc_email

            msg.attach(MIMEText(body_text, "plain"))

            if images:
                for idx, img_b64 in enumerate(images):
                    img_data = base64.b64decode(img_b64)
                    image_part = MIMEBase("image", "png")
                    image_part.set_payload(img_data)
                    encoders.encode_base64(image_part)
                    image_part.add_header(
                        "Content-Disposition",
                        f'attachment; filename="image_{idx + 1}.png"',
                    )
                    msg.attach(image_part)

            with smtplib.SMTP("localhost", 1025) as server:
                recipients = [cleaned_to_email]
                if cleaned_cc_email:
                    recipients.append(cleaned_cc_email)
                server.send_message(msg)
                print(f"✅ Email sent successfully to {cleaned_to_email}")
                return True
        except Exception as e:
            print(f"❌ Error sending email: {e}")
            return False


mailpit_email_sender = MailpitEmailSender()

