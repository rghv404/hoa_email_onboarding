import logging

from django.conf import settings
from postmarker.core import PostmarkClient

from hoa_management.models import HOA

logger = logging.getLogger(__name__)


class EmailService:
    """
    Service class for handling email operations using Postmark
    """

    def __init__(self):
        self.client = None
        if (
            settings.POSTMARK_API_TOKEN
            and settings.POSTMARK_API_TOKEN != "your_postmark_api_token_here"
        ):
            self.client = PostmarkClient(server_token=settings.POSTMARK_API_TOKEN)
        else:
            logger.warning(
                "Postmark API token not configured. Email sending will be simulated."
            )

    def generate_hoa_onboarding_email(self, hoa: HOA) -> dict[str, str]:
        """
        Generate email content for HOA onboarding

        Args:
            hoa: HOA instance to generate email for

        Returns:
            Dictionary containing email subject and body
        """
        properties = hoa.properties.filter(is_active=True)
        property_list = "\n".join(
            [
                f"• {prop.address} ({prop.get_property_type_display()})"
                for prop in properties[:10]
            ]
        )  # Limit to first 10

        if properties.count() > 10:
            property_list += f"\n... and {properties.count() - 10} more properties"

        subject = f"Property Management Information Request - {hoa.name}"

        # Generate property list HTML
        property_list_html = ""
        for prop in properties[:15]:  # Show up to 15 properties
            property_list_html += f"""
                <li style="margin-bottom: 8px;">
                    <strong>{prop.address}</strong><br>
                    <span style="color: #666; font-size: 14px;">Type: {prop.get_property_type_display()}</span>
                    {f'<br><span style="color: #666; font-size: 14px;">Units: {prop.unit_count}</span>' if prop.unit_count > 1 else ""}
                </li>
            """

        if properties.count() > 15:
            property_list_html += f"""
                <li style="margin-bottom: 8px; font-style: italic; color: #666;">
                    ... and {properties.count() - 15} additional properties
                </li>
            """

        body = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Property Management Information Request</title>
</head>
<body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333; max-width: 600px; margin: 0 auto; padding: 20px;">

    <div style="background-color: #f8f9fa; padding: 20px; border-radius: 8px; margin-bottom: 20px;">
        <h2 style="color: #2c3e50; margin-top: 0;">Property Management Information Request</h2>
        <p style="margin-bottom: 0; color: #666;">HOA: <strong>{hoa.name}</strong></p>
    </div>

    <p>Dear {hoa.name} Management Team,</p>

    <p>We hope this email finds you well. We are reaching out to verify and update our records regarding your HOA and the properties you manage.</p>

    <div style="background-color: #e8f4f8; padding: 15px; border-radius: 6px; margin: 20px 0;">
        <h3 style="color: #2c3e50; margin-top: 0;">Current HOA Information</h3>
        <ul style="list-style: none; padding-left: 0;">
            <li><strong>Name:</strong> {hoa.name}</li>
            <li><strong>Contact Email:</strong> {hoa.contact_email}</li>
            <li><strong>Phone:</strong> {hoa.phone or "Not provided"}</li>
            <li><strong>Management Company:</strong> {hoa.management_company or "Self-managed"}</li>
        </ul>
    </div>

    <div style="background-color: #fff3cd; padding: 15px; border-radius: 6px; margin: 20px 0;">
        <h3 style="color: #2c3e50; margin-top: 0;">Properties in Our Records ({properties.count()} total)</h3>
        <ul style="padding-left: 20px;">
            {property_list_html}
        </ul>
    </div>

    <p>To ensure our records are accurate and up-to-date, please provide the following information:</p>

    <div style="background-color: #f8f9fa; padding: 20px; border-radius: 6px; margin: 20px 0;">
        <ol style="padding-left: 20px;">
            <li style="margin-bottom: 15px;">
                <strong>Property Management Verification:</strong><br>
                <span style="color: #666;">Do you currently manage all the properties listed above? If not, please specify which properties should be added or removed.</span>
            </li>

            <li style="margin-bottom: 15px;">
                <strong>Regular Dues Amount:</strong><br>
                <span style="color: #666;">What is the amount of regular HOA dues in dollars (monthly/quarterly/annually)?</span>
            </li>

            <li style="margin-bottom: 15px;">
                <strong>Preferred Payment Method:</strong><br>
                <span style="color: #666;">What is your preferred payment method? (Check, ACH transfer, online payment, wire transfer, etc.)</span>
            </li>

            <li style="margin-bottom: 15px;">
                <strong>Payment Address:</strong><br>
                <span style="color: #666;">What is the mailing address for HOA payments and correspondence?</span>
            </li>

            <li style="margin-bottom: 15px;">
                <strong>Master HOA:</strong><br>
                <span style="color: #666;">Is there a master HOA that oversees your HOA? If yes, please provide the name.</span>
            </li>

            <li style="margin-bottom: 15px;">
                <strong>Phone Number:</strong><br>
                <span style="color: #666;">Please confirm or provide the primary phone number for HOA business.</span>
            </li>

            <li style="margin-bottom: 15px;">
                <strong>Management Company:</strong><br>
                <span style="color: #666;">Please confirm the name of your management company, or indicate if the HOA is self-managed.</span>
            </li>
        </ol>
    </div>

    <p>Please reply to this email with the requested information at your earliest convenience. Your prompt response will help us maintain accurate records and ensure smooth communication.</p>

    <div style="background-color: #e3f2fd; padding: 15px; border-radius: 6px; margin: 20px 0;">
        <p style="margin: 0; font-size: 14px;"><strong>How to respond:</strong></p>
        <p style="margin: 5px 0 0 0; color: #666; font-size: 14px;">
            Simply reply to this email with your answers. Our system will automatically process your response and update our records.
        </p>
    </div>

    <div style="background-color: #d4edda; padding: 15px; border-radius: 6px; margin: 20px 0;">
        <p style="margin: 0;"><strong>Thank you for your cooperation!</strong></p>
        <p style="margin: 5px 0 0 0; color: #666;">We value our relationship with {hoa.name} and appreciate your time in helping us update our records.</p>
    </div>

    <hr style="border: none; border-top: 1px solid #eee; margin: 30px 0;">

    <div style="text-align: center; color: #666; font-size: 14px;">
        <p><strong>Property Management Services Team</strong><br>
        Email: {settings.POSTMARK_FROM_EMAIL}</p>

        <p style="font-size: 12px; margin-top: 20px;">
            This email was sent to verify and update property management records.<br>
            If you received this email in error, please contact us immediately.
        </p>
    </div>

