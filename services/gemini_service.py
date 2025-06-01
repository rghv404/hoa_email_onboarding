import json
import logging

from django.conf import settings
from django.utils import timezone
from google import genai

from hoa_management.models import HOA, EmailResponse

logger = logging.getLogger(__name__)


class GeminiEmailAnalyzer:
    """
    Service class for analyzing HOA email responses using Google Gemini AI
    and generating appropriate follow-up responses.
    """

    # Response categories
    COMPLETE_RESPONSE = "complete_response"
    REQUESTING_CLARIFICATION = "requesting_clarification"
    INCOMPLETE_RESPONSE = "incomplete_response"
    NO_PROPERTY_MANAGEMENT = "no_property_management"
    PARTIAL_PROPERTY_MANAGEMENT = "partial_property_management"

    def __init__(self):
        """Initialize the Gemini client"""
        if not settings.GEMINI_API_KEY:
            raise ValueError("GEMINI_API_KEY not configured in settings")

        # Create the Gemini client
        self.client = genai.Client(api_key=settings.GEMINI_API_KEY)

    def analyze_email_response(self, email_response: EmailResponse) -> dict:
        """
        Analyze an HOA email response and categorize it into one of the 5 scenarios.

        Args:
            email_response: EmailResponse object to analyze

        Returns:
            Dictionary containing analysis results
        """
        try:
            # Get the email content
            content = email_response.text_content or email_response.html_content or ""

            # Create the analysis prompt
            analysis_prompt = self._create_analysis_prompt(email_response.hoa, content)

            # Call Gemini API
            response = self.client.models.generate_content(
                model="gemini-2.0-flash-001", contents=analysis_prompt
            )

            # Parse the response
            analysis_result = self._parse_analysis_response(response.text)

            logger.info(f"Successfully analyzed email response {email_response.id}")
            return analysis_result

        except Exception as e:
            logger.error(
                f"Error analyzing email response {email_response.id}: {str(e)}"
            )
            return {
                "category": "error",
                "confidence": 0,
                "extracted_data": {},
                "reasoning": f"Error during analysis: {str(e)}",
            }

    def generate_follow_up_response(
        self, email_response: EmailResponse, analysis_result: dict
    ) -> tuple[str, str]:
        """
        Generate an appropriate follow-up email response based on the analysis.

        Args:
            email_response: EmailResponse object
            analysis_result: Result from analyze_email_response

        Returns:
            Tuple of (email_subject, email_body, reasoning)
        """
        try:
            _ = analysis_result.get("category", "")

            # Create the response generation prompt
            response_prompt = self._create_response_prompt(
                email_response.hoa,
                email_response.text_content or email_response.html_content,
                analysis_result,
            )

            # Call Gemini API
            response = self.client.models.generate_content(
                model="gemini-2.0-flash-001", contents=response_prompt
            )

            # Parse the response
            email_content = self._parse_response_generation(response.text)

            logger.info(
                f"Successfully generated response for email {email_response.id}"
            )
            return email_content

        except Exception as e:
            logger.error(
                f"Error generating response for email {email_response.id}: {str(e)}"
            )
            return (
                f"Re: {email_response.subject}",
                "Thank you for your response. We will review it and get back to you soon.",
                f"Error during response generation: {str(e)}",
            )

    def _create_analysis_prompt(self, hoa: HOA, email_content: str) -> str:
        """Create the prompt for email analysis"""

        required_questions = [
            "Property management confirmation (Do you manage the listed properties?)",
            "Regular dues amount",
            "Payment method preference",
            "Payment address (mailing address for payments)",
            "Master HOA name (if applicable)",
            "Phone number for HOA business",
            "Management company name (if applicable)",
        ]

        prompt = f"""
You are an AI assistant helping to analyze HOA (Homeowners Association) email responses.

HOA Information:
- Name: {hoa.name}
- Contact Email: {hoa.contact_email}
- Properties Count: {hoa.properties.count()}

We sent this HOA an email asking for the following information:
{chr(10).join(f"- {q}" for q in required_questions)}

Here is their email response:
---
{email_content}
---

Please analyze this response and categorize it into ONE of these scenarios:

1. "complete_response": HOA has answered ALL required questions clearly
2. "requesting_clarification": HOA is asking for more details/clarification before answering
3. "incomplete_response": HOA answered SOME but not all required questions
4. "no_property_management": HOA states they don't manage any properties
5. "partial_property_management": HOA manages some but not all properties in our database

For each answered question, extract the specific information provided.

Respond in this exact JSON format:
{{
    "category": "one_of_the_five_categories_above",
    "confidence": 85,
    "extracted_data": {{
        "manages_properties": true/false/null,
        "properties_confirmation": "extracted text or null",
        "regular_dues_amount": "extracted amount or null",
        "payment_method": "extracted method or null",
        "payment_address": "extracted address or null",
        "master_hoa_name": "extracted name or null",
        "phone_number": "extracted phone or null",
        "management_company": "extracted company or null"
    }},
    "reasoning": "Brief explanation of why you chose this category and what information was found"
}}
"""
        return prompt

    def _create_response_prompt(
        self, hoa: HOA, original_content: str, analysis_result: dict
    ) -> str:
        """Create the prompt for response generation"""

        category = analysis_result.get("category", "")
        extracted_data = analysis_result.get("extracted_data", {})

        prompt = f"""
You are an AI assistant helping to generate professional follow-up emails to HOAs.

HOA Information:
- Name: {hoa.name}
- Contact Email: {hoa.contact_email}

Original HOA Response:
---
{original_content}
---

Analysis Result:
- Category: {category}
- Extracted Data: {json.dumps(extracted_data, indent=2)}

Based on the category "{category}", generate an appropriate follow-up email response:

CATEGORY-SPECIFIC INSTRUCTIONS:

If "complete_response":
- Thank them for providing all the information
- Ask them to add our contact for future communications regarding this property
- Use "Property Management Team (raghv@mainstay.io)" as the contact to add
- Confirm we have all needed details

If "requesting_clarification":
- Address their specific questions/concerns
- Provide the clarification they requested
- Re-ask for the original information we need

If "incomplete_response":
- Thank them for the partial information
- Politely ask for the missing information with specific explanations
- Example: "Please share the payment address - this helps us make timely payments"

If "no_property_management":
- Thank them for clarifying
- Ask them to ignore our email
- Apologize for any confusion

If "partial_property_management":
- Confirm which properties they don't manage
- Ask for verification of this detail
- Request information only for properties they do manage

RESPONSE REQUIREMENTS:
- Professional and courteous tone
- Reference their original response appropriately
- Be specific about what information is still needed
- Keep it concise but complete
- Use HTML format for better presentation
- When asking to add contact information, use "Property Management Team (raghv@mainstay.io)"
- Sign emails as "Property Management Team"

Respond in this exact JSON format:
{{
    "subject": "Re: Property Management Information Request - {hoa.name}",
    "body": "HTML formatted email body",
    "reasoning": "Brief explanation of the response strategy"
}}
"""
        return prompt

    def _parse_analysis_response(self, response_text: str) -> dict:
        """Parse the JSON response from Gemini analysis"""
        try:
            # Clean up the response text
            response_text = response_text.strip()
            if response_text.startswith("```json"):
                response_text = response_text[7:]
            if response_text.endswith("```"):
                response_text = response_text[:-3]

            return json.loads(response_text)
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse analysis response: {e}")
            return {
                "category": "error",
                "confidence": 0,
                "extracted_data": {},
                "reasoning": f"Failed to parse AI response: {str(e)}",
            }

    def _parse_response_generation(self, response_text: str) -> tuple[str, str, str]:
        """Parse the JSON response from Gemini response generation"""
        try:
            # Clean up the response text
            response_text = response_text.strip()
            if response_text.startswith("```json"):
                response_text = response_text[7:]
            if response_text.endswith("```"):
                response_text = response_text[:-3]

            parsed = json.loads(response_text)
            return (
                parsed.get("subject", "Re: Property Management Information Request"),
                parsed.get("body", "Thank you for your response."),
                parsed.get("reasoning", "Generated response based on AI analysis"),
            )
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse response generation: {e}")
            return (
                "Re: Property Management Information Request",
                "Thank you for your response. We will review it and get back to you soon.",
                f"Failed to parse AI response: {str(e)}",
            )

    def process_email_response(self, email_response: EmailResponse) -> bool:
        """
        Complete processing of an email response: analyze and generate follow-up.

        Args:
            email_response: EmailResponse object to process

        Returns:
            Boolean indicating success
        """
        try:
            # Analyze the email
            analysis_result = self.analyze_email_response(email_response)

            # Generate follow-up response
            subject, body, reasoning = self.generate_follow_up_response(
                email_response, analysis_result
            )

            # Update the email response object
            email_response.ai_analysis_result = analysis_result
            email_response.ai_generated_response = body
            email_response.ai_reasoning = reasoning
            email_response.ai_processed_at = timezone.now()

            # Update extracted data fields
            extracted_data = analysis_result.get("extracted_data", {})
            if extracted_data.get("manages_properties") is not None:
                email_response.manages_properties = extracted_data["manages_properties"]
            if extracted_data.get("properties_confirmation"):
                email_response.properties_confirmation = extracted_data[
                    "properties_confirmation"
                ]
            if extracted_data.get("regular_dues_amount"):
                email_response.regular_dues_amount = extracted_data[
                    "regular_dues_amount"
                ]
            if extracted_data.get("payment_method"):
                email_response.payment_method = extracted_data["payment_method"]
            if extracted_data.get("payment_address"):
                email_response.payment_address = extracted_data["payment_address"]
            if extracted_data.get("master_hoa_name"):
                email_response.master_hoa_name = extracted_data["master_hoa_name"]
            if extracted_data.get("phone_number"):
                email_response.phone_number = extracted_data["phone_number"]
            if extracted_data.get("management_company"):
                email_response.management_company = extracted_data["management_company"]

            # Calculate completeness score
            email_response.response_completeness_score = (
                self._calculate_completeness_score(extracted_data)
            )

            email_response.save()

            logger.info(f"Successfully processed email response {email_response.id}")
            return True

        except Exception as e:
            logger.error(
                f"Error processing email response {email_response.id}: {str(e)}"
            )
            return False

    def _calculate_completeness_score(self, extracted_data: dict) -> int:
        """Calculate completeness score based on answered questions"""
        total_questions = 7
        answered_questions = 0

        required_fields = [
            "manages_properties",
            "regular_dues_amount",
            "payment_method",
            "payment_address",
            "phone_number",
        ]

        optional_fields = ["master_hoa_name", "management_company"]

        # Count required fields
        for field in required_fields:
            if (
                extracted_data.get(field) is not None
                and extracted_data.get(field) != ""
            ):
                answered_questions += 1

        # Count optional fields (weighted less)
        for field in optional_fields:
            if (
                extracted_data.get(field) is not None
                and extracted_data.get(field) != ""
            ):
                answered_questions += 0.5

        return min(100, int((answered_questions / total_questions) * 100))
