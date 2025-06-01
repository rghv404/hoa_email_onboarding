import json
import logging
import random

from django.contrib import messages
from django.core.paginator import Paginator
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods

from services.email_processor import EmailResponseProcessor
from services.email_service import EmailService
from services.gemini_service import GeminiEmailAnalyzer

from .models import HOA, EmailResponse, Property


def hoa_list(request):
    """
    Display a list of HOAs with pagination
    """
    # Get all HOAs and randomize the order for variety
    hoas = list(HOA.objects.all())
    random.shuffle(hoas)

    # Paginate the results
    paginator = Paginator(hoas, 12)  # Show 12 HOAs per page
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    context = {
        "page_obj": page_obj,
        "total_hoas": len(hoas),
    }

    return render(request, "hoa_management/hoa_list.html", context)


def hoa_detail(request, hoa_id):
    """
    Display details for a specific HOA including its properties and latest email response
    """
    hoa = get_object_or_404(HOA, id=hoa_id)
    properties = hoa.properties.filter(is_active=True).order_by("address")

    # Get the most recent email response
    latest_response = hoa.email_responses.first()  # Already ordered by -created_at

    context = {
        "hoa": hoa,
        "properties": properties,
        "latest_response": latest_response,
    }

    return render(request, "hoa_management/hoa_detail.html", context)


def email_preview(request, hoa_id):
    """
    Preview the email that would be sent to an HOA
    """
    hoa = get_object_or_404(HOA, id=hoa_id)
    email_service = EmailService()
    email_content = email_service.generate_hoa_onboarding_email(hoa)

    context = {
        "hoa": hoa,
        "email_subject": email_content["subject"],
        "email_body": email_content["body"],
    }

    return render(request, "hoa_management/email_preview.html", context)


@require_http_methods(["POST"])
def send_email(request, hoa_id):
    """
    Send onboarding email to an HOA with optional demo email customization
    """
    hoa = get_object_or_404(HOA, id=hoa_id)
    email_service = EmailService()

    # Get custom demo email from form if provided
    demo_email = request.POST.get("demo_email", "").strip() or None

    try:
        result = email_service.send_hoa_onboarding_email(hoa, demo_email=demo_email)

        if result["success"]:
            demo_info = f"Demo email sent to: {result['demo_email']}"
            if result["is_custom_demo_email"]:
                demo_info += " (custom address)"
            else:
                demo_info += " (default demo address)"

            messages.success(
                request,
                f"✅ Email sent successfully! {demo_info}. "
                f"📧 Check your inbox (and spam folder) for the demo email. "
                f"🤖 Reply to the email to test our inbound processing and see the future AI response feature!",
            )
        else:
            messages.error(
                request, f"Failed to send email to {hoa.name}: {result['message']}"
            )

    except Exception as e:
        messages.error(
            request, f"An error occurred while sending email to {hoa.name}: {str(e)}"
        )

    # Redirect back to the HOA detail page
    return redirect("hoa_detail", hoa_id=hoa_id)


@require_http_methods(["POST"])
def send_email_ajax(request, hoa_id):
    """
    Send onboarding email to an HOA via AJAX with demo email support
    """
    hoa = get_object_or_404(HOA, id=hoa_id)
    email_service = EmailService()

    # Get custom demo email from form if provided
    demo_email = request.POST.get("demo_email", "").strip() or None

    try:
        result = email_service.send_hoa_onboarding_email(hoa, demo_email=demo_email)

        return JsonResponse(
            {
                "success": result["success"],
                "message": result["message"],
                "hoa_name": hoa.name,
                "demo_email": result.get("demo_email"),
                "is_custom_demo_email": result.get("is_custom_demo_email", False),
            }
        )

    except Exception as e:
        return JsonResponse(
            {
                "success": False,
                "message": f"An error occurred: {str(e)}",
                "hoa_name": hoa.name,
                "demo_email": None,
            }
        )


def dashboard(request):
    """
    Dashboard view showing summary statistics
    """
    total_hoas = HOA.objects.count()
    total_properties = Property.objects.count()
    active_properties = Property.objects.filter(is_active=True).count()

    # Get some recent HOAs for quick access
    recent_hoas = HOA.objects.order_by("-created_at")[:6]

    context = {
        "total_hoas": total_hoas,
        "total_properties": total_properties,
        "active_properties": active_properties,
        "recent_hoas": recent_hoas,
    }

    return render(request, "hoa_management/dashboard.html", context)


