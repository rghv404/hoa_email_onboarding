# Google Gemini AI Integration Guide

## Overview

This document describes the intelligent email parsing and response generation feature implemented using Google Gemini AI for the HOA email onboarding system.

## Features Implemented

### 1. Email Response Analysis
The system categorizes HOA email responses into 5 scenarios:
- **Complete Response**: HOA answered all required questions
- **Requesting Clarification**: HOA asking for more details
- **Incomplete Response**: HOA answered some but not all questions
- **No Property Management**: HOA doesn't manage any properties
- **Partial Property Management**: HOA manages some but not all properties

### 2. Automated Response Generation
Based on the analysis, the system generates appropriate follow-up emails:
- **Complete Response**: Thank them and ask to add contact for future communications
- **Requesting Clarification**: Address their questions and re-ask for information
- **Incomplete Response**: Politely ask for missing information with explanations
- **No Property Management**: Thank them and ask to ignore the email
- **Partial Property Management**: Confirm which properties they don't manage

### 3. AI Reasoning and Review
- AI provides reasoning for categorization decisions
- Generated responses can be reviewed before sending
- UI displays confidence scores and extracted data

### 4. Email Threading
- Maintains proper email conversation threads
- Uses In-Reply-To and References headers
- Preserves email context for better communication

## Setup Instructions

### 1. Install Dependencies
The `google-genai` package has been added to `pyproject.toml` and installed via `uv`.

### 2. Configure API Key
1. Get your Gemini API key from: https://aistudio.google.com/app/apikey
2. Add it to your `.env` file:
   ```
   GEMINI_API_KEY=your_actual_api_key_here
   ```

### 3. Database Migration
The following fields have been added to the `EmailResponse` model:
- `ai_analysis_result` (JSONField): Stores AI analysis results
- `ai_generated_response` (TextField): Generated email response
- `ai_reasoning` (TextField): AI explanation for decisions
- `ai_processed_at` (DateTimeField): Processing timestamp
- `generated_response_sent` (BooleanField): Send status
- `generated_response_sent_at` (DateTimeField): Send timestamp

Migration has been created and applied.

## Usage

### 1. Processing Email Responses
1. Navigate to an email response detail page
2. Click "Parse and Generate Response" button
3. AI will analyze the email and generate a response
4. Review the analysis results and generated response
5. Click "Send Generated Response" to send the email

### 2. Viewing AI Analysis
The email response detail page now shows:
- **AI Analysis Results**: Category, confidence, reasoning
- **Extracted Information**: Parsed data from the email
- **Response Completeness**: Score based on answered questions
- **Generated Response**: AI-created follow-up email

### 3. Demo Mode
- All generated responses are sent to `raghvendra.singh@opendoor.com`
- Original HOA email addresses are preserved in the database
- Clear demo notices are displayed in the UI

## Technical Implementation

### Core Components

#### 1. GeminiEmailAnalyzer (`services/gemini_service.py`)
Main service class that handles:
- Email content analysis using Gemini AI
- Response categorization into 5 scenarios
- Follow-up email generation
- Data extraction and completeness scoring

#### 2. Updated Views (`hoa_management/views.py`)
- `parse_and_generate_response`: Processes emails with AI
- `send_generated_response`: Sends AI-generated responses

#### 3. Enhanced Templates
- Updated `email_response_detail.html` with AI analysis display
- Shows categorization, confidence, reasoning, and generated responses
- Interactive buttons for processing and sending

#### 4. Email Threading (`services/email_service.py`)
- Enhanced email service with threading support
- Proper In-Reply-To and References headers
- Maintains conversation context

### AI Prompts

The system uses carefully crafted prompts for:
1. **Analysis Prompt**: Categorizes emails and extracts structured data
2. **Response Prompt**: Generates appropriate follow-up emails based on category

### Error Handling
- Graceful handling of missing API keys
- Fallback responses for AI failures
- Clear error messages in the UI
- Comprehensive logging

## Required Questions Analysis

The AI analyzes responses for these 7 required questions:
1. Property management confirmation
2. Regular dues amount
3. Payment method preference
4. Payment address
5. Master HOA name (if applicable)
6. Phone number for HOA business
7. Management company name (if applicable)

## Response Categories in Detail

### Complete Response
- All required questions answered
- High completeness score (80%+)
- Generates thank you email with contact addition request

### Requesting Clarification
- HOA asks questions before answering
- Generates contextual clarification response
- Re-asks for original information needed

### Incomplete Response
- Some questions answered, others missing
- Generates polite follow-up for missing information
- Explains why each piece of information is needed

### No Property Management
- HOA states they don't manage properties
- Generates polite dismissal email
- Apologizes for confusion

### Partial Property Management
- HOA manages some but not all properties
- Generates verification request
- Asks for information only about managed properties

## Testing

### Sample Email Responses
Use the management command to create test data:
```bash
python manage.py create_sample_response
```

### Manual Testing
1. Create or use existing email responses
2. Test AI analysis with different response types
3. Verify generated responses are appropriate
4. Test email sending functionality

## Security Considerations

- API keys stored in environment variables
- Demo mode prevents accidental real emails
- Input validation on all AI-generated content
- Proper error handling for API failures

## Future Enhancements

1. **Real-time Processing**: Automatic AI analysis on email receipt
2. **Response Templates**: Customizable response templates
3. **Confidence Thresholds**: Automatic sending based on confidence scores
4. **Analytics Dashboard**: AI performance metrics and insights
5. **Multi-language Support**: Support for non-English HOA responses

## Troubleshooting

### Common Issues

1. **Missing API Key Error**
   - Ensure GEMINI_API_KEY is set in .env file
   - Verify API key is valid and has proper permissions

2. **AI Analysis Fails**
   - Check internet connectivity
   - Verify Gemini API service status
   - Review logs for specific error messages

3. **Generated Response Not Sent**
   - Check Postmark configuration
   - Verify demo email address is valid
   - Review email service logs

### Logs
Check Django logs for detailed error information:
- AI processing errors
- Email sending failures
- API communication issues

## Support

For issues or questions about the AI integration:
1. Check the logs for error details
2. Verify all configuration settings
3. Test with sample data first
4. Review the AI prompts for customization needs
