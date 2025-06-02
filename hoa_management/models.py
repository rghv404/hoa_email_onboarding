from django.contrib.auth.models import User
from django.core.validators import EmailValidator, RegexValidator
from django.db import models


class HOA(models.Model):
    """
    Model representing a Homeowners Association
    """

    name = models.CharField(max_length=200, help_text="Name of the HOA")
    address = models.TextField(help_text="Physical address of the HOA")
    contact_email = models.EmailField(
        validators=[EmailValidator()], help_text="Primary contact email for the HOA"
    )
    phone_regex = RegexValidator(
        regex=r"^\+?1?\d{9,15}$",
        message="Phone number must be entered in the format: '+999999999'. Up to 15 digits allowed.",
    )
    phone = models.CharField(
        validators=[phone_regex],
        max_length=17,
        blank=True,
        help_text="Contact phone number",
    )
    management_company = models.CharField(
        max_length=200,
        blank=True,
        null=True,
        help_text="Name of the management company (if any)",
    )
    website = models.URLField(blank=True, null=True, help_text="HOA website URL")
    established_date = models.DateField(
        blank=True, null=True, help_text="Date when HOA was established"
    )
    total_units = models.PositiveIntegerField(
        default=0, help_text="Total number of units managed by this HOA"
    )
    monthly_fee_range = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        help_text="Monthly fee range (e.g., '$200-$400')",
    )
    demo_email_used = models.EmailField(
        blank=True,
        null=True,
        help_text="Demo email address used for this HOA's onboarding",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "HOA"
        verbose_name_plural = "HOAs"
        ordering = ["name"]

    def __str__(self):
        return self.name

    @property
    def property_count(self):
        """Return the number of properties associated with this HOA"""
        return self.properties.count()


class Property(models.Model):
    """
    Model representing a property managed by an HOA
    """

    PROPERTY_TYPES = [
        ("single_family", "Single Family Home"),
        ("townhouse", "Townhouse"),
        ("condo", "Condominium"),
        ("apartment", "Apartment"),
        ("commercial", "Commercial"),
        ("other", "Other"),
    ]

    hoa = models.ForeignKey(
        HOA,
        on_delete=models.CASCADE,
        related_name="properties",
        help_text="HOA that manages this property",
    )
    address = models.TextField(help_text="Property address")
    property_type = models.CharField(
        max_length=20,
        choices=PROPERTY_TYPES,
        default="single_family",
        help_text="Type of property",
    )
    unit_count = models.PositiveIntegerField(
        default=1,
        help_text="Number of units in this property (1 for single family homes)",
    )
    square_footage = models.PositiveIntegerField(
        blank=True, null=True, help_text="Total square footage"
    )
    year_built = models.PositiveIntegerField(
        blank=True, null=True, help_text="Year the property was built"
    )
    monthly_hoa_fee = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        blank=True,
        null=True,
        help_text="Monthly HOA fee for this property",
    )
    is_active = models.BooleanField(
        default=True, help_text="Whether this property is actively managed"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Property"
        verbose_name_plural = "Properties"
        ordering = ["address"]

    def __str__(self):
        return f"{self.address} ({self.get_property_type_display()})"


class EmailResponse(models.Model):
    """
    Model representing an email response received from an HOA
    """

    STATUS_CHOICES = [
        ("new", "New"),
        ("reviewed", "Reviewed"),
        ("processed", "Processed"),
    ]

    hoa = models.ForeignKey(
        HOA,
        on_delete=models.CASCADE,
        related_name="email_responses",
        help_text="HOA that sent this response",
    )
    message_id = models.CharField(
        max_length=255, unique=True, help_text="Unique message ID from email provider"
    )
    from_email = models.EmailField(help_text="Email address of the sender")
    subject = models.CharField(max_length=500, help_text="Email subject line")

    # Email content
    raw_content = models.TextField(help_text="Full raw email content")
    html_content = models.TextField(
        blank=True, null=True, help_text="HTML version of email content"
    )
    text_content = models.TextField(
        blank=True, null=True, help_text="Plain text version of email content"
    )

    # Parsed responses to our 7 questions
    manages_properties = models.BooleanField(
        null=True, blank=True, help_text="Does HOA manage the listed properties?"
    )
    properties_confirmation = models.TextField(
        blank=True,
        null=True,
        help_text="Details about property management confirmation",
    )
    regular_dues_amount = models.CharField(
        max_length=100, blank=True, null=True, help_text="Amount of regular HOA dues"
    )
    payment_method = models.CharField(
        max_length=200, blank=True, null=True, help_text="Preferred payment method"
    )
    payment_address = models.TextField(
        blank=True, null=True, help_text="Mailing address for payments"
    )
    master_hoa_name = models.CharField(
        max_length=200, blank=True, null=True, help_text="Name of master HOA if any"
    )
    phone_number = models.CharField(
        max_length=20,
        blank=True,
        null=True,
        help_text="Primary phone number for HOA business",
    )
    management_company = models.CharField(
        max_length=200, blank=True, null=True, help_text="Management company name"
    )

    # Metadata
    response_completeness_score = models.IntegerField(
        default=0, help_text="Completeness score from 0-100 based on answered questions"
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="new",
        help_text="Processing status of the response",
    )
    reviewed_by = models.ForeignKey(
        User,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        help_text="User who reviewed this response",
    )
    reviewed_at = models.DateTimeField(
        null=True, blank=True, help_text="When this response was reviewed"
    )

    # AI Analysis fields
    ai_analysis_result = models.JSONField(
        null=True,
        blank=True,
        help_text="AI analysis result with categorization and extracted data",
    )
    ai_generated_response = models.TextField(
        blank=True, null=True, help_text="AI-generated follow-up email response"
    )
    ai_reasoning = models.TextField(
        blank=True,
        null=True,
        help_text="AI explanation for the categorization and response",
    )
    ai_processed_at = models.DateTimeField(
        null=True, blank=True, help_text="When this response was processed by AI"
    )
    generated_response_sent = models.BooleanField(
        default=False, help_text="Whether the AI-generated response has been sent"
    )
    generated_response_sent_at = models.DateTimeField(
        null=True, blank=True, help_text="When the generated response was sent"
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Email Response"
        verbose_name_plural = "Email Responses"
        ordering = ["-created_at"]

    def __str__(self):
        return f"Response from {self.hoa.name} - {self.created_at.strftime('%Y-%m-%d %H:%M')}"

    @property
    def content_preview(self):
        """Get a preview of the email content"""
        content = self.text_content or self.html_content or ""
        return content[:200] + "..." if len(content) > 200 else content

    def calculate_completeness_score(self):
        """Calculate and update the completeness score - will be implemented with LLM later"""
        # For now, just return 0 - will be calculated by LLM processing
        self.response_completeness_score = 0
        return self.response_completeness_score
