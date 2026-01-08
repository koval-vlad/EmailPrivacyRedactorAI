import os
import base64
import httpx

# ============================================================
# OPTION 1: Resend API (RECOMMENDED for Reflex Cloud)
# ============================================================
# FREE: 100 emails/day, 3,000/month
# Sign up: https://resend.com
# No credit card required

def deduplicate_email_addresses(to_email: str, cc_email: str = "") -> tuple[str, str]:
    """
    Remove duplicate email addresses between to and cc fields.
    Resend and SendGrid require unique email addresses across to, cc, and bcc fields.
    
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


async def send_email_resend(
    from_email: str,
    to_email: str,
    subject: str,
    body_text: str,
    cc_email: str = "",
    images: list = None,
    api_key: str = None
) -> bool:
    """Send email via Resend API"""
    api_key = api_key or os.getenv("RESEND_API_KEY", "")
    
    if not api_key:
        print("❌ RESEND_API_KEY not set")
        return False
        
    try:
        # Deduplicate email addresses (Resend requires unique emails across to, cc, bcc)
        cleaned_to_email, cleaned_cc_email = deduplicate_email_addresses(to_email, cc_email)
        
        # Use resend package if available
        try:
            import resend
            resend.api_key = api_key
            
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
            
            email = resend.Emails.send(params)
            print(f"✅ Email sent via Resend! ID: {email['id']}")
            return True
            
        except ImportError:
            # Fallback to direct API call if resend package not installed
            email_data = {
                "from": from_email,
                "to": [cleaned_to_email],
                "subject": subject,
                "text": body_text,
            }
            
            if cleaned_cc_email:
                email_data["cc"] = [cleaned_cc_email]
            
            if images:
                email_data["attachments"] = [
                    {"filename": f"image_{idx + 1}.png", "content": img_b64}
                    for idx, img_b64 in enumerate(images)
                ]
            
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(
                    "https://api.resend.com/emails",
                    headers={
                        "Authorization": f"Bearer {api_key}",
                        "Content-Type": "application/json",
                    },
                    json=email_data
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