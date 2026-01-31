import os

from email_privacy_redactor_ai.components.mailpit_email_sender import mailpit_email_sender
from email_privacy_redactor_ai.components.resend_api_email_sender import resend_email_sender
from email_privacy_redactor_ai.components.sendgrid_api_email_sender import sendgrid_email_sender


class EmailSender:
    """Orchestrates choosing which email provider to use for redacted messages."""

    def __init__(self, force_production: bool | None = None) -> None:
        self._force_production = force_production

    def should_use_production(self) -> bool:
        """Return whether the app should send via production APIs instead of Mailpit."""
        if self._force_production is not None:
            return self._force_production
        return os.getenv("USE_PRODUCTION_EMAIL", "").lower() == "true"

    async def send(self, state) -> None:
        """Send the redacted email using Mailpit (dev) or Resend/SendGrid (prod)."""
        try:
            if not self.should_use_production():
                self._send_with_mailpit(state)
                return

            await self._send_with_production(state)
        except Exception as e:
            print(f"❌ Error in {self.__class__.__name__}.send: {e}")
            import traceback

            traceback.print_exc()
            state.step = "sent"

    def _send_with_mailpit(self, state) -> None:
        print("📧 Using Mailpit for local email testing...")
        from_email_mailpit = os.getenv("EMAIL_SENDER_MAILPIT", "")
        success = mailpit_email_sender.send_email(
            from_email=from_email_mailpit,
            to_email=state.to_email,
            subject=state.subject,
            body_text=state.redacted_content,
            cc_email=state.cc_email,
            images=state.redacted_images if state.redacted_images else None,
        )

        if success:
            state.step = "sent"
        else:
            print("Warning: Email sending failed, but proceeding to sent step")
            state.step = "sent"

    async def _send_with_production(self, state) -> None:
        print("📧 Using production email services (Resend → SendGrid fallback)...")

        from_email_resend = os.getenv("EMAIL_SENDER_RESEND", "")
        resend_success = await resend_email_sender.send_email(
            from_email=from_email_resend,
            to_email=state.to_email,
            subject=state.subject,
            body_text=state.redacted_content,
            cc_email=state.cc_email,
            images=state.redacted_images if state.redacted_images else None,
        )

        if resend_success:
            print("✅ Email sent successfully via Resend")
            state.step = "sent"
            return

        print(
            "⚠️ Resend failed, trying SendGrid as fallback... from_email_resend: ",
            from_email_resend,
        )
        from_email_sendgrid = os.getenv("EMAIL_SENDER_SENDGRID", "")
        sendgrid_success = await sendgrid_email_sender.send_email(
            from_email=from_email_sendgrid,
            to_email=state.to_email,
            subject=state.subject,
            body_text=state.redacted_content,
            cc_email=state.cc_email,
            images=state.redacted_images if state.redacted_images else None,
        )

        if sendgrid_success:
            print("✅ Email sent successfully via SendGrid (fallback)")
            state.step = "sent"
        else:
            print(
                "❌ Both Resend and SendGrid failed. Email not sent. from_email_sendgrid: ",
                from_email_sendgrid,
            )
            state.step = "sent"


email_sender = EmailSender()

