# HOA Email Onboarding System

## Postmark Developer Challenge Submission

A comprehensive HOA (Homeowners Association) email onboarding system that showcases **Postmark's inbound email processing capabilities** with **Google Gemini AI integration**. This application demonstrates a complete email workflow from outbound information requests to intelligent automated response processing and generation.

## 🏆 **Challenge Highlights**

### **Inbound Email Processing Showcase**
- **Webhook Integration**: Seamless processing of inbound emails via Postmark webhooks
- **Automated HOA Identification**: Smart matching of email responses to HOA records
- **Real-time Response Display**: Immediate visualization of received responses
- **🤖 AI-Powered Analysis**: Google Gemini AI integration for intelligent email parsing
- **Automated Response Generation**: Context-aware follow-up emails based on AI analysis
- **Smart Categorization**: 5-scenario classification with confidence scoring

### **Live Demo**
- **Application URL**: `https://rghv404.pythonanywhere.com`
- **Webhook Endpoint**: `https://rghv404.pythonanywhere.com/webhook/postmark-inbound/`
- **Inbound Email**: `4c17207b2cb109e33fb619e01b59252c@inbound.postmarkapp.com`

## 🚀 **Key Features**

### **Outbound Email System**
- Professional HTML email templates for HOA information requests
- **Smart Demo Email Redirection** to `raghv@mainstay.io` (customizable per send)
- **Custom Demo Email Input** - judges can use their own email for testing
- Reply-to configuration pointing to Postmark inbound address
- **Clear Demo Messaging** with spam folder warnings and AI feature previews
- Comprehensive property and HOA information display

### **🤖 AI-Powered Email Processing**
- **Webhook Endpoint**: Secure processing of Postmark inbound webhooks
- **HOA Identification**: Automatic matching via email address and subject line
- **Response Storage**: Complete email content preservation with AI analysis
- **Intelligent Analysis**: Google Gemini AI categorizes responses into 5 scenarios:
  - **Complete Response**: All required information provided
  - **Requesting Clarification**: HOA needs more details before responding
  - **Incomplete Response**: Partial information provided
  - **No Property Management**: HOA doesn't manage properties
  - **Partial Property Management**: HOA manages some but not all properties
- **Smart Response Generation**: AI creates contextual follow-up emails
- **Confidence Scoring**: AI provides confidence levels for analysis accuracy
- **Status Tracking**: Enhanced with AI processing timestamps and results

### **User Interface**
- **Dashboard**: Overview of HOAs, properties, and email statistics
- **HOA Management**: Detailed HOA profiles with property listings
- **Email Preview**: Professional email template preview before sending
- **🤖 AI Analysis Display**: Beautiful visualization of AI analysis results
  - Category badges with confidence percentages
  - Progress bars for completeness scoring
  - Extracted information display with proper formatting
  - AI reasoning explanations for transparency
- **Response Management**: Complete email response display with AI capabilities
  - "Parse and Generate Response" for AI analysis
  - Generated response preview with HTML rendering
  - "Send Generated Response" with demo email routing
- **Admin Interface**: Enhanced Django admin with AI fields

## 📧 **Email Workflow**

### **1. Outbound Process**
1. Select HOA from the dashboard or HOA list
2. Preview the generated email template
3. Send email (redirected to demo address for testing)
4. Email includes reply-to address for automatic response processing

### **2. Inbound Process**
1. HOA responds to the email
2. Postmark forwards response to webhook endpoint
3. System identifies HOA and stores response
4. Response appears in HOA detail page
5. Admin can review and process responses

### **3. 🤖 AI Processing Workflow**
1. **Click "Parse and Generate Response"** on any email response
2. **AI Analysis**: Google Gemini AI analyzes the email content
3. **Categorization**: System classifies response into one of 5 scenarios
4. **Data Extraction**: AI extracts structured information (dues, payment methods, etc.)
5. **Response Generation**: AI creates contextual follow-up email
6. **Review Interface**: Beautiful UI displays analysis results and reasoning
7. **Send Response**: Generated email sent via Postmark with proper threading
8. **Demo Mode**: All emails redirected to `raghv@mainstay.io` for safe testing

## 🛠 **Technical Stack**

- **Backend**: Django 5.0.9 with Python 3.12
- **Email Service**: Postmark API with postmarker library
- **🤖 AI Integration**: Google Gemini AI via google-genai package
- **Database**: SQLite with JSONField for AI analysis storage
- **Frontend**: Bootstrap 5.3 with responsive design and AI result visualization
- **Package Management**: uv for fast dependency management
- **Deployment**: PythonAnywhere hosting
- **Environment**: python-decouple for configuration management

## 🔧 **Setup Instructions**

### **Local Development**
```bash
# Clone repository
git clone <repository-url>
cd hoa_email_onboarding

# Install dependencies
uv sync

# Configure environment
cp .env.example .env
# Edit .env with your Postmark credentials and Gemini API key

# Run migrations
python manage.py migrate

# Create sample data
python manage.py populate_hoa_data
python manage.py create_sample_response

# Start development server
python manage.py runserver
```

### **Postmark Configuration**
1. **API Configuration**:
   - Set `POSTMARK_API_TOKEN` in `.env`
   - Configure `POSTMARK_FROM_EMAIL`

2. **Inbound Email Setup**:
   - Configure webhook URL: `https://rghv404.pythonanywhere.com/webhook/postmark-inbound/`
   - Set inbound email: `4c17207b2cb109e33fb619e01b59252c@inbound.postmarkapp.com`

## 🎯 **Demo Scenario**

### **Testing the Complete Workflow**
1. **Visit**: `https://rghv404.pythonanywhere.com`
2. **Browse HOAs**: View the list of sample HOAs
3. **Select HOA**: Click on any HOA to view details
4. **Customize Demo Email**: Enter your email address or use default `raghv@mainstay.io`
5. **Send Email**: Use "Preview Email" → "Send Demo Email"
6. **Check Your Inbox**: Email sent to your specified demo address (check spam folder!)
7. **Reply to Email**: Respond to demonstrate inbound processing
8. **View Response**: Check HOA detail page for received response
9. **Process Response**: Use "View Full Response" and "Parse and Generate Response"
10. **Experience AI Preview**: See messaging about future Gemini LLM integration

---

**Built for the Postmark Developer Challenge** - Showcasing the power of inbound email processing with a real-world HOA management application.
