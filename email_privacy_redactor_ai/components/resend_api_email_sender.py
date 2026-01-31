import os
import base64
import httpx


class ResendEmailSender:
    """Sends emails via the Resend API (primary production channel)."""

    def __init__(self, api_key: str | None = None):
        self.api_key = api_key or os.getenv("RESEND_API_KEY", "")
        if not self.api_key:
            print("❌ RESEND_API_KEY not set")

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
        """Send email through Resend or fall back to direct HTTP call if the SDK is missing."""
        api_key = api_key or self.api_key
        if not api_key:
            return False

        try:
            cleaned_to_email, cleaned_cc_email = self.deduplicate_email_addresses(
                to_email, cc_email
            )

            params = {
                "from": from_email,
                "to": [cleaned_to_email],
                "subject": subject,
                "text": body_text,
            }
            if cleaned_cc_email:
                params["cc"] = [cleaned_cc_email]
            if images:
                params["attachments"] = [
                    {"filename": f"image_{idx + 1}.png", "content": img_b64}
                    for idx, img_b64 in enumerate(images)
                ]

            try:
                import resend

                resend.api_key = api_key
                email = resend.Emails.send(params)
                print(f"✅ Email sent via Resend! ID: {email['id']}")
                return True
            except ImportError:
                async with httpx.AsyncClient(timeout=30.0) as client:
                    response = await client.post(
                        "https://api.resend.com/emails",
                        headers={
                            "Authorization": f"Bearer {api_key}",
                            "Content-Type": "application/json",
                        },
                        json=params,
                    )
                    if response.status_code == 200:
                        result = response.json()
                        print(f"✅ Email sent via Resend! ID: {result.get('id')}")
                        return True
                    else:
                        print(f"❌ Resend error: {response.status_code} - {response.text}")
                        return False
        except Exception as e:
            print(f"❌ Error sending via Resend: {e}")
            return False


resend_email_sender = ResendEmailSender()