</body>
</html>"""

        return {"subject": subject, "body": body}

    def send_email(
        self,
        to_email: str,
        subject: str,
        body: str,
        from_email: str | None = None,
        is_html: bool = False,
        reply_to: str | None = None,
        in_reply_to: str | None = None,
        references: str | None = None,
    ) -> dict[str, any]:
        """
        Send email using Postmark

        Args:
            to_email: Recipient email address
            subject: Email subject
            body: Email body (plain text or HTML)
            from_email: Sender email (optional, uses default if not provided)
            is_html: Whether the body is HTML format
            reply_to: Reply-to email address (optional)
            in_reply_to: Message ID this email is replying to (for threading)
            references: References header for email threading

        Returns:
            Dictionary with success status and message
        """
        if not from_email:
            from_email = settings.POSTMARK_FROM_EMAIL

        if not self.client:
            # Simulate email sending for development/testing
            logger.info("SIMULATED EMAIL SEND:")
            logger.info(f"To: {to_email}")
            logger.info(f"From: {from_email}")
            logger.info(f"Subject: {subject}")
            logger.info(f"Body: {body[:200]}...")

            return {
                "success": True,
                "message": "Email simulated successfully (Postmark not configured)",
                "message_id": "simulated-" + str(hash(f"{to_email}{subject}")),
            }

        try:
            email_data = {
                "From": from_email,
                "To": to_email,
                "Subject": subject,
            }

            if reply_to:
                email_data["ReplyTo"] = reply_to

            # Add threading headers for email conversation
            headers = []
            if in_reply_to:
                headers.append({"Name": "In-Reply-To", "Value": in_reply_to})
            if references:
                headers.append({"Name": "References", "Value": references})

            if headers:
                email_data["Headers"] = headers

            if is_html:
                email_data["HtmlBody"] = body
            else:
                email_data["TextBody"] = body

            response = self.client.emails.send(**email_data)

            logger.info(
                f"Email sent successfully to {to_email}. Message ID: {response['MessageID']}"
            )

            return {
                "success": True,
                "message": "Email sent successfully. Note the email was actually sent to ",
                "message_id": response["MessageID"],
            }

        except Exception as e:
            logger.error(f"Failed to send email to {to_email}: {str(e)}")

            return {
                "success": False,
                "message": f"Failed to send email: {str(e)}",
                "message_id": None,
            }

    def send_hoa_onboarding_email(
        self, hoa: HOA, demo_email: str | None = None
    ) -> dict[str, any]:
        """
        Generate and send onboarding email to an HOA
        For demo purposes, all emails are redirected to a demo email address

        Args:
            hoa: HOA instance to send email to
            demo_email: Optional custom demo email address (defaults to raghv@mainstay.io)

        Returns:
            Dictionary with success status and message
        """
        email_content = self.generate_hoa_onboarding_email(hoa)

        # Demo email redirection
        default_demo_email = "raghv@mainstay.io"
        target_email = demo_email or default_demo_email
        original_email = hoa.contact_email

        logger.info(
            f"DEMO MODE: Redirecting email from {original_email} to {target_email}"
        )

        result = self.send_email(
            to_email=target_email,
            subject=email_content["subject"],
            body=email_content["body"],
            is_html=True,
            reply_to="4c17207b2cb109e33fb619e01b59252c@inbound.postmarkapp.com",
        )

        # Add demo information to the result
        result["demo_email"] = target_email
        result["original_email"] = original_email
        result["is_custom_demo_email"] = demo_email is not None

        return result
