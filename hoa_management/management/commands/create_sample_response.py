from django.core.management.base import BaseCommand
from hoa_management.models import HOA, EmailResponse


class Command(BaseCommand):
    help = 'Create a sample email response for testing'

    def handle(self, *args, **options):
        # Get the first HOA
        hoa = HOA.objects.first()
        if not hoa:
            self.stdout.write(self.style.ERROR('No HOAs found. Please run populate_hoa_data first.'))
            return

        # Create a sample email response (simplified - no parsing)
        sample_response = EmailResponse.objects.create(
            hoa=hoa,
            message_id='sample-response-123',
            from_email=hoa.contact_email,
            subject=f'Re: Property Management Information Request - {hoa.name}',
            text_content="""Dear Property Management Services Team,

Thank you for reaching out. Here are the answers to your questions:

1. Property Management Verification: Yes, we currently manage all the properties listed in your email.

2. Regular Dues Amount: Our monthly HOA dues are $275 per unit.

3. Preferred Payment Method: We prefer ACH transfers for all payments.

4. Payment Address: Please send all correspondence to:
   Sunset Gardens HOA
   123 Management Way
   Property City, CA 90210

5. Master HOA: There is no master HOA that oversees our association.

6. Phone Number: Our primary business phone number is (555) 123-4567.

7. Management Company: We are currently self-managed.

Please let me know if you need any additional information.

Best regards,
John Smith
Board President
{hoa_name}""".format(hoa_name=hoa.name),
            raw_content='{"sample": "postmark webhook data"}',
            response_completeness_score=0,  # Will be calculated by LLM later
            status='new'
        )

        self.stdout.write(
            self.style.SUCCESS(
                f'Successfully created sample email response for {hoa.name} (ID: {sample_response.id})'
            )
        )
