from django.urls import path

from . import views

urlpatterns = [
    path("", views.dashboard, name="dashboard"),
    path("hoas/", views.hoa_list, name="hoa_list"),
    path("hoas/<int:hoa_id>/", views.hoa_detail, name="hoa_detail"),
    path("hoas/<int:hoa_id>/email-preview/", views.email_preview, name="email_preview"),
    path("hoas/<int:hoa_id>/send-email/", views.send_email, name="send_email"),
    path(
        "hoas/<int:hoa_id>/send-email-ajax/",
        views.send_email_ajax,
        name="send_email_ajax",
    ),
    path("webhook/postmark-inbound/", views.postmark_webhook, name="postmark_webhook"),
    path(
        "responses/<int:response_id>/mark-reviewed/",
        views.mark_response_reviewed,
        name="mark_response_reviewed",
    ),
    path(
        "responses/<int:response_id>/",
        views.email_response_detail,
        name="email_response_detail",
    ),
    path(
        "responses/<int:response_id>/parse-and-generate/",
        views.parse_and_generate_response,
        name="parse_and_generate_response",
    ),
    path(
        "responses/<int:response_id>/send-generated-response/",
        views.send_generated_response,
        name="send_generated_response",
    ),
]