@csrf_exempt
@require_http_methods(["POST"])
def postmark_webhook(request):
    """
    Handle inbound email webhooks from Postmark
    """
    try:
        # Parse the JSON payload
        payload = json.loads(request.body.decode("utf-8"))

        # Process the email
        processor = EmailResponseProcessor()
        success, message, email_response = processor.process_inbound_email(payload)

        if success:
            logging.info(f"Webhook processed successfully: {message}")
            return JsonResponse(
                {
                    "status": "success",
                    "message": message,
                    "email_response_id": email_response.id if email_response else None,
                }
            )
        else:
            logging.warning(f"Webhook processing failed: {message}")
            return JsonResponse({"status": "error", "message": message}, status=400)

    except json.JSONDecodeError:
        logging.error("Invalid JSON in webhook payload")
        return JsonResponse(
            {"status": "error", "message": "Invalid JSON payload"}, status=400
        )
    except Exception as e:
        logging.error(f"Webhook processing error: {str(e)}")
        return JsonResponse(
            {"status": "error", "message": f"Processing error: {str(e)}"}, status=500
        )


@require_http_methods(["POST"])
def mark_response_reviewed(request, response_id):
    """
    Mark an email response as reviewed
    """
    try:
        email_response = get_object_or_404(EmailResponse, id=response_id)

        email_response.status = "reviewed"
        email_response.reviewed_at = timezone.now()
        # Note: In a real app, you'd want user authentication
        # email_response.reviewed_by = request.user
        email_response.save()

        messages.success(
            request, f"Response from {email_response.hoa.name} marked as reviewed."
        )

        return redirect("hoa_detail", hoa_id=email_response.hoa.id)

    except Exception as e:
        messages.error(request, f"Error marking response as reviewed: {str(e)}")
        return redirect("hoa_list")


def email_response_detail(request, response_id):
    """
    Display full email response with parsing and response generation options
    """
    email_response = get_object_or_404(EmailResponse, id=response_id)

    context = {
        "email_response": email_response,
        "hoa": email_response.hoa,
    }

    return render(request, "hoa_management/email_response_detail.html", context)


@require_http_methods(["POST"])
def parse_and_generate_response(request, response_id):
    """
    Parse email response and generate automated response using Gemini AI
    """
    email_response = get_object_or_404(EmailResponse, id=response_id)

    try:
        # Initialize Gemini analyzer
        analyzer = GeminiEmailAnalyzer()

        # Process the email response
        success = analyzer.process_email_response(email_response)

        if success:
            # Get the analysis result for display
            analysis = email_response.ai_analysis_result or {}
            category = analysis.get("category", "unknown")
            confidence = analysis.get("confidence", 0)

            messages.success(
                request,
                f"✅ AI Analysis Complete! "
                f"Category: {category.replace('_', ' ').title()} "
                f"(Confidence: {confidence}%). "
                f"Generated response is ready for review.",
            )
        else:
            messages.error(
                request,
                f"❌ Failed to process email response from {email_response.hoa.name}. "
                f"Please check the logs for details.",
            )

    except ValueError as e:
        # Handle missing API key
        messages.error(
            request,
            f"⚙️ Configuration Error: {str(e)}. "
            f"Please configure GEMINI_API_KEY in your environment.",
        )
    except Exception as e:
        # Handle other errors
        messages.error(
            request,
            f"❌ Error processing email: {str(e)}. "
            f"Please try again or check the logs.",
        )

    return redirect("email_response_detail", response_id=response_id)


@require_http_methods(["POST"])
def send_generated_response(request, response_id):
    """
    Send the AI-generated response email to the HOA
    """
    email_response = get_object_or_404(EmailResponse, id=response_id)

    # Check if we have a generated response
    if not email_response.ai_generated_response:
        messages.error(
            request,
            "No AI-generated response found. Please run 'Parse and Generate Response' first.",
        )
        return redirect("email_response_detail", response_id=response_id)

    # Check if already sent
    if email_response.generated_response_sent:
        messages.warning(
            request,
            f"Generated response was already sent on {email_response.generated_response_sent_at.strftime('%Y-%m-%d %H:%M')}.",
        )
        return redirect("email_response_detail", response_id=response_id)

    try:
        email_service = EmailService()

        # Prepare the email
        subject = f"Re: {email_response.subject}"
        body = email_response.ai_generated_response

        # For demo purposes, redirect to demo email (same logic as original onboarding)
        default_demo_email = "raghv@mainstay.io"
        demo_email = default_demo_email  # TODO: Could be enhanced to remember user's custom demo email

        # Send the email with proper threading headers
        result = email_service.send_email(
            to_email=demo_email,
            subject=subject,
            body=body,
            is_html=True,
            reply_to="4c17207b2cb109e33fb619e01b59252c@inbound.postmarkapp.com",
            in_reply_to=email_response.message_id,
            references=email_response.message_id,
        )

        if result["success"]:
            # Mark as sent
            email_response.generated_response_sent = True
            email_response.generated_response_sent_at = timezone.now()
            email_response.save()

            messages.success(
                request,
                f"✅ AI-generated response sent successfully! "
                f"📧 Demo email sent to: {demo_email} "
                f"(Original HOA: {email_response.hoa.contact_email})",
            )
        else:
            messages.error(
                request, f"❌ Failed to send generated response: {result['message']}"
            )

    except Exception as e:
        messages.error(request, f"❌ Error sending generated response: {str(e)}")

    return redirect("email_response_detail", response_id=response_id)
