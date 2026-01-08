import reflex as rx
from email_privacy_redactor_ai.components.image_file_handler import handle_image_upload as _handle_image_upload, remove_image as _remove_image
from email_privacy_redactor_ai.components.ocrspace_image_redactor import redact_image as _redact_image
from email_privacy_redactor_ai.components.text_redactor import redact_text as _redact_text
from email_privacy_redactor_ai.components.email_sender import send_email as _send_email


class EmailPrivacyRedactorAI(rx.State):
    # Form fields
    to_email: str = ""
    cc_email: str = ""
    subject: str = ""
    content: str = ""
    
    # Validation errors
    to_email_error: str = ""
    cc_email_error: str = ""
    image_upload_error: str = ""
    
    # Image handling
    uploaded_images: list[str] = []  # Base64 encoded images
    redacted_images: list[str] = []  # Base64 encoded redacted images
    
    # State management
    step: str = "compose"  # 'compose', 'preview', 'sent'
    loading: bool = False
    redacted_content: str = ""
    selected_image_index: int = -1  # -1 means no image selected for modal
    ai_feedback: str = ""  # Feedback from Groq and OCR.space APIs
    show_comparison_modal: bool = False  # Whether to show content comparison modal
    show_test_files_menu: bool = False  # Whether to show test files dropdown menu
    available_test_files: list[str] = []  # List of available test file names
    available_test_images: list[str] = []  # List of available test image file names
    selected_test_images: list[str] = []  # List of selected test image file names
    show_test_images_menu: bool = False  # Whether to show test images dropdown menu
    
    # Store original data for back button
    original_to: str = ""
    original_cc: str = ""
    original_subject: str = ""
    original_content: str = ""
    original_images: list[str] = []
    
    # Redaction placeholder settings (editable by user)
    redact_name: str = "[NAME]"
    redact_email: str = "[EMAIL]"
    redact_phone: str = "[PHONE]"
    redact_address: str = "[ADDRESS]"
    redact_ssn: str = "[SSN]"
    redact_card: str = "[CC CARD]"
    redact_key: str = "[KEY]"
    redact_password: str = "[PASS]"
    redact_token: str = "[TOKEN]"
    redact_id: str = "[ID]"
    redact_dollar: str = "[$]"
    redact_account: str = "[ACCOUNT]"
    
    # Checkbox states for enabling/disabling redaction (all checked by default)
    redact_name_enabled: bool = True
    redact_email_enabled: bool = True
    redact_phone_enabled: bool = True
    redact_address_enabled: bool = True
    redact_ssn_enabled: bool = True
    redact_card_enabled: bool = True
    redact_key_enabled: bool = True
    redact_password_enabled: bool = True
    redact_token_enabled: bool = True
    redact_id_enabled: bool = True
    redact_dollar_enabled: bool = True
    redact_account_enabled: bool = True
    
    def set_redact_name(self, value: str):
        self.redact_name = value
    
    def set_redact_email(self, value: str):
        self.redact_email = value
    
    def set_redact_phone(self, value: str):
        self.redact_phone = value
    
    def set_redact_address(self, value: str):
        self.redact_address = value
    
    def set_redact_ssn(self, value: str):
        self.redact_ssn = value
    
    def set_redact_card(self, value: str):
        self.redact_card = value
    
    def set_redact_key(self, value: str):
        self.redact_key = value
    
    def set_redact_password(self, value: str):
        self.redact_password = value
    
    def set_redact_token(self, value: str):
        self.redact_token = value
    
    def set_redact_id(self, value: str):
        self.redact_id = value
    
    def set_redact_dollar(self, value: str):
        self.redact_dollar = value
    
    def set_redact_account(self, value: str):
        self.redact_account = value
    
    # Checkbox setters
    def set_redact_name_enabled(self, value: bool):
        self.redact_name_enabled = value
    
    def set_redact_email_enabled(self, value: bool):
        self.redact_email_enabled = value
    
    def set_redact_phone_enabled(self, value: bool):
        self.redact_phone_enabled = value
    
    def set_redact_address_enabled(self, value: bool):
        self.redact_address_enabled = value
    
    def set_redact_ssn_enabled(self, value: bool):
        self.redact_ssn_enabled = value
    
    def set_redact_card_enabled(self, value: bool):
        self.redact_card_enabled = value
    
    def set_redact_key_enabled(self, value: bool):
        self.redact_key_enabled = value
    
    def set_redact_password_enabled(self, value: bool):
        self.redact_password_enabled = value
    
    def set_redact_token_enabled(self, value: bool):
        self.redact_token_enabled = value
    
    def set_redact_id_enabled(self, value: bool):
        self.redact_id_enabled = value
    
    def set_redact_dollar_enabled(self, value: bool):
        self.redact_dollar_enabled = value
    
    def set_redact_account_enabled(self, value: bool):
        self.redact_account_enabled = value
    
    def set_to_email(self, value: str):
        """Set to_email and clear error when user types"""
        self.to_email = value
        self.to_email_error = ""
    
    def set_cc_email(self, value: str):
        """Set cc_email and clear error when user types"""
        self.cc_email = value
        self.cc_email_error = ""
    
    async def handle_image_upload(self, files: list[rx.UploadFile]):
        """Handle image uploads with validation"""
        # Clear previous error
        self.image_upload_error = ""
        yield
        
        # Check max number of images (4 total)
        current_count = len(self.uploaded_images)
        new_count = len(files)
        total_count = current_count + new_count
        
        if total_count > 4:
            self.image_upload_error = f"Maximum 4 images allowed. You have {current_count} image(s) and tried to upload {new_count} more."
            return
        
        # Check total size (5 MB = 5 * 1024 * 1024 bytes)
        MAX_SIZE_BYTES = 5 * 1024 * 1024  # 5 MB
        
        # Calculate current total size from base64 images
        # Base64 encoding increases size by ~33%, so original ≈ base64_size * 3/4
        current_total_size = 0
        for img_b64 in self.uploaded_images:
            # Estimate original size from base64 (base64 is ~4/3 of original)
            current_total_size += len(img_b64.encode('utf-8')) * 3 // 4
        
        # Calculate new files size
        new_total_size = 0
        for file in files:
            upload_data = await file.read()
            file_size = len(upload_data)
            new_total_size += file_size
            # Reset file pointer for later processing
            await file.seek(0)
        
        total_size = current_total_size + new_total_size
        
        if total_size > MAX_SIZE_BYTES:
            current_mb = current_total_size / (1024 * 1024)
            new_mb = new_total_size / (1024 * 1024)
            total_mb = total_size / (1024 * 1024)
            self.image_upload_error = f"Maximum 5 MB total size allowed. Current: {current_mb:.2f} MB, New upload: {new_mb:.2f} MB, Total: {total_mb:.2f} MB."
            return
        
        # If validation passes, proceed with upload
        await _handle_image_upload(self, files)
    
    def remove_image(self, index: int):
        """Remove an uploaded image"""
        _remove_image(self, index)
        # Clear error when image is removed
        self.image_upload_error = ""
    
    async def redact_image(self, image_b64: str) -> str:
        """Redact sensitive info from image using OCR + text redaction"""
        return await _redact_image(image_b64)
    
    def validate_emails(self, email_string: str) -> tuple[bool, str]:
        """
        Validate email addresses separated by comma or semicolon
        
        Args:
            email_string: String containing email addresses separated by ',' or ';'
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        if not email_string or not email_string.strip():
            return True, ""  # Empty is allowed (for CC)
        
        import re
        # Email regex pattern
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        
        # Split by comma or semicolon
        emails = re.split(r'[,;]', email_string)
        invalid_emails = []
        
        for email in emails:
            email = email.strip()
            if email:  # Skip empty strings
                if not re.match(email_pattern, email):
                    invalid_emails.append(email)
        
        if invalid_emails:
            return False, f"Invalid email address(es): {', '.join(invalid_emails)}"
        
        return True, ""
    
    async def redact_text(self):
        """Call Groq API to redact sensitive information with email validation"""
        # Clear previous errors
        self.to_email_error = ""
        self.cc_email_error = ""
        yield
        
        # Validate To email (required)
        if not self.to_email or not self.to_email.strip():
            self.to_email_error = "To email is required"
            return
        
        to_valid, to_error = self.validate_emails(self.to_email)
        if not to_valid:
            self.to_email_error = to_error
            return
        
        # Validate CC email (optional)
        if self.cc_email and self.cc_email.strip():
            cc_valid, cc_error = self.validate_emails(self.cc_email)
            if not cc_valid:
                self.cc_email_error = cc_error
                return
        
        # If validation passes, proceed with redaction
        async for _ in _redact_text(self):
            yield
    
    def handle_back(self):
        """Return to compose screen with original data intact"""
        self.to_email = self.original_to
        self.cc_email = self.original_cc
        self.subject = self.original_subject
        self.content = self.original_content
        self.uploaded_images = self.original_images.copy()
        self.to_email_error = ""
        self.cc_email_error = ""
        self.step = "compose"
    
    
    async def send_email(self):
        """Send the redacted email"""
        await _send_email(self)
    
    @rx.var
    def selected_image(self) -> str:
        """Get the currently selected image for the modal"""
        if self.selected_image_index >= 0 and self.selected_image_index < len(self.redacted_images):
            return self.redacted_images[self.selected_image_index]
        return ""
    
    def open_image_modal(self, index: int):
        """Open modal to view image at index"""
        self.selected_image_index = index
    
    def close_image_modal(self):
        """Close the image modal"""
        self.selected_image_index = -1
    
    def open_comparison_modal(self):
        """Open the content comparison modal"""
        self.show_comparison_modal = True
    
    def close_comparison_modal(self):
        """Close the content comparison modal"""
        self.show_comparison_modal = False
    
    def handle_test_menu_open_change(self, is_open: bool):
        """Handle test files menu open/close"""
        if is_open:
            # Load available test files when opening menu
            self.load_available_test_files()
    
    def handle_test_images_menu_open_change(self, is_open: bool):
        """Handle test images menu open/close"""
        self.show_test_images_menu = is_open
        if is_open:
            # Load available test images when opening menu
            self.load_available_test_images()
    
    def load_available_test_files(self):
        """Load list of available test files from assets folder"""
        import os
        # Get the assets folder path - __file__ is email_privacy_redactor_ai.py
        current_dir = os.path.dirname(__file__)
        assets_path = os.path.join(current_dir, "assets")
        test_files = []
        
        if os.path.exists(assets_path):
            for filename in os.listdir(assets_path):
                if filename.endswith("_Test.txt") and not filename.startswith("."):
                    test_files.append(filename)
        
        # Sort files alphabetically
        test_files.sort()
        self.available_test_files = test_files
    
    def load_test_file_content(self, filename: str):
        """Load content from a test file"""
        import os
        # Get the assets folder path - __file__ is email_privacy_redactor_ai.py
        current_dir = os.path.dirname(__file__)
        assets_path = os.path.join(current_dir, "assets")
        file_path = os.path.join(assets_path, filename)
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                file_content = f.read()
            self.content = file_content
            self.show_test_files_menu = False
        except Exception as e:
            print(f"Error loading test file {filename}: {e}")
            self.show_test_files_menu = False
    
    def load_test_file_by_index(self, index: int):
        """Load test file content by index in available_test_files list"""
        if 0 <= index < len(self.available_test_files):
            filename = self.available_test_files[index]
            self.load_test_file_content(filename)
    
    def format_test_file_name(self, filename: str) -> str:
        """Format test file name for display (remove _Test.txt and underscores)"""
        # Remove _Test.txt suffix
        name = filename.replace("_Test.txt", "")
        # Replace underscores with spaces
        name = name.replace("_", " ")
        return name
    
    def get_formatted_test_file_name(self, index: int) -> str:
        """Get formatted test file name by index"""
        if 0 <= index < len(self.available_test_files):
            filename = self.available_test_files[index]
            return self.format_test_file_name(filename)
        return ""
    
    def load_available_test_images(self):
        """Load list of available test images from assets folder"""
        import os
        current_dir = os.path.dirname(__file__)
        assets_path = os.path.join(current_dir, "assets")
        test_images = []
        
        if os.path.exists(assets_path):
            for filename in os.listdir(assets_path):
                if filename.endswith("_Test.jpg") and not filename.startswith("."):
                    test_images.append(filename)
        
        # Sort files alphabetically
        test_images.sort()
        self.available_test_images = test_images
    
    def toggle_test_image_selection(self, filename: str):
        """Toggle selection of a test image"""
        if filename in self.selected_test_images:
            self.selected_test_images.remove(filename)
        else:
            self.selected_test_images.append(filename)
    
    def toggle_test_image_selection_by_index(self, index: int):
        """Toggle selection of a test image by index"""
        if 0 <= index < len(self.available_test_images):
            filename = self.available_test_images[index]
            self.toggle_test_image_selection(filename)
    
    def is_test_image_selected_by_index(self, index: int) -> bool:
        """Check if a test image is selected by index"""
        if 0 <= index < len(self.available_test_images):
            filename = self.available_test_images[index]
            return filename in self.selected_test_images
        return False
    
    def get_formatted_test_image_name(self, index: int) -> str:
        """Get formatted test image name by index"""
        if 0 <= index < len(self.available_test_images):
            filename = self.available_test_images[index]
            return self.format_test_image_name(filename)
        return ""
    
    def upload_selected_test_images(self):
        """Upload all selected test images"""
        import os
        import base64
        
        current_dir = os.path.dirname(__file__)
        assets_path = os.path.join(current_dir, "assets")
        
        for filename in self.selected_test_images:
            file_path = os.path.join(assets_path, filename)
            try:
                with open(file_path, 'rb') as f:
                    image_data = f.read()
                    # Convert to base64
                    base64_image = base64.b64encode(image_data).decode('utf-8')
                    self.uploaded_images.append(base64_image)
            except Exception as e:
                print(f"Error loading test image {filename}: {e}")
        
        # Clear selections after upload and close menu
        self.selected_test_images = []
        self.show_test_images_menu = False
    
    def format_test_image_name(self, filename: str) -> str:
        """Format test image name for display (remove _Test.jpg and underscores)"""
        # Remove _Test.jpg suffix
        name = filename.replace("_Test.jpg", "")
        # Replace underscores with spaces
        name = name.replace("_", " ")
        return name
    
    def is_test_image_selected(self, filename: str) -> bool:
        """Check if a test image is selected"""
        return filename in self.selected_test_images
    
    def handle_new_email(self):
        """Reset form for new email"""
        self.to_email = ""
        self.cc_email = ""
        self.subject = ""
        self.content = ""
        self.to_email_error = ""
        self.cc_email_error = ""
        self.uploaded_images = []
        self.redacted_images = []
        self.redacted_content = ""
        self.original_to = ""
        self.original_cc = ""
        self.original_subject = ""
        self.original_content = ""
        self.original_images = []
        self.selected_image_index = -1
        self.ai_feedback = ""
        self.show_comparison_modal = False
        # Reset redaction placeholders to defaults
        self.redact_name = "[NAME]"
        self.redact_email = "[EMAIL]"
        self.redact_phone = "[PHONE]"
        self.redact_address = "[ADDRESS]"
        self.redact_ssn = "[SSN]"
        self.redact_card = "[CC CARD]"
        self.redact_key = "[KEY]"
        self.redact_password = "[PASS]"
        self.redact_token = "[TOKEN]"
        self.redact_id = "[ID]"
        self.redact_dollar = "[$]"
        self.redact_account = "[ACCOUNT]"
        # Reset checkbox states to checked
        self.redact_name_enabled = True
        self.redact_email_enabled = True
        self.redact_phone_enabled = True
        self.redact_address_enabled = True
        self.redact_ssn_enabled = True
        self.redact_card_enabled = True
        self.redact_key_enabled = True
        self.redact_password_enabled = True
        self.redact_token_enabled = True
        self.redact_id_enabled = True
        self.redact_dollar_enabled = True
        self.redact_account_enabled = True
        self.image_upload_error = ""
        self.selected_test_images = []
        self.step = "compose"
    
    
    def append_feedback(self, message: str):
        """Append a feedback message to the AI feedback box"""
        timestamp = ""
        import datetime
        try:
            timestamp = datetime.datetime.now().strftime("%H:%M:%S")
        except:
            pass
        if self.ai_feedback:
            self.ai_feedback += f"\n[{timestamp}] {message}"
        else:
            self.ai_feedback = f"[{timestamp}] {message}"


# Import app from app.py for Reflex compatibility
# Using importlib to avoid circular import issues
import importlib
_app_module = None

def _get_app():
    """Lazy import of app to avoid circular dependencies"""
    global _app_module
    if _app_module is None:
        _app_module = importlib.import_module('email_privacy_redactor_ai.app')
    return _app_module.app

# Use __getattr__ for lazy loading
def __getattr__(name):
    if name == 'app':
        return _get_app()
    raise AttributeError(f"module '{__name__}' has no attribute '{name}'")
