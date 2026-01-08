import httpx
import os


def get_groq_api_key() -> str:
    """Get Groq API key from environment"""
    api_key = os.getenv("GROQ_API_KEY", "")
    if not api_key:
        print("WARNING: GROQ_API_KEY not set in environment variables")
    return api_key


async def redact_text(state):
    """Call Groq API to redact sensitive information"""
    if not state.to_email or not state.content:
        return
    
    # Store original data
    state.original_to = state.to_email
    state.original_cc = state.cc_email
    state.original_subject = state.subject
    state.original_content = state.content
    state.original_images = state.uploaded_images.copy()
    
    state.loading = True
    state.ai_feedback = ""  # Clear previous feedback
    yield
    
    try:
        # Redact text content
        state.append_feedback("🔄 Connecting to Groq API for text redaction...")
        yield
        
        async with httpx.AsyncClient(timeout=30.0) as client:
            state.append_feedback("📤 Sending text to Groq API (Llama 3.3 70B)...")
            yield
            
            # Build the redaction instructions list only for enabled items
            redaction_instructions = []
            if getattr(state, 'redact_name_enabled', True):
                redaction_instructions.append(f"- Names (people's names, first names, last names, full names) → {state.redact_name}")
            if getattr(state, 'redact_email_enabled', True):
                redaction_instructions.append(f"- Email addresses (anything with @ symbol) → {state.redact_email}")
            if getattr(state, 'redact_phone_enabled', True):
                redaction_instructions.append(f"- Phone numbers (any format) → {state.redact_phone}")
            if getattr(state, 'redact_address_enabled', True):
                redaction_instructions.append(f"- Physical addresses (street addresses, cities, states, zip codes) → {state.redact_address}")
            if getattr(state, 'redact_ssn_enabled', True):
                redaction_instructions.append(f"- Social Security Numbers → {state.redact_ssn}")
            if getattr(state, 'redact_card_enabled', True):
                redaction_instructions.append(f"- Credit card numbers → {state.redact_card}")
            if getattr(state, 'redact_key_enabled', True):
                redaction_instructions.append(f"- API keys → {state.redact_key}")
            if getattr(state, 'redact_password_enabled', True):
                redaction_instructions.append(f"- Passwords → {state.redact_password}")
            if getattr(state, 'redact_token_enabled', True):
                redaction_instructions.append(f"- Tokens → {state.redact_token}")
            if getattr(state, 'redact_id_enabled', True):
                redaction_instructions.append(f"- ID numbers (user IDs, employee IDs, customer IDs, document IDs, verification IDs, any alphanumeric IDs with or without hyphens, formats like 'HC-9920-ALPHA', 'PASS-99283-TX', 'Document ID: XXX-XXXX-XXX', 'Verification ID: XXX-XXXX-XXX', etc) → {state.redact_id}")
            if getattr(state, 'redact_dollar_enabled', True):
                redaction_instructions.append(f"- Dollar amounts (prices, salaries, costs, $ amounts) → {state.redact_dollar}")
            if getattr(state, 'redact_account_enabled', True):
                redaction_instructions.append(f"- Account numbers (bank accounts, customer accounts) → {state.redact_account}")
            
            # Build the prompt
            if redaction_instructions:
                instructions_text = "\n".join(redaction_instructions)
                prompt_content = f"""You are an email privacy protection tool. Redact ONLY the sensitive information types listed below from the following email content by replacing them with the specified placeholders:

{instructions_text}

CRITICAL RULES:
1. ONLY redact the types listed above. Do NOT redact anything else.
2. Leave ALL other information completely unchanged - including any types not listed above.
3. DO NOT redact company names, organization names, or business names - leave them unchanged.
4. DO NOT redact common nouns, generic terms, or non-sensitive information.
5. Make sure each type is replaced with its EXACT placeholder shown above.
6. Be precise: match each item to its correct type and use the exact placeholder for that type.
7. If a type is not in the list above, it should NOT be redacted at all - leave it exactly as it appears in the original text.
8. FOR ID NUMBERS: Redact ALL identification numbers including alphanumeric IDs with hyphens, prefixes like "Document ID:", "Verification ID:", "Reference ID:", etc. Examples: "HC-9920-ALPHA", "PASS-99283-TX", "Document ID: HC-9920-ALPHA", "Verification ID: PASS-99283-TX" - ALL should be redacted as ID numbers.

Be thorough and catch all instances of the listed types. Return ONLY the redacted email content with no additional commentary or explanation.

Email content to redact:
{state.content}"""
            else:
                # No redaction types enabled - return content unchanged
                prompt_content = f"""You are an email privacy protection tool. No redaction types are currently enabled, so return the email content exactly as-is without any modifications.

Email content:
{state.content}"""
            
            response = await client.post(
                "https://api.groq.com/openai/v1/chat/completions",
                headers={
                    "Content-Type": "application/json",
                    "Authorization": f"Bearer {get_groq_api_key()}",
                },
                json={
                    "model": "llama-3.3-70b-versatile",
                    "messages": [{
                        "role": "user",
                        "content": prompt_content
                    }],
                    "temperature": 0.3,
                }
            )
            
            if response.status_code == 200:
                data = response.json()
                text_content = data.get("choices", [{}])[0].get("message", {}).get("content", state.content)
                state.redacted_content = text_content
                
                # Get usage info if available
                usage = data.get("usage", {})
                tokens_used = usage.get("total_tokens", 0)
                state.append_feedback(f"✅ Groq API: Text redaction complete ({tokens_used} tokens used)")
            else:
                state.append_feedback(f"⚠️ Groq API: Error {response.status_code} - {response.text[:100]}")
                state.redacted_content = state.content
            yield
        
        # Redact images
        if state.uploaded_images:
            state.append_feedback(f"🖼️ Processing {len(state.uploaded_images)} image(s) with OCR.space...")
            yield
            
            from email_privacy_redactor_ai.components.ocrspace_image_redactor import redact_image
            state.redacted_images = []
            for idx, img_b64 in enumerate(state.uploaded_images):
                state.append_feedback(f"📸 Processing image {idx + 1}/{len(state.uploaded_images)}...")
                yield
                redacted_img = await redact_image(img_b64, state)
                state.redacted_images.append(redacted_img)
            
            state.append_feedback(f"✅ All {len(state.uploaded_images)} image(s) processed successfully")
        else:
            state.append_feedback("ℹ️ No images to process")
        
        state.step = "preview"
            
    except Exception as e:
        error_msg = f"Error calling Groq API: {e}"
        print(error_msg)
        state.append_feedback(f"❌ Error: {error_msg}")
        state.redacted_content = state.content
        state.redacted_images = state.uploaded_images.copy()
        state.step = "preview"
    
    finally:
        state.loading = False

