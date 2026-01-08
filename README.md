# 📧 Email Privacy Redactor AI

**Intelligent Email Privacy Protection with AI-Powered Text and Image Redaction**

[![Demo](https://img.shields.io/badge/Live%20Demo-blue?style=for-the-badge)](https://email-privacy-redactor-ai.reflex.app)
[![Reflex](https://img.shields.io/badge/Built%20with-Reflex-4a154b?style=for-the-badge)](https://reflex.dev)
[![Python](https://img.shields.io/badge/Python-3.9+-3776AB?style=for-the-badge&logo=python)](https://www.python.org/)

---

## 🎯 Overview

**Email Privacy Redactor AI** is a sophisticated web application that automatically detects and redacts sensitive information from both email text and attached images before sending. Built with modern AI technologies, it ensures your emails remain compliant with privacy regulations (GDPR, HIPAA, etc.) while maintaining readability.

### 💡 The Problem It Solves

In today's digital workplace, sharing emails often requires redacting sensitive information like:
- Personal identifiable information (PII)
- Financial data (credit cards, account numbers)
- Authentication credentials (passwords, tokens, API keys)
- Healthcare information
- Confidential business data

Manually finding and redacting this information is:
- ❌ Time-consuming and error-prone
- ❌ Easy to miss hidden sensitive data
- ❌ Impractical for images and screenshots
- ❌ Risk of human error leading to data breaches

### ✅ Our Solution

**Email Privacy Redactor AI** provides:
- 🤖 **AI-Powered Detection**: Uses advanced LLM models to intelligently identify 12+ types of sensitive information
- 📝 **Text Redaction**: Automatically replaces sensitive data in email content with customizable placeholders
- 🖼️ **Image Redaction**: OCR + AI analysis to redact sensitive text from images and screenshots
- ⚙️ **Granular Control**: Enable/disable specific redaction types based on your needs
- 📧 **Direct Integration**: Preview, edit, and send redacted emails seamlessly
- 🔒 **Privacy-First**: All processing happens securely with no data storage

---

## 🌟 Key Features

### 🎛️ **Customizable Redaction Types**
- ✅ **Names** (First names, last names, full names)
- ✅ **Email Addresses** (Any email format)
- ✅ **Phone Numbers** (All international formats)
- ✅ **Physical Addresses** (Street, city, state, zip)
- ✅ **Social Security Numbers** (SSN formats)
- ✅ **Credit Card Numbers** (Including masked formats like `Visa **** 9901`)
- ✅ **API Keys** (Various key formats)
- ✅ **Passwords** (Password values, not labels)
- ✅ **Tokens** (JWT, API tokens, session tokens)
- ✅ **ID Numbers** (Document IDs, verification IDs, employee IDs - formats like `HC-9920-ALPHA`, `PASS-99283-TX`)
- ✅ **Dollar Amounts** (Prices, salaries, costs)
- ✅ **Account Numbers** (Bank accounts, customer accounts)

### 🎨 **User Experience Features**
- **Smart Test Content Loading**: Quick-load sample emails and images from predefined test files
- **Interactive Preview**: Side-by-side comparison of original vs. redacted content
- **Image Modal Viewers**: Click images to view full-size versions
- **Real-time AI Feedback**: Live status updates during redaction process
- **Custom Placeholders**: Edit replacement text for each redaction type
- **Enable/Disable Controls**: Checkbox-based control for each redaction type
- **Image Upload Validation**: Limits (max 4 images, 5 MB total) with user-friendly error messages
- **Auto-Clear on Refresh**: Prevents stale data on page reloads
- **Email Validation**: Real-time validation for To and CC fields

### 🔧 **Technical Features**
- **Async Processing**: Non-blocking API calls for smooth user experience
- **Multiple Email Providers**: Supports Mailpit (dev), Resend API, and SendGrid (production)
- **Base64 Image Handling**: Efficient client-side image processing
- **OCR Integration**: Advanced text extraction from images with bounding box coordinates
- **AI Classification**: Sophisticated prompt engineering for accurate data type detection
- **State Management**: Persistent state across navigation with "Back" button support

---

## 🏗️ Technology Stack

### **Frontend & Framework**
- **[Reflex](https://reflex.dev)** (v0.8.24.post1) - Modern Python web framework for full-stack applications
  - Built on React/Next.js under the hood
  - Component-based architecture
  - Reactive state management
  - Server-side rendering (SSR)

### **AI & Machine Learning**
- **[Groq API](https://console.groq.com)** - Ultra-fast LLM inference
  - **Model**: `llama-3.3-70b-versatile`
  - **Use Case**: Text classification and redaction in both email content and OCR-extracted text
  - **Why Groq**: Lightning-fast inference (~300 tokens/second), cost-effective, privacy-focused

### **OCR (Optical Character Recognition)**
- **[OCR.space API](https://ocr.space/ocrapi)** - Cloud-based OCR service
  - **Engine**: OCR Engine 2 (optimized for structured data)
  - **Use Case**: Extract text with precise bounding box coordinates from images
  - **Output**: Text content + pixel coordinates for accurate redaction boxes

### **Email Services**
- **Development**: [Mailpit](https://github.com/axllent/mailpit) - Local SMTP testing server
- **Production**: 
  - **[Resend API](https://resend.com)** (Primary) - Modern email API
  - **[SendGrid API](https://sendgrid.com)** (Fallback) - Enterprise email delivery

### **Core Libraries**
- **Python 3.9+** - Main programming language
- **httpx** - Async HTTP client for API calls
- **Pillow (PIL)** - Image processing and manipulation
- **python-dotenv** - Environment variable management

### **Infrastructure**
- **Reflex Cloud** - Hosting platform for Reflex applications
- **Base64 Encoding** - In-memory image handling (no file system writes)

---

## 🔌 APIs Used

### 1. **Groq API** (`https://api.groq.com/openai/v1/chat/completions`)

**Purpose**: AI-powered text analysis and redaction

**Usage**:
- **Text Redaction**: Analyzes email content and replaces sensitive information with placeholders
- **Image Text Classification**: After OCR extraction, classifies each text box by sensitive data type

**Model**: `llama-3.3-70b-versatile`
- 70 billion parameter model
- Optimized for instruction following
- Temperature: 0.3 (deterministic, accurate responses)

**Prompt Engineering**:
- Dynamic prompt generation based on enabled redaction types
- Explicit rules to prevent false positives (e.g., don't redact company names)
- Pattern matching for complex formats (IDs with hyphens, masked credit cards, JWT tokens)
- Context-aware classification (recognizes labels like "Document ID:" followed by values)

**Example Request**:
```python
{
    "model": "llama-3.3-70b-versatile",
    "messages": [{
        "role": "user",
        "content": "Redact sensitive information: Names → [NAME], Emails → [EMAIL], ..."
    }],
    "temperature": 0.3
}
```

### 2. **OCR.space API** (`https://api.ocr.space/parse/image`)

**Purpose**: Extract text from images with bounding box coordinates

**Configuration**:
- **Engine**: 2 (structured data optimization)
- **Input**: Base64-encoded images
- **Output**: JSON with text content and coordinates (x, y, width, height)

**Use Case**:
1. User uploads image containing sensitive text
2. OCR.space extracts all text with pixel coordinates
3. Groq AI classifies each text box as sensitive or not
4. PIL draws black boxes over sensitive text areas
5. Returns redacted image

**Example Response Structure**:
```json
{
    "ParsedResults": [{
        "TextOverlay": {
            "Lines": [{
                "Words": [{
                    "WordText": "John Smith",
                    "Left": 50,
                    "Top": 100,
                    "Width": 120,
                    "Height": 30
                }]
            }]
        }
    }]
}
```

### 3. **Email APIs** (Resend / SendGrid)

**Resend API** (`https://api.resend.com/emails`):
- Primary production email service
- Modern REST API
- Supports HTML/text emails with attachments

**SendGrid API** (`https://api.sendgrid.com/v3/mail/send`):
- Fallback email service
- Enterprise-grade delivery
- Automatic retry on Resend failure

---

## 📋 How It Works: Step-by-Step

### **Step 1: Compose Email** (`/`)
1. **Fill Email Details**:
   - Enter recipient(s) in "To" field (comma-separated for multiple)
   - Optionally add CC recipients
   - Enter email subject
   - Type or paste email content in the Content area

2. **Optional: Load Test Content**:
   - Click the 📄 icon next to "Content:" label
   - Select from predefined test files (e.g., "Member Enrollment", "Incident Report")
   - Content automatically populates the text area

3. **Optional: Upload Images**:
   - Click "Upload Images" button or drag-and-drop
   - Or click the 🖼️ icon to load sample test images
   - Upload up to 4 images (max 5 MB total)
   - Images appear as thumbnails; click to view full-size

4. **Configure Redaction Settings**:
   - Each redaction type has a checkbox (enabled by default) and customizable placeholder
   - Check/uncheck types you want to redact or skip
   - Edit placeholder text (e.g., change `[NAME]` to `[REDACTED NAME]`)

### **Step 2: Preview & Redact** (Click "Preview Redacted Email")
1. **API Calls Initiated**:
   - **Text Redaction**: 
     - Email content sent to Groq API
     - AI analyzes text and identifies sensitive information
     - Replaces with specified placeholders
     - Returns redacted text
   
   - **Image Redaction** (if images uploaded):
     - Each image sent to OCR.space API
     - OCR extracts text with coordinates
     - Text boxes sent to Groq AI for classification
     - PIL draws black boxes over sensitive text areas
     - Returns redacted images

2. **Real-time Feedback**:
   - AI feedback panel shows progress:
     - `🔄 Connecting to Groq API...`
     - `📤 Sending text to Groq API...`
     - `✅ Text redaction complete (X tokens used)`
     - `🖼️ Processing 3 image(s)...`
     - `✅ All images processed successfully`

3. **Preview Page** (`/preview`):
   - Displays redacted email content (editable)
   - Shows redacted images side-by-side with originals
   - "Show Comparison" button for side-by-side text comparison
   - Original data preserved for "Back" button functionality

### **Step 3: Review & Edit**
1. **Review Redacted Content**:
   - Verify all sensitive information is properly redacted
   - Check that non-sensitive information remains intact

2. **Make Manual Edits** (if needed):
   - Content area is fully editable
   - Make any adjustments before sending

3. **View Images**:
   - Click any image to open full-size modal
   - Compare original vs. redacted versions
   - Close modal with X button

### **Step 4: Send or Go Back**
1. **Send Email** (Click "Send Email" button):
   - Email sent via configured service (Mailpit/Resend/SendGrid)
   - Images attached if present
   - Redirects to success page

2. **Go Back** (Click "Back" button):
   - Returns to compose page
   - All original data restored (unredacted content, original images)
   - Can modify settings and redact again

### **Step 5: Confirmation** (`/sent`)
- Success message: "Your AI redacted email was successfully sent."
- Option to send another email

---

## 🚀 Real-World Use Cases

### **1. Healthcare & HIPAA Compliance**
- **Scenario**: Healthcare provider needs to forward patient inquiry to specialist
- **Solution**: Automatically redact patient names, SSNs, medical record IDs, addresses
- **Benefit**: Ensures HIPAA compliance while maintaining email context

### **2. Financial Services**
- **Scenario**: Bank representative sharing account inquiry with compliance team
- **Solution**: Redacts account numbers, credit card numbers, SSNs, dollar amounts
- **Benefit**: Protects customer financial data per PCI-DSS requirements

### **3. Customer Support**
- **Scenario**: Support agent needs to escalate ticket with customer information
- **Solution**: Redacts names, emails, phone numbers, account numbers
- **Benefit**: Privacy protection while maintaining ticket context

### **4. Legal & Compliance**
- **Scenario**: Lawyer forwarding case-related email with client information
- **Solution**: Redacts client names, addresses, SSNs, case IDs
- **Benefit**: Attorney-client privilege protection

### **5. Human Resources**
- **Scenario**: HR sharing employee inquiry with management
- **Solution**: Redacts employee IDs, SSNs, addresses, salary information
- **Benefit**: Employee privacy compliance

### **6. Screenshot Sharing**
- **Scenario**: Developer sharing error screenshot containing API keys
- **Solution**: OCR extracts text, AI identifies and redacts API keys, tokens, credentials
- **Benefit**: Prevents accidental credential exposure

### **7. GDPR Compliance**
- **Scenario**: European company sharing customer data inquiry
- **Solution**: Automatically redacts all PII (names, emails, addresses, IDs)
- **Benefit**: GDPR-compliant data sharing

---

## 🛠️ Installation & Setup

### **Prerequisites**
- Python 3.9 or higher
- pip (Python package manager)
- API keys:
  - [Groq API Key](https://console.groq.com) (Free tier available)
  - [OCR.space API Key](https://ocr.space/ocrapi/freekey) (Free tier available)
  - Email service keys (optional for development):
    - [Resend API Key](https://resend.com/api-keys)
    - [SendGrid API Key](https://app.sendgrid.com/settings/api_keys)

### **Installation Steps**

1. **Clone the Repository**:
   ```bash
   git clone https://github.com/yourusername/EmailPrivacyRedactorAI.git
   cd EmailPrivacyRedactorAI
   ```

2. **Create Virtual Environment** (Recommended):
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Set Up Environment Variables**:
   Create a `.env` file in the root directory:
   ```env
   # Required APIs
   GROQ_API_KEY=your_groq_api_key_here
   OCRSPACE_API_KEY=your_ocrspace_api_key_here
   
   # Optional: Email services (for production)
   EMAIL_SENDER_RESEND=your_resend_email@yourdomain.com
   RESEND_API_KEY=your_resend_api_key_here
   EMAIL_SENDER_SENDGRID=your_sendgrid_email@yourdomain.com
   SENDGRID_API_KEY=your_sendgrid_api_key_here
   
   # Development email (optional)
   EMAIL_SENDER_MAILPIT=test@example.com
   
   # Force production email sending locally (optional)
   USE_PRODUCTION_EMAIL=false
   ```

5. **Run Development Server**:
   ```bash
   reflex run
   ```
   The app will be available at `http://localhost:3000`

6. **Build for Production**:
   ```bash
   reflex export
   ```

### **Deploy to Reflex Cloud**

1. **Install Reflex CLI** (if not already installed):
   ```bash
   pip install reflex-cli
   ```

2. **Login to Reflex Cloud**:
   ```bash
   reflex login
   ```

3. **Deploy**:
   ```bash
   reflex deploy
   ```

4. **Set Environment Variables in Reflex Cloud Dashboard**:
   - Go to your app's settings
   - Add all required environment variables from `.env` file

---

## 📁 Project Structure

```
EmailPrivacyRedactorAI/
├── email_privacy_redactor_ai/
│   ├── __init__.py
│   ├── email_privacy_redactor_ai.py    # Main state management
│   ├── app.py                           # Reflex app configuration
│   ├── index_page.py                    # Landing page
│   ├── pages/
│   │   ├── email_compose_page.py        # Compose email UI
│   │   ├── email_preview_page.py        # Preview redacted email UI
│   │   └── email_sent_page.py           # Success confirmation page
│   ├── components/
│   │   ├── text_redactor.py             # Groq API text redaction logic
│   │   ├── ocrspace_image_redactor.py   # OCR + AI image redaction
│   │   ├── email_sender.py              # Email sending orchestrator
│   │   ├── image_file_handler.py        # Image upload handling
│   │   ├── mailpit_email_sender.py      # Mailpit email sender
│   │   ├── resend_api_email_sender.py   # Resend API integration
│   │   ├── sendgrid_api_email_sender.py # SendGrid API integration
│   │   └── ui/
│   │       ├── checkbox_input.py        # Custom checkbox + input component
│   │       └── auto_clear_page_button.py # Auto-clear on refresh component
│   └── assets/
│       ├── Incident_Report_Test.txt     # Sample test content
│       ├── Incident_Report_Test.jpg     # Sample test images
│       ├── Member_Enrollment_Test.txt
│       ├── Member_Enrollment_Test.jpg
│       ├── Service_Activation_Record_Test.txt
│       └── Service_Activation_Record_Test.jpg
├── rxconfig.py                          # Reflex configuration
├── requirements.txt                     # Python dependencies
└── README.md                            # This file
```

---

## 🔒 Privacy & Security

- **No Data Storage**: Original or redacted content is never stored on servers
- **In-Memory Processing**: All processing happens in application memory
- **Secure API Calls**: All API communications use HTTPS
- **Client-Side Validation**: Email validation happens before API calls
- **Environment Variables**: API keys stored securely, never in code
- **Base64 Encoding**: Images handled as base64 strings (no file system writes)

---

## 🎨 Customization

### **Custom Placeholders**
Edit placeholder text in the "Redact this information" section:
- Default: `[NAME]`, `[EMAIL]`, `[PHONE]`, etc.
- Custom: `[REDACTED]`, `***`, `[PRIVATE]`, etc.

### **Disable Redaction Types**
Uncheck boxes next to redaction types you don't want to use. The AI will skip those types entirely.

### **Test Content**
Add your own test files to `email_privacy_redactor_ai/assets/`:
- Text files: Must end with `_Test.txt`
- Image files: Must end with `_Test.jpg`

---

## 🐛 Troubleshooting

### **API Key Errors**
- Ensure `.env` file exists and contains valid API keys
- Verify keys are active in respective service dashboards
- Check for typos in environment variable names

### **Image Upload Fails**
- Check file size (max 5 MB total)
- Check number of images (max 4)
- Ensure images are in supported formats (PNG, JPG, JPEG, GIF)

### **Email Sending Fails**
- Development: Ensure Mailpit is running (if using local SMTP)
- Production: Verify Resend/SendGrid API keys and sender email addresses
- Check email validation errors in the UI

### **Redaction Not Working**
- Verify API keys are set correctly
- Check AI feedback panel for error messages
- Ensure at least one redaction type is enabled
- Check Groq API quota/limits

---

## 📊 Performance

- **Text Redaction**: ~1-3 seconds (depending on content length)
- **Image Redaction**: ~3-5 seconds per image (OCR + AI classification + redaction)
- **Groq API**: Ultra-fast inference (~300 tokens/second)
- **OCR.space**: ~1-2 seconds per image
- **Total Processing**: ~5-15 seconds for typical email with 2-3 images

---

## 🚧 Future Enhancements

- [ ] Batch processing for multiple emails
- [ ] Custom redaction rules and patterns
- [ ] PDF document support
- [ ] Redaction history/audit log
- [ ] Multi-language support
- [ ] Integration with email clients (Gmail, Outlook)
- [ ] Advanced image redaction (blur, pixelate options)
- [ ] Export redacted content to PDF
- [ ] API endpoint for programmatic access

---

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

---

## 🙏 Acknowledgments

- **[Groq](https://groq.com)** for providing fast, cost-effective LLM inference
- **[OCR.space](https://ocr.space)** for reliable OCR services
- **[Reflex](https://reflex.dev)** for the amazing Python web framework
- **[Resend](https://resend.com)** and **[SendGrid](https://sendgrid.com)** for email delivery services

---

## 📞 Support & Contact

- **Live Demo**: [https://email-privacy-redactor-ai.reflex.app](https://email-privacy-redactor-ai.reflex.app)
- **Issues**: [GitHub Issues](https://github.com/yourusername/EmailPrivacyRedactorAI/issues)
- **Documentation**: Check this README for detailed usage instructions

---

**Built with ❤️ using Python, Reflex, and AI**
