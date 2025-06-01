import logging

from hoa_management.models import HOA, EmailResponse

logger = logging.getLogger(__name__)


class EmailResponseProcessor:
    """
    Simplified service class for processing inbound email responses from HOAs
    Stores raw email content for later processing with LLM
    """

    def find_hoa_from_email(self, from_email: str, subject: str) -> HOA | None:
        """
        Try to identify which HOA sent the email response
        """
        # First, try to match by email address
        try:
            hoa = HOA.objects.get(contact_email__iexact=from_email)
            return hoa
        except HOA.DoesNotExist:
            pass

        # Try to extract HOA name from subject line if it contains our standard format
        if "Property Management Information Request" in subject and " - " in subject:
            # Simple string split to get HOA name
            parts = subject.split(" - ")
            if len(parts) > 1:
                hoa_name = parts[-1].strip()
                try:
                    hoa = HOA.objects.get(name__iexact=hoa_name)
                    return hoa
                except HOA.DoesNotExist:
                    pass

        # Try partial name matching in subject
        for hoa in HOA.objects.all():
            if hoa.name.lower() in subject.lower():
                return hoa

        logger.warning(
            f"Could not identify HOA for email from {from_email} with subject: {subject}"
        )
        return None

    def process_inbound_email(
        self, postmark_data: dict
    ) -> tuple[bool, str, EmailResponse | None]:
        """
        Process an inbound email from Postmark webhook
        Simplified version that just stores the raw email for later LLM processing

        Args:
            postmark_data: The webhook payload from Postmark

        Returns:
            Tuple of (success, message, email_response_object)
        """
        try:
            # Extract email data from Postmark payload
            from_email = postmark_data.get("From", "")
            subject = postmark_data.get("Subject", "")
            text_body = postmark_data.get("TextBody", "")
            html_body = postmark_data.get("HtmlBody", "")
            message_id = postmark_data.get("MessageID", "")

            # Find the HOA
            hoa = self.find_hoa_from_email(from_email, subject)
            if not hoa:
                return (
                    False,
                    f"Could not identify HOA for email from {from_email}",
                    None,
                )

            # Check if we already processed this email
            if EmailResponse.objects.filter(message_id=message_id).exists():
                return (
                    False,
                    f"Email with message ID {message_id} already processed",
                    None,
                )

            # Create EmailResponse object with just the raw content
            # No parsing for now - will be processed later with LLM
            email_response = EmailResponse.objects.create(
                hoa=hoa,
                message_id=message_id,
                from_email=from_email,
                subject=subject,
                raw_content=str(postmark_data),
                html_content=html_body,
                text_content=text_body,
                response_completeness_score=0,  # Will be calculated by LLM later
                status="new",
            )

            logger.info(
                f"Successfully stored email response from {hoa.name} (ID: {email_response.id})"
            )

            return True, f"Successfully received email from {hoa.name}", email_response

        except Exception as e:
            logger.error(f"Error processing inbound email: {str(e)}")
            return False, f"Error processing email: {str(e)}", None
