# Deployment Guide for PythonAnywhere

## Pre-Deployment Checklist

### 1. Environment Configuration
- [ ] Update `.env` with production Postmark credentials
- [ ] Verify `ALLOWED_HOSTS` includes `rghv404.pythonanywhere.com`
- [ ] Set `DEBUG=False` for production (optional for demo)

### 2. Database Setup
- [ ] Run migrations: `python manage.py migrate`
- [ ] Create sample data: `python manage.py populate_hoa_data`
- [ ] Create sample response: `python manage.py create_sample_response`
- [ ] Create superuser: `python manage.py createsuperuser`

### 3. Static Files
- [ ] Collect static files: `python manage.py collectstatic`
- [ ] Verify static files are served correctly

## PythonAnywhere Configuration

### 1. Web App Settings
- **Source code**: `/home/rghv404/repos/hoa_email_onboarding`
- **Working directory**: `/home/rghv404/repos/hoa_email_onboarding`
- **WSGI file**: Update to point to `hoa_email_onboarding.wsgi`

### 2. Static Files Configuration
- **URL**: `/static/`
- **Directory**: `/home/rghv404/hoa_email_onboarding/static`

### 3. Media Files Configuration
- **URL**: `/media/`
- **Directory**: `/home/rghv404/hoa_email_onboarding/media`

## Postmark Configuration

### 1. Webhook Setup
- **Webhook URL**: `https://rghv404.pythonanywhere.com/webhook/postmark-inbound/`
- **HTTP Method**: POST
- **Content Type**: application/json

### 2. Inbound Email Configuration
- **Inbound Email Address**: `4c17207b2cb109e33fb619e01b59252c@inbound.postmarkapp.com`
- **Forward to Webhook**: Enable
- **Include Raw Email**: Enable (optional)

### 3. API Configuration
- **Server Token**: Set in environment variables
- **From Email**: `raghvendra.singh@opendoor.com` (for demo)
- **Reply-To**: `4c17207b2cb109e33fb619e01b59252c@inbound.postmarkapp.com`

## Testing Checklist

### 1. Basic Functionality
- [ ] Homepage loads correctly
- [ ] HOA list displays sample data
- [ ] HOA detail pages work
- [ ] Email preview functionality works
- [ ] Admin interface accessible

### 2. Email Functionality
- [ ] Outbound emails send successfully
- [ ] Emails redirect to demo address
- [ ] Reply-to header is set correctly
- [ ] Email templates render properly

### 3. Webhook Functionality
- [ ] Webhook endpoint responds to POST requests
- [ ] Email responses are processed correctly
- [ ] HOA identification works
- [ ] Response display on HOA detail page
- [ ] Full response page functionality

### 4. Demo Workflow
- [ ] Complete end-to-end email workflow
- [ ] Response processing and display
- [ ] "Parse and Generate Response" button works
- [ ] Status management (new/reviewed/processed)

## Troubleshooting

### Common Issues
1. **Static files not loading**: Check static files configuration
2. **Database errors**: Ensure migrations are run
3. **Webhook not receiving**: Verify URL and Postmark configuration
4. **Email not sending**: Check Postmark API credentials

### Logs to Check
- PythonAnywhere error logs
- Django application logs
- Postmark delivery logs
- Webhook processing logs

## Security Considerations

### Production Settings
- Set `DEBUG=False`
- Use strong `SECRET_KEY`
- Configure proper `ALLOWED_HOSTS`
- Enable HTTPS (automatic on PythonAnywhere)

### Webhook Security
- Consider adding webhook signature verification
- Rate limiting for webhook endpoint
- Input validation for email content

## Performance Optimization

### Database
- Consider PostgreSQL for production
- Add database indexes for frequently queried fields
- Implement database connection pooling

### Caching
- Add Redis for session and cache storage
- Implement template caching
- Cache frequently accessed data

### Background Processing
- Use Celery for email processing
- Queue webhook processing for high volume
- Implement retry logic for failed operations
