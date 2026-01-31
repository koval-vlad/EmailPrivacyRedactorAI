import os
import base64
import httpx


class SendgridEmailSender:
    """Handles SendGrid API-based email delivery (fallback production channel)."""

    def __init__(self, api_key: str | None = None):
        self.api_key = api_key or os.getenv("SENDGRID_API_KEY", "")
        if not self.api_key:
            print("ERROR: SENDGRID_API_KEY not set")

    @staticmethod
    def deduplicate_email_addresses(
        to_email: str, cc_email: str = ""
    ) -> tuple[str, str]:
        to_normalized = to_email.lower().strip() if to_email else ""
        cc_normalized = cc_email.lower().strip() if cc_email else ""
        if cc_normalized and cc_normalized == to_normalized:
            return to_email, ""
        return to_email, cc_email

    async def send_email(
        self,
        from_email: str,
        to_email: str,
        subject: str,
        body_text: str,
        cc_email: str = "",
        images: list | None = None,
        api_key: str | None = None,
    ) -> bool:
        api_key = api_key or self.api_key
        if not api_key:
            return False

        try:
            cleaned_to_email, cleaned_cc_email = self.deduplicate_email_addresses(
                to_email, cc_email
            )
            email_data = {
                "personalizations": [
                    {"to": [{"email": cleaned_to_email}]},
                ],
                "from": {"email": from_email},
                "subject": subject,
                "content": [
                    {
                        "type": "text/plain",
                        "value": body_text,
                    }
                ],
            }
            if cleaned_cc_email:
                email_data["personalizations"][0]["cc"] = [
                    {"email": cleaned_cc_email}
                ]
            if images:
                attachments = []
                for idx, img_b64 in enumerate(images):
                    attachments.append(
                        {
                            "content": img_b64,
                            "filename": f"image_{idx + 1}.png",
                            "type": "image/png",
                            "disposition": "attachment",
                        }
                    )
                email_data["attachments"] = attachments

            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(
                    "https://api.sendgrid.com/v3/mail/send",
                    headers={
                        "Authorization": f"Bearer {api_key}",
                        "Content-Type": "application/json",
                    },
                    json=email_data,
                )
                if response.status_code == 202:
                    print(f"✅ Email sent successfully via SendGrid to {to_email}")
                    return True
                print(f"❌ SendGrid API error: {response.status_code} - {response.text}")
                return False
        except Exception as e:
            print(f"❌ Error sending email via SendGrid: {e}")
            return False


sendgrid_email_sender = SendgridEmailSender()
