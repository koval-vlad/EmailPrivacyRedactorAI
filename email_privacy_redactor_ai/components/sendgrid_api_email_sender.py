import os
import base64
import httpx
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders

# ============================================================
# OPTION 2: SendGrid API
# ============================================================
# FREE: 100 emails/day
# Sign up: https://sendgrid.com

def deduplicate_email_addresses(to_email: str, cc_email: str = "") -> tuple[str, str]:
    """
    Remove duplicate email addresses between to and cc fields.
    SendGrid and Resend require unique email addresses across to, cc, and bcc fields.
    
    Args:
        to_email: Primary recipient email
        cc_email: CC recipient email (optional)
    
    Returns:
        tuple: (cleaned_to_email, cleaned_cc_email) where cc_email is empty if it matches to_email
    """
    # Normalize emails (lowercase and strip whitespace)
    to_normalized = to_email.lower().strip() if to_email else ""
    cc_normalized = cc_email.lower().strip() if cc_email else ""
    
    # If CC email matches TO email, remove it from CC
    if cc_normalized and cc_normalized == to_normalized:
        return to_email, ""
    
    return to_email, cc_email


async def send_email_sendgrid(
    from_email: str,
    to_email: str,
    subject: str,
    body_text: str,
    cc_email: str = "",
    images: list = None,
    api_key: str = None
) -> bool:
    """
    Send email via SendGrid API
    
    Args:
        from_email: Sender email (must be verified in SendGrid)
        to_email: Recipient email
        subject: Email subject
        body_text: Email body
        cc_email: CC recipient (optional)
        images: List of base64 encoded images (optional)
        api_key: SendGrid API key (or set SENDGRID_API_KEY env var)
    
    Returns:
        bool: True if sent successfully
    """
    api_key = api_key or os.getenv("SENDGRID_API_KEY", "")
    
    if not api_key:
        print("ERROR: SENDGRID_API_KEY not set")
        return False
    
    try:
        # Deduplicate email addresses (SendGrid requires unique emails across to, cc, bcc)
        cleaned_to_email, cleaned_cc_email = deduplicate_email_addresses(to_email, cc_email)
        
        # Prepare email data
        email_data = {
            "personalizations": [{
                "to": [{"email": cleaned_to_email}],
            }],
            "from": {"email": from_email},
            "subject": subject,
            "content": [{
                "type": "text/plain",
                "value": body_text
            }]
        }
        
        # Add CC if provided and not a duplicate
        if cleaned_cc_email:
            email_data["personalizations"][0]["cc"] = [{"email": cleaned_cc_email}]
        
        # Add attachments if provided
        if images:
            attachments = []
            for idx, img_b64 in enumerate(images):
                attachments.append({
                    "content": img_b64,
                    "filename": f"image_{idx + 1}.png",
                    "type": "image/png",
                    "disposition": "attachment"
                })
            email_data["attachments"] = attachments
        
        # Send via SendGrid API
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                "https://api.sendgrid.com/v3/mail/send",
                headers={
                    "Authorization": f"Bearer {api_key}",
                    "Content-Type": "application/json",
                },
                json=email_data
            )
            
            if response.status_code == 202:
                print(f"✅ Email sent successfully via SendGrid to {to_email}")
                return True
            else:
                print(f"❌ SendGrid API error: {response.status_code} - {response.text}")
                return False
                
    except Exception as e:
        print(f"❌ Error sending email via SendGrid: {e}")
        return False
