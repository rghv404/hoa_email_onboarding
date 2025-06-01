from django.contrib import admin

from .models import HOA, EmailResponse, Property


@admin.register(HOA)
class HOAAdmin(admin.ModelAdmin):
    list_display = [
        "name",
        "contact_email",
        "phone",
        "management_company",
        "property_count",
        "created_at",
    ]
    list_filter = ["management_company", "created_at", "established_date"]
    search_fields = ["name", "contact_email", "management_company", "address"]
    readonly_fields = ["created_at", "updated_at", "property_count"]
    fieldsets = (
        (
            "Basic Information",
            {"fields": ("name", "address", "contact_email", "phone", "website")},
        ),
        (
            "Management Details",
            {
                "fields": (
                    "management_company",
                    "established_date",
                    "total_units",
                    "monthly_fee_range",
                )
            },
        ),
        (
            "Timestamps",
            {"fields": ("created_at", "updated_at"), "classes": ("collapse",)},
        ),
    )


@admin.register(Property)
class PropertyAdmin(admin.ModelAdmin):
    list_display = [
        "address",
        "hoa",
        "property_type",
        "unit_count",
        "monthly_hoa_fee",
        "is_active",
    ]
    list_filter = ["property_type", "is_active", "hoa", "year_built"]
    search_fields = ["address", "hoa__name"]
    readonly_fields = ["created_at", "updated_at"]
    fieldsets = (
        (
            "Basic Information",
            {"fields": ("hoa", "address", "property_type", "unit_count")},
        ),
        (
            "Property Details",
            {
                "fields": (
                    "square_footage",
                    "year_built",
                    "monthly_hoa_fee",
                    "is_active",
                )
            },
        ),
        (
            "Timestamps",
            {"fields": ("created_at", "updated_at"), "classes": ("collapse",)},
        ),
    )


@admin.register(EmailResponse)
class EmailResponseAdmin(admin.ModelAdmin):
    list_display = [
        "hoa",
        "from_email",
        "subject",
        "status",
        "response_completeness_score",
        "created_at",
    ]
    list_filter = ["status", "created_at", "hoa", "response_completeness_score"]
    search_fields = ["hoa__name", "from_email", "subject", "text_content"]
    readonly_fields = ["created_at", "updated_at", "message_id", "content_preview"]

    fieldsets = (
        (
            "Basic Information",
            {"fields": ("hoa", "from_email", "subject", "message_id", "status")},
        ),
        (
            "Email Content",
            {
                "fields": ("text_content", "html_content", "raw_content"),
                "classes": ("collapse",),
            },
        ),
        (
            "Parsed Responses",
            {
                "fields": (
                    "manages_properties",
                    "properties_confirmation",
                    "regular_dues_amount",
                    "payment_method",
                    "payment_address",
                    "master_hoa_name",
                    "phone_number",
                    "management_company",
                )
            },
        ),
        ("Analysis", {"fields": ("response_completeness_score", "content_preview")}),
        ("Review Information", {"fields": ("reviewed_by", "reviewed_at")}),
        (
            "Timestamps",
            {"fields": ("created_at", "updated_at"), "classes": ("collapse",)},
        ),
    )

    def save_model(self, request, obj, form, change):
        # Auto-calculate completeness score when saving
        obj.calculate_completeness_score()
        super().save_model(request, obj, form, change)
