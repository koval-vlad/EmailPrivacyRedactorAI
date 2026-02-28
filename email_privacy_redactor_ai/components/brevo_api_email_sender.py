import os
import base64
import httpx


class BrevoEmailSender:
    """Handles Brevo API-based email delivery (fallback production channel)."""

    def __init__(self, api_key: str | None = None):
        self.api_key = api_key or os.getenv("BREVO_API_KEY", "")
        if not self.api_key:
            print("ERROR: BREVO_API_KEY not set")

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
            # Base email structure
            email_data = {
                "sender": {"email": from_email},
                "to": [{"email": cleaned_to_email}],
                "subject": subject,
                "textContent": body_text  
            }

            # Add CC if it exists
            if cleaned_cc_email:
                email_data["cc"] = [{"email": cleaned_cc_email}]

            # Add Attachments
            if images:
                attachments = []
                for idx, img_b64 in enumerate(images):
                    attachments.append({
                        "content": img_b64,
                        "name": f"image_{idx + 1}.png" 
                    })
                email_data["attachment"] = attachments 

            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(
                    "https://api.brevo.com/v3/smtp/email",
                    headers={
                        "api-key": api_key,  
                        "Content-Type": "application/json",
                        "Accept": "application/json",
                    },
                    json=email_data,
                )
                if response.status_code == 201:
                    print(f"✅ Email sent successfully via Brevo to {to_email}")
                    return True
                print(f"❌ Brevo API error: {response.status_code} - {response.text}")
                return False
        except Exception as e:
            print(f"❌ Error sending email via Brevo: {e}")
            return False


brevo_email_sender = BrevoEmailSender()
