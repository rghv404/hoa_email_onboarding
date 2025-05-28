import random
from decimal import Decimal
from datetime import date, timedelta
from django.core.management.base import BaseCommand
from faker import Faker
from hoa_management.models import HOA, Property


class Command(BaseCommand):
    help = 'Populate the database with sample HOA and property data'

    def add_arguments(self, parser):
        parser.add_argument(
            '--hoas',
            type=int,
            default=15,
            help='Number of HOAs to create (default: 15)'
        )
        parser.add_argument(
            '--properties-per-hoa',
            type=int,
            default=5,
            help='Average number of properties per HOA (default: 5)'
        )
        parser.add_argument(
            '--clear',
            action='store_true',
            help='Clear existing data before populating'
        )

    def handle(self, *args, **options):
        fake = Faker()
        
        if options['clear']:
            self.stdout.write('Clearing existing data...')
            Property.objects.all().delete()
            HOA.objects.all().delete()
            self.stdout.write(self.style.SUCCESS('Existing data cleared.'))

        num_hoas = options['hoas']
        avg_properties = options['properties_per_hoa']

        self.stdout.write(f'Creating {num_hoas} HOAs with an average of {avg_properties} properties each...')

        # Sample management companies
        management_companies = [
            'Premier Property Management',
            'Community Management Associates',
            'HOA Management Solutions',
            'Residential Management Group',
            'Elite Community Services',
            None,  # Some HOAs self-manage
        ]

        # Create HOAs
        hoas = []
        for i in range(num_hoas):
            hoa = HOA.objects.create(
                name=f"{fake.city()} {random.choice(['Heights', 'Gardens', 'Village', 'Estates', 'Commons', 'Ridge', 'Park'])} HOA",
                address=fake.address(),
                contact_email=fake.email(),
                phone=fake.phone_number()[:17],  # Ensure it fits the field length
                management_company=random.choice(management_companies),
                website=fake.url() if random.choice([True, False]) else None,
                established_date=fake.date_between(start_date='-30y', end_date='-1y'),
                total_units=random.randint(50, 500),
                monthly_fee_range=f"${random.randint(150, 300)}-${random.randint(350, 600)}"
            )
            hoas.append(hoa)
            
            # Create properties for this HOA
            num_properties = random.randint(max(1, avg_properties - 3), avg_properties + 3)
            
            for j in range(num_properties):
                property_type = random.choice([choice[0] for choice in Property.PROPERTY_TYPES])
                
                # Adjust unit count based on property type
                if property_type == 'single_family':
                    unit_count = 1
                elif property_type == 'townhouse':
                    unit_count = random.randint(1, 3)
                elif property_type == 'condo':
                    unit_count = random.randint(1, 2)
                elif property_type == 'apartment':
                    unit_count = random.randint(4, 50)
                else:
                    unit_count = random.randint(1, 10)
                
                Property.objects.create(
                    hoa=hoa,
                    address=fake.address(),
                    property_type=property_type,
                    unit_count=unit_count,
                    square_footage=random.randint(800, 3500) if random.choice([True, False]) else None,
                    year_built=random.randint(1980, 2023) if random.choice([True, False]) else None,
                    monthly_hoa_fee=Decimal(str(random.randint(150, 600))) if random.choice([True, False]) else None,
                    is_active=random.choice([True, True, True, False])  # 75% active
                )

        self.stdout.write(
            self.style.SUCCESS(
                f'Successfully created {num_hoas} HOAs and {Property.objects.count()} properties.'
            )
        )
