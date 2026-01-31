import httpx
import os


class TextRedactor:
    """Encapsulates text-redaction prompts & Groq API calls."""

    def __init__(self, groq_api_key: str | None = None):
        self.api_key = groq_api_key or os.getenv("GROQ_API_KEY", "")
        if not self.api_key:
            print("WARNING: GROQ_API_KEY not set in environment variables")

    async def redact_text(self, state):
        """Call Groq to redact text and optionally images."""
        if not state.to_email or not state.content:
            return

        state.original_to = state.to_email
        state.original_cc = state.cc_email
        state.original_subject = state.subject
        state.original_content = state.content
        state.original_images = state.uploaded_images.copy()

        state.loading = True
        state.ai_feedback = ""
        yield

        try:
            state.append_feedback("🔄 Connecting to Groq API for text redaction...")
            yield

            async with httpx.AsyncClient(timeout=30.0) as client:
                state.append_feedback("📤 Sending text to Groq API (Llama 3.3 70B)...")
                yield

                prompt_content = self._build_prompt(state)
                response = await client.post(
                    "https://api.groq.com/openai/v1/chat/completions",
                    headers={
                        "Content-Type": "application/json",
                        "Authorization": f"Bearer {self.api_key}",
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
                    state.redacted_content = data.get("choices", [{}])[0].get("message", {}).get("content", state.content)
                    usage = data.get("usage", {})
                    tokens_used = usage.get("total_tokens", 0)
                    state.append_feedback(f"✅ Groq API: Text redaction complete ({tokens_used} tokens used)")
                else:
                    state.append_feedback(f"⚠️ Groq API: Error {response.status_code} - {response.text[:100]}")
                    state.redacted_content = state.content
                yield

            async for _ in self._process_images(state):
                pass
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

    def _build_prompt(self, state):
        mapping = [
            ("redact_name_enabled", "Names", state.redact_name),
            ("redact_email_enabled", "Email addresses", state.redact_email),
            ("redact_phone_enabled", "Phone numbers", state.redact_phone),
            ("redact_address_enabled", "Physical addresses", state.redact_address),
            ("redact_ssn_enabled", "Social Security Numbers", state.redact_ssn),
            ("redact_card_enabled", "Credit card numbers", state.redact_card),
            ("redact_key_enabled", "API keys", state.redact_key),
            ("redact_password_enabled", "Passwords", state.redact_password),
            ("redact_token_enabled", "Tokens", state.redact_token),
            ("redact_id_enabled", "ID numbers", state.redact_id),
            ("redact_dollar_enabled", "Dollar amounts", state.redact_dollar),
            ("redact_account_enabled", "Account numbers", state.redact_account),
        ]

        instructions = []
        for attr, label, placeholder in mapping:
            if getattr(state, attr, True):
                instructions.append(f"- {label} → {placeholder}")

        if instructions:
            instructions_text = "\n".join(instructions)
            return f"""You are an email privacy protection tool. Redact ONLY the sensitive information types listed below from the following email content by replacing them with the specified placeholders:

-{instructions_text}

-CRITICAL RULES:
-1. ONLY redact the types listed above. Do NOT redact anything else.
-2. Leave ALL other information completely unchanged - including any types not listed above.
-3. DO NOT redact company names, organization names, or business names - leave them unchanged.
-4. DO NOT redact common nouns, generic terms, or non-sensitive information.
-5. Make sure each type is replaced with its EXACT placeholder shown above.
-6. Be precise: match each item to its correct type and use the exact placeholder for that type.
-7. If a type is not in the list above, it should NOT be redacted at all - leave it exactly as it appears in the original text.
-8. FOR ID NUMBERS: Redact ALL identification numbers including alphanumeric IDs with hyphens, prefixes like "Document ID:", "Verification ID:", "Reference ID:", etc. Examples: "HC-9920-ALPHA", "PASS-99283-TX", "Document ID: HC-9920-ALPHA", "Verification ID: PASS-99283-TX" - ALL should be redacted as ID numbers.

-Be thorough and catch all instances of the listed types. Return ONLY the redacted email content with no additional commentary or explanation.

-Email content to redact:
-{state.content}"""
        return f"""You are an email privacy protection tool. No redaction types are currently enabled, so return the email content exactly as-is without any modifications.

-Email content:
-{state.content}"""

    async def _process_images(self, state):
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


text_redactor = TextRedactor()

