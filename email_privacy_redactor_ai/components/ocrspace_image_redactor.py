import httpx
from PIL import Image, ImageDraw, ImageFont
import base64
from io import BytesIO
import os
import json
from dotenv import load_dotenv

# Load environment variables from .env file
# This ensures API keys are available when the module is imported
load_dotenv()


class CloudImageRedactor:
    """Redact sensitive information from images using OCR.space + AI"""
    
    def __init__(self, ocr_api_key: str = None, groq_api_key: str = None):
        """
        Initialize the cloud redactor
        
        Args:
            ocr_api_key: OCR.space API key (get free at https://ocr.space/ocrapi)
            groq_api_key: Groq API key (get free at https://console.groq.com)
        """
        self.ocr_api_key = ocr_api_key or os.getenv("OCRSPACE_API_KEY", "")
        self.groq_api_key = groq_api_key or os.getenv("GROQ_API_KEY", "")
        
        if not self.ocr_api_key:
            print("WARNING: OCRSPACE_API_KEY not set. Get free key at https://ocr.space/ocrapi")
        if not self.groq_api_key:
            print("WARNING: GROQ_API_KEY not set. Get free key at https://console.groq.com")
    
    async def extract_text_with_boxes(self, image_b64: str, state=None) -> list:
        """
        Extract text from image with bounding box coordinates using OCR.space
        
        Returns:
            List of dicts with 'text', 'x', 'y', 'width', 'height'
        """
        try:
            if state:
                state.append_feedback("🔍 OCR.space: Extracting text from image...")
            
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(
                    'https://api.ocr.space/parse/image',
                    data={
                        'apikey': self.ocr_api_key,
                        'base64Image': f'data:image/png;base64,{image_b64}',
                        'OCREngine': 2,  # Engine 2 is better for structured data
                        'scale': 'true',
                        'isTable': 'false',
                        'detectOrientation': 'true',
                    }
                )
                
                # Check if response is valid JSON
                try:
                    result = response.json()
                except Exception as json_error:
                    error_msg = f"Error parsing OCR.space response as JSON: {json_error}"
                    print(error_msg)
                    print(f"Response status: {response.status_code}")
                    print(f"Response text: {response.text[:200]}")
                    if state:
                        state.append_feedback(f"❌ OCR.space: {error_msg}")
                    return []
                
                # Check if result is a dict (not a string)
                if not isinstance(result, dict):
                    print(f"OCR.space API returned non-dict response: {type(result)}")
                    print(f"Response: {result}")
                    return []
                
                if not result.get('IsErroredOnProcessing'):
                    text_boxes = []
                    
                    # Parse OCR results
                    parsed_results = result.get('ParsedResults', [])
                    if parsed_results:
                        text_overlay = parsed_results[0].get('TextOverlay', {})
                        lines = text_overlay.get('Lines', [])
                        
                        for line in lines:
                            words = line.get('Words', [])
                            for word in words:
                                text = word.get('WordText', '').strip()
                                if text:
                                    text_boxes.append({
                                        'text': text,
                                        'x': word.get('Left', 0),
                                        'y': word.get('Top', 0),
                                        'width': word.get('Width', 0),
                                        'height': word.get('Height', 0),
                                    })
                    
                    if text_boxes:
                        if state:
                            state.append_feedback(f"✅ OCR.space: Found {len(text_boxes)} text elements")
                    else:
                        # No text found is a valid result, not an error
                        if state:
                            state.append_feedback("ℹ️ OCR.space: No text detected in image")
                    return text_boxes
                else:
                    error_msg = result.get('ErrorMessage', ['Unknown error'])
                    if isinstance(error_msg, list):
                        error_msg = error_msg[0] if error_msg else 'Unknown error'
                    elif not isinstance(error_msg, str):
                        error_msg = str(error_msg)
                    print(f"OCR.space API error: {error_msg}")
                    if state:
                        state.append_feedback(f"❌ OCR.space API error: {error_msg}")
                    return []
                    
        except Exception as e:
            error_msg = str(e) if e else "Unknown error"
            full_error = f"Error calling OCR.space API: {error_msg}"
            print(full_error)
            import traceback
            traceback.print_exc()
            if state:
                state.append_feedback(f"❌ OCR.space: {full_error}")
            return []
    
    async def identify_sensitive_text_with_ai(self, text_boxes: list, state=None) -> dict:
        """
        Use AI to identify which text boxes contain sensitive information
        
        Args:
            text_boxes: List of text boxes from OCR
            state: Optional state object to append feedback messages
            
        Returns:
            Dict mapping text to sensitivity type
        """
        if not text_boxes:
            return {}
        
        if state:
            state.append_feedback("🤖 Groq API: Analyzing text for sensitive information...")
        
        # Prepare text for AI analysis
        text_list = [f"{i}: {box['text']}" for i, box in enumerate(text_boxes)]
        all_text = "\n".join(text_list)
        
        # Build list of enabled types for image redaction
        enabled_types = []
        type_descriptions = []
        
        if state:
            if getattr(state, 'redact_name_enabled', True):
                enabled_types.append("name")
                type_descriptions.append("- name: Person's name (first name, last name, full name, or any part of a person's name) - NOT company names or organization names. IMPORTANT: If you see a first name, also classify the adjacent last name as 'name' even if it appears in a separate box.")
            if getattr(state, 'redact_email_enabled', True):
                enabled_types.append("email")
                type_descriptions.append("- email: Email address (anything with @ symbol)")
            if getattr(state, 'redact_phone_enabled', True):
                enabled_types.append("phone")
                type_descriptions.append("- phone: Phone number (any format)")
            if getattr(state, 'redact_address_enabled', True):
                enabled_types.append("address")
                type_descriptions.append("- address: Street address, city, state, zip code")
            if getattr(state, 'redact_ssn_enabled', True):
                enabled_types.append("ssn")
                type_descriptions.append("- ssn: Social Security Number")
            if getattr(state, 'redact_card_enabled', True):
                enabled_types.append("credit_card")
                type_descriptions.append(
                    "- credit_card: Credit card numbers and card details. "
                    "This includes full card numbers (like 1234 5678 9012 3456, 1234-5678-9012-3456, 1234567890123456) "
                    "AND masked card formats like 'Visa **** 9901', '**** 9901', or similar. "
                    "Treat the card brand (e.g., 'Visa'), the masked section (****), and the last 4 digits together as credit_card "
                    "so the ENTIRE card reference is redacted, not just part of it."
                )
            if getattr(state, 'redact_key_enabled', True):
                enabled_types.append("api_key")
                type_descriptions.append("- api_key: API keys")
            if getattr(state, 'redact_password_enabled', True):
                enabled_types.append("password")
                type_descriptions.append("- password: Passwords, passcodes, or password values (the actual password text, not just the word 'Password' label)")
            if getattr(state, 'redact_token_enabled', True):
                enabled_types.append("token")
                type_descriptions.append("- token: Tokens (the actual token values, NOT the word 'Token' label itself). Look for token values that appear next to, below, or after labels like 'Token:', 'Access Token:', 'API Token:', 'Authentication Token:', etc. Tokens can be long alphanumeric strings, JWT tokens (often starting with 'eyJ'), API tokens, session tokens, etc.")
            if getattr(state, 'redact_id_enabled', True):
                enabled_types.append("id")
                type_descriptions.append("- id: Identification numbers (user IDs, employee IDs, customer IDs, document IDs, verification IDs, any alphanumeric IDs with or without hyphens like 'HC-9920-ALPHA', 'PASS-99283-TX') - NOT company names. CRITICAL: Look for ID patterns like 'HC-9920-ALPHA' or 'PASS-99283-TX' (letters, numbers, hyphens) even when they appear in separate text boxes from labels like 'Document ID:', 'Verification ID:', 'Reference ID:'. If you see a label like 'Document ID:' in one box and 'HC-9920-ALPHA' in the next box, classify 'HC-9920-ALPHA' as id. If the entire text box contains 'Document ID: HC-9920-ALPHA' together, classify the WHOLE box as id.")
            if getattr(state, 'redact_dollar_enabled', True):
                enabled_types.append("dollar")
                type_descriptions.append("- dollar: Dollar amounts, prices, salaries")
            if getattr(state, 'redact_account_enabled', True):
                enabled_types.append("account")
                type_descriptions.append("- account: Account numbers, bank account numbers")
        
        # If no types enabled, return empty dict
        if not enabled_types:
            return {}
        
        type_list = "\n".join(type_descriptions)
        
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(
                    "https://api.groq.com/openai/v1/chat/completions",
                    headers={
                        "Content-Type": "application/json",
                        "Authorization": f"Bearer {self.groq_api_key}",
                    },
                    json={
                        "model": "llama-3.3-70b-versatile",
                        "messages": [{
                            "role": "user",
                            "content": f"""Analyze the following text extracted from an image via OCR. Identify which items contain sensitive information that should be redacted.

For each line number that contains sensitive information, classify it as one of these types ONLY:
{type_list}

CRITICAL RULES:
1. ONLY classify the types listed above. Do NOT classify anything else as sensitive.
2. If a type is NOT in the list above, do NOT classify anything as that type, even if it looks similar.
3. DO NOT classify ID numbers, user IDs, employee IDs, customer IDs, or any identification numbers unless "id" is explicitly listed above. If "id" is not listed, leave all ID numbers UNCLASSIFIED (do not include them in your response).
4. DO NOT classify company names, organization names, or business names - they should NOT be in the response.
5. Make precise classifications: names go as "name", emails go as "email", addresses go as "address", etc.
6. DO NOT confuse types: names should be "name" NOT "id", emails should be "email" NOT "address", ID numbers should NOT be classified as "address" or any other type if "id" is not listed.
7. Physical addresses (street addresses) are different from ID numbers - do NOT misclassify ID numbers as addresses.
8. Common nouns and generic terms are NOT sensitive information.
9. If unsure whether something matches a type in the list, do NOT include it in your response - only include items you are certain match the listed types.
10. FOR NAMES: If "name" is in the list above, be thorough - classify BOTH first names AND last names as "name". If you see a first name (like "John", "Mary", "Robert"), also look for and classify the adjacent last name (like "Smith", "Johnson", "Williams") as "name" even if they appear in separate boxes. Look for patterns like "First Last", "Last, First", or names on adjacent lines.
11. FOR PASSWORDS: If "password" is in the list above, classify the ACTUAL PASSWORD VALUES, NOT the label "Password" itself. Look for password values that appear next to, after, or in parentheses after labels like "Password:", "Pass:", "PWD:", or the word "Password". Examples: "Password (Secure!Health99)" - classify "Secure!Health99" as password, NOT the word "Password". Password values can be alphanumeric strings with special characters. DO NOT classify the word "Password" or labels like "Password:" as sensitive if they're just labels - only classify the actual password values.
12. FOR TOKENS: If "token" is in the list above, classify the ACTUAL TOKEN VALUES, NOT the label "Token" itself. Look for token values that appear next to, below, or after labels like "Token:", "Access Token:", "API Token:", "Authentication Token:", etc. Examples: "Authentication Token: eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..." - classify "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..." as token, NOT the label "Authentication Token:". Tokens can be long alphanumeric strings, JWT tokens (often starting with "eyJ"), API tokens, session tokens, etc. DO NOT classify the word "Token" or labels like "Authentication Token:" as sensitive if they're just labels - only classify the actual token values. Be thorough - if you see "Token:" on one line and the actual token on the next line, classify the token line, not the "Token:" label line. If a token appears on the same line after a colon, classify only the token part, not the label.
13. FOR CREDIT CARDS: If "credit_card" is in the list above, classify ANY card-related sensitive text. This includes: full card numbers (any format with spaces, hyphens, or no separators), AND masked card formats like "Visa **** 9901", "**** 9901", or similar. When you see a pattern like "Backup Payment Card: Visa **** 9901", classify the parts "Visa", "****", and "9901" as credit_card (do NOT classify the label words like "Backup Payment Card:"). The goal is to ensure the entire card reference is redacted, not just the middle digits or only the number - the brand + masked section + last 4 digits together should all be classified as credit_card.
14. FOR IDs: If "id" is in the list above, be thorough with IDs that have prefixes. IMPORTANT: 
    - If a text box contains BOTH a label AND an ID value together (like "Document ID: HC-9920-ALPHA" in one box), classify the ENTIRE box as "id".
    - If the label and value are in SEPARATE boxes (e.g., one box says "Document ID:" and the next box says "HC-9920-ALPHA"), classify the VALUE box (the one with "HC-9920-ALPHA") as "id".
    - CRITICAL: Look for ID patterns even when separated. If you see a line with "Document ID:", "Verification ID:", "Reference ID:", "ID:", etc., and the NEXT line or nearby line contains an alphanumeric pattern with hyphens (like "HC-9920-ALPHA", "PASS-99283-TX", or similar patterns like "ABC-1234-XYZ"), classify that alphanumeric pattern as "id".
    - Also recognize standalone ID patterns: Any text matching patterns like "XX-####-XXX" (letters, numbers, hyphens) or similar alphanumeric-hyphenated formats should be classified as "id" if they appear in context suggesting they are IDs (near labels like "ID:", "Document ID:", etc., or standalone if they match the pattern).
    - Examples from the text to analyze: 
      * If you see "0: Document" and "1: ID:" and "2: HC-9920-ALPHA" → classify line "2" as id
      * If you see "5: Document ID: HC-9920-ALPHA" (all in one line) → classify line "5" as id
      * If you see "10: HC-9920-ALPHA" (standalone but matches ID pattern) → classify line "10" as id
    - IDs can be alphanumeric with hyphens (like "HC-9920-ALPHA" or "PASS-99283-TX"). Be thorough - recognize these patterns and classify them as id.
15. FOR ADDRESSES: If "address" is in the list above, classify the ACTUAL ADDRESS VALUES, NOT the label itself. Examples: "Residential Address: 1202 Maplewood Drive, Austin, TX 78701" - classify "1202 Maplewood Drive, Austin, TX 78701" as address, NOT the label "Residential Address:". DO NOT classify address labels like "Residential Address:", "Mailing Address:", "Home Address:", etc. as sensitive - only classify the actual street addresses, cities, states, and zip codes that follow these labels.

Text to analyze:
{all_text}

Respond with ONLY a valid JSON object in this exact format:
{{
  "0": "name",
  "5": "email",
  "12": "phone"
}}

Include ONLY the line numbers that contain sensitive information matching the types above. If a line has no sensitive info, don't include it.
Do NOT include any explanation, markdown formatting, or additional text - ONLY the JSON object."""
                        }],
                        "temperature": 0.1,
                    }
                )
                
                data = response.json()
                ai_response = data.get("choices", [{}])[0].get("message", {}).get("content", "{}")
                
                # Clean up response - remove markdown code blocks if present
                ai_response = ai_response.strip()
                if ai_response.startswith("```"):
                    # Remove markdown code block markers
                    lines = ai_response.split("\n")
                    ai_response = "\n".join(lines[1:-1]) if len(lines) > 2 else ai_response
                ai_response = ai_response.replace("```json", "").replace("```", "").strip()
                
                # Parse JSON response
                sensitivity_map = json.loads(ai_response)
                
                # Convert string indices to integers
                sensitivity_map = {int(k): v for k, v in sensitivity_map.items()}
                
                print(f"AI identified {len(sensitivity_map)} sensitive items")
                if state:
                    state.append_feedback(f"✅ Groq API: Identified {len(sensitivity_map)} sensitive item(s)")
                    for idx, redaction_type in list(sensitivity_map.items())[:5]:  # Show first 5
                        if idx < len(text_boxes):
                            state.append_feedback(f"   • {redaction_type}: '{text_boxes[idx]['text']}'")
                    if len(sensitivity_map) > 5:
                        state.append_feedback(f"   ... and {len(sensitivity_map) - 5} more")
                
                return sensitivity_map
                
        except Exception as e:
                error_msg = f"Error calling AI for sensitivity detection: {e}"
                print(error_msg)
                import traceback
                traceback.print_exc()
                if state:
                    state.append_feedback(f"❌ Groq API: {error_msg}")
                return {}
    
    def merge_adjacent_boxes(self, boxes: list, max_distance: int = 20) -> list:
        """
        Merge text boxes that are close together (same line)
        """
        if not boxes:
            return []
        
        # Sort boxes by position (top to bottom, left to right)
        sorted_boxes = sorted(boxes, key=lambda b: (b['y'], b['x']))
        
        merged = []
        current_line = [sorted_boxes[0]]
        
        for box in sorted_boxes[1:]:
            prev_box = current_line[-1]
            
            # Check if boxes are on the same line (similar y-coordinate)
            y_diff = abs(box['y'] - prev_box['y'])
            x_distance = box['x'] - (prev_box['x'] + prev_box['width'])
            
            if y_diff < prev_box['height'] * 0.5 and 0 <= x_distance < max_distance:
                current_line.append(box)
            else:
                # Merge current line and start new one
                if current_line:
                    merged.append(self._merge_box_group(current_line))
                current_line = [box]
        
        # Don't forget the last line
        if current_line:
            merged.append(self._merge_box_group(current_line))
        
        return merged
    
    def _merge_box_group(self, boxes: list) -> dict:
        """Merge a group of boxes into one"""
        if len(boxes) == 1:
            return boxes[0]
        
        min_x = min(b['x'] for b in boxes)
        min_y = min(b['y'] for b in boxes)
        max_x = max(b['x'] + b['width'] for b in boxes)
        max_y = max(b['y'] + b['height'] for b in boxes)
        
        # Preserve redaction_type from the first box (all should have the same type)
        merged_box = {
            'text': ' '.join(b['text'] for b in boxes),
            'x': min_x,
            'y': min_y,
            'width': max_x - min_x,
            'height': max_y - min_y,
            'indices': [boxes.index(b) for b in boxes] if hasattr(boxes[0], 'index') else []
        }
        
        # Preserve redaction_type if it exists
        if 'redaction_type' in boxes[0]:
            merged_box['redaction_type'] = boxes[0]['redaction_type']
        
        return merged_box
    
    async def find_sensitive_boxes(self, text_boxes: list, state=None) -> list:
        """
        Find all text boxes that contain sensitive information using AI
        
        Returns:
            List of boxes with sensitive info and their types
        """
        # Use AI to identify sensitive information on individual word boxes
        sensitivity_map = await self.identify_sensitive_text_with_ai(text_boxes, state)
        
        # Create mapping of redaction types to enabled state
        type_to_enabled = {}
        if state:
            type_to_enabled = {
                'name': getattr(state, 'redact_name_enabled', True),
                'email': getattr(state, 'redact_email_enabled', True),
                'phone': getattr(state, 'redact_phone_enabled', True),
                'address': getattr(state, 'redact_address_enabled', True),
                'ssn': getattr(state, 'redact_ssn_enabled', True),
                'credit_card': getattr(state, 'redact_card_enabled', True),
                'api_key': getattr(state, 'redact_key_enabled', True),
                'password': getattr(state, 'redact_password_enabled', True),
                'token': getattr(state, 'redact_token_enabled', True),
                'id': getattr(state, 'redact_id_enabled', True),
                'dollar': getattr(state, 'redact_dollar_enabled', True),
                'account': getattr(state, 'redact_account_enabled', True),
            }
        else:
            # Default to all enabled if no state provided
            type_to_enabled = {
                'name': True, 'email': True, 'phone': True, 'address': True,
                'ssn': True, 'credit_card': True, 'api_key': True, 'password': True,
                'token': True, 'id': True, 'dollar': True, 'account': True,
            }
        
        sensitive_boxes = []
        
        # Only use individual word boxes - this gives precise word-level redaction
        # Filter based on checkbox enabled states
        for idx, box in enumerate(text_boxes):
            if idx in sensitivity_map:
                redaction_type = sensitivity_map[idx]
                # Only include if this type is enabled
                if type_to_enabled.get(redaction_type, True):
                    sensitive_boxes.append({
                        **box,
                        'redaction_type': redaction_type
                    })
        
        # Optionally merge adjacent sensitive boxes of the same type for better visual appearance
        # but only merge boxes that are very close together (e.g., phone numbers split across boxes)
        sensitive_boxes = self._merge_adjacent_sensitive_boxes(sensitive_boxes)
        
        return sensitive_boxes
    
    def _merge_adjacent_sensitive_boxes(self, boxes: list) -> list:
        """
        Merge only adjacent sensitive boxes that are very close together
        This helps with cases like phone numbers that might be split into multiple boxes
        """
        if not boxes:
            return []
        
        # Sort boxes by position
        sorted_boxes = sorted(boxes, key=lambda b: (b['y'], b['x']))
        merged = []
        current_group = [sorted_boxes[0]]
        
        for box in sorted_boxes[1:]:
            prev_box = current_group[-1]
            
            # Check if boxes are on the same line
            y_diff = abs(box['y'] - prev_box['y'])
            x_distance = box['x'] - (prev_box['x'] + prev_box['width'])
            
            # Use dynamic max_distance based on redaction type
            # Names can have larger spacing between first and last name
            redaction_type = prev_box.get('redaction_type', 'other')
            if redaction_type == 'name':
                max_distance = 100  # Much larger distance for names (first/last name spacing can be wide)
            elif redaction_type in ['phone', 'credit_card']:
                max_distance = 15  # Medium distance for numbers that might be split
            else:
                max_distance = 30  # Default distance for other types
            
            # Check if boxes are close together and of the same type
            # Allow some gap between boxes on the same line
            if (y_diff < prev_box['height'] * 0.6 and  # Same line (more lenient y-check)
                0 <= x_distance < max_distance and  # Within max distance
                box.get('redaction_type') == prev_box.get('redaction_type')):  # Same type
                current_group.append(box)
            else:
                # Merge current group and start new one
                if len(current_group) == 1:
                    merged.append(current_group[0])
                else:
                    merged.append(self._merge_box_group(current_group))
                current_group = [box]
        
        # Don't forget the last group
        if len(current_group) == 1:
            merged.append(current_group[0])
        else:
            merged.append(self._merge_box_group(current_group))
        
        return merged
    
    def draw_redaction_boxes(self, image: Image.Image, sensitive_boxes: list, 
                            show_labels: bool = True, state=None) -> Image.Image:
        """
        Draw black redaction boxes over sensitive information
        
        Args:
            image: PIL Image
            sensitive_boxes: List of boxes to redact
            show_labels: Whether to show redaction type labels
            state: Optional state object to get custom redaction placeholders
        
        Returns:
            Redacted PIL Image
        """
        # Create a copy to avoid modifying original
        img_copy = image.copy()
        draw = ImageDraw.Draw(img_copy)
        
        # Try to load a font
        try:
            font = ImageFont.truetype("arial.ttf", 14)
        except:
            try:
                font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 14)
            except:
                font = ImageFont.load_default()
        
        # Use custom placeholders from state if available, otherwise use defaults
        if state:
            # Safely access state attributes with getattr to handle Reflex state wrapping
            try:
                labels = {
                    'name': getattr(state, 'redact_name', '[NAME]'),
                    'email': getattr(state, 'redact_email', '[EMAIL]'),
                    'phone': getattr(state, 'redact_phone', '[PHONE]'),
                    'ssn': getattr(state, 'redact_ssn', '[SSN]'),
                    'credit_card': getattr(state, 'redact_card', '[CC CARD]'),
                    'address': getattr(state, 'redact_address', '[ADDRESS]'),
                    'dollar': getattr(state, 'redact_dollar', '[$]'),
                    'api_key': getattr(state, 'redact_key', '[KEY]'),
                    'account': getattr(state, 'redact_account', '[ACCOUNT]'),
                    'token': getattr(state, 'redact_token', '[TOKEN]'),
                    'id': getattr(state, 'redact_id', '[ID]'),
                    'password': getattr(state, 'redact_password', '[PASS]'),
                }
            except (AttributeError, TypeError) as e:
                # If accessing state fails, fall back to defaults
                print(f"Warning: Could not access state redaction placeholders: {e}")
                labels = {
                    'name': '[NAME]',
                    'email': '[EMAIL]',
                    'phone': '[PHONE]',
                    'ssn': '[SSN]',
                    'credit_card': '[CC CARD]',
                    'address': '[ADDRESS]',
                    'dollar': '[$]',
                    'api_key': '[KEY]',
                    'account': '[ACCOUNT]',
                    'token': '[TOKEN]',
                    'id': '[ID]',
                    'password': '[PASS]',
                }
        else:
            labels = {
                'name': '[NAME]',
                'email': '[EMAIL]',
                'phone': '[PHONE]',
                'ssn': '[SSN]',
                'credit_card': '[CC CARD]',
                'address': '[ADDRESS]',
                'dollar': '[$]',
                'api_key': '[KEY]',
                'account': '[ACCOUNT]',
                'token': '[TOKEN]',
                'id': '[ID]',
                'password': '[PASS]',
            }
        
        for box in sensitive_boxes:
            x, y, w, h = box['x'], box['y'], box['width'], box['height']
            redaction_type = box.get('redaction_type', 'other')
            
            # Add minimal padding to ensure text is fully covered
            padding = 2
            x1 = max(0, x - padding)
            y1 = max(0, y - padding)
            x2 = x + w + padding
            y2 = y + h + padding
            
            # Draw black rectangle
            draw.rectangle([x1, y1, x2, y2], fill=(0, 0, 0))
            
            # Draw label if requested
            if show_labels and w > 40:  # Only show label if box is wide enough
                label = labels.get(redaction_type, '[REDACTED]')
                
                # Get text size for centering
                bbox = draw.textbbox((0, 0), label, font=font)
                text_width = bbox[2] - bbox[0]
                text_height = bbox[3] - bbox[1]
                
                # Center label in box
                label_x = x1 + (x2 - x1 - text_width) / 2
                label_y = y1 + (y2 - y1 - text_height) / 2
                
                # Draw white text
                draw.text((label_x, label_y), label, fill=(255, 255, 255), font=font)
        
        return img_copy
    
    async def redact_image_from_base64(self, image_b64: str, state=None) -> str:
        """
        Complete redaction pipeline for base64 encoded image
        
        Args:
            image_b64: Base64 encoded image string
            state: Optional state object to append feedback messages
        
        Returns:
            Base64 encoded redacted image
        """
        try:
            # Decode base64 to image
            image_data = base64.b64decode(image_b64)
            image = Image.open(BytesIO(image_data))
            
            # Convert to RGB if needed
            if image.mode != 'RGB':
                image = image.convert('RGB')
            
            # Extract text with bounding boxes using OCR.space
            text_boxes = await self.extract_text_with_boxes(image_b64, state)
            
            if not text_boxes:
                if state:
                    state.append_feedback("ℹ️ No text detected in image")
                print("No text detected in image")
                return image_b64
            
            print(f"Detected {len(text_boxes)} text boxes")
            
            # Find sensitive information using AI
            sensitive_boxes = await self.find_sensitive_boxes(text_boxes, state)
            
            print(f"Found {len(sensitive_boxes)} sensitive items")
            
            if not sensitive_boxes:
                if state:
                    state.append_feedback("ℹ️ No sensitive information detected in image")
                print("No sensitive information detected")
                return image_b64
            
            if state:
                state.append_feedback(f"🎨 Drawing redaction boxes over {len(sensitive_boxes)} sensitive area(s)...")
            
            # Draw redaction boxes (pass state for custom labels)
            redacted_image = self.draw_redaction_boxes(image, sensitive_boxes, state=state)
            
            # Convert back to base64
            buffered = BytesIO()
            redacted_image.save(buffered, format="PNG")
            redacted_b64 = base64.b64encode(buffered.getvalue()).decode()
            
            if state:
                state.append_feedback("✅ Image redaction complete")
            
            return redacted_b64
            
        except Exception as e:
            print(f"Error redacting image: {e}")
            import traceback
            traceback.print_exc()
            return image_b64  # Return original if redaction fails


# Create a global instance for convenience
_redactor = CloudImageRedactor()

# Standalone function for backward compatibility
async def redact_image(image_b64: str, state=None) -> str:
    """
    Redact sensitive info from image using OCR.space API
    This is a wrapper around CloudImageRedactor for backward compatibility
    
    Args:
        image_b64: Base64 encoded image string
        state: Optional state object to append feedback messages
        
    Returns:
        Base64 encoded redacted image string
    """
    return await _redactor.redact_image_from_base64(image_b64, state)

