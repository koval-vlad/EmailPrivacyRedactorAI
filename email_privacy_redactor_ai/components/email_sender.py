import os
from email_privacy_redactor_ai.components.mailpit_email_sender import send_email_via_mailpit
from email_privacy_redactor_ai.components.resend_api_email_sender import send_email_resend
from email_privacy_redactor_ai.components.sendgrid_api_email_sender import send_email_sendgrid


async def send_email(state):
    """
    Send the redacted email.
    
    In development: Uses Mailpit (local SMTP testing server)
    In production: Tries Resend API first, falls back to SendGrid if Resend fails
    
    To test production email sending locally, set USE_PRODUCTION_EMAIL=true in .env
    """
    try:
        # Check if we should use production email sending
        # Set USE_PRODUCTION_EMAIL=true in .env to test production email locally
        use_production = os.getenv("USE_PRODUCTION_EMAIL", "").lower() == "true"
        
        # In development (default), use Mailpit
        if not use_production:
            print("📧 Using Mailpit for local email testing...")
            from_email_mailpit = os.getenv("EMAIL_SENDER_MAILPIT", "")
            success = send_email_via_mailpit(
                from_email=from_email_mailpit,
                to_email=state.to_email,
                subject=state.subject,
                body_text=state.redacted_content,
                cc_email=state.cc_email,
                images=state.redacted_images if state.redacted_images else None
            )
            
            if success:
                state.step = "sent"
            else:
                print("Warning: Email sending failed, but proceeding to sent step")
                state.step = "sent"
            return
        
        # In production: Try Resend first, then SendGrid as fallback
        print("📧 Using production email services (Resend → SendGrid fallback)...")
        
        # Try Resend first
        from_email_resend = os.getenv("EMAIL_SENDER_RESEND", "")
        resend_success = await send_email_resend(
            from_email=from_email_resend,
            to_email=state.to_email,
            subject=state.subject,
            body_text=state.redacted_content,
            cc_email=state.cc_email,
            images=state.redacted_images if state.redacted_images else None
        )
        
        if resend_success:
            print("✅ Email sent successfully via Resend")
            state.step = "sent"
            return
        
        # Resend failed, try SendGrid as fallback
        print("⚠️ Resend failed, trying SendGrid as fallback... from_email_resend: ", from_email_resend)
        from_email_sendgrid = os.getenv("EMAIL_SENDER_SENDGRID", "")
        sendgrid_success = await send_email_sendgrid(
            from_email=from_email_sendgrid,
            to_email=state.to_email,
            subject=state.subject,
            body_text=state.redacted_content,
            cc_email=state.cc_email,
            images=state.redacted_images if state.redacted_images else None
        )
        
        if sendgrid_success:
            print("✅ Email sent successfully via SendGrid (fallback)")
            state.step = "sent"
        else:
            print("❌ Both Resend and SendGrid failed. Email not sent. from_email_sendgrid: ", from_email_sendgrid)
            # Still proceed to sent step - you may want to add error handling UI here
            state.step = "sent"
            
    except Exception as e:
        print(f"❌ Error in send_email: {e}")
        import traceback
        traceback.print_exc()
        # Still proceed to sent step even on error
        state.step = "sent"

