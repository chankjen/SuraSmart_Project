"""Management command to create demo users for testing role-based access control."""
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model

User = get_user_model()


class Command(BaseCommand):
    help = 'Create demo users for different roles'

    def handle(self, *args, **options):
        # Define users to create
        demo_users = [
            # Family Members
            {
                'username': 'alex', 
                'email': 'alex@example.com', 
                'password': 'family123', 
                'role': 'family_member', 
                'first_name': 'Alex',
                'last_name': 'Johnson',
                'national_id': '12345678'
            },
            {
                'username': 'amanda', 
                'email': 'amanda@example.com', 
                'password': 'family123', 
                'role': 'family_member', 
                'first_name': 'Amanda',
                'last_name': 'Smith',
                'national_id': '87654321'
            },
            
            # Police Officers
            {
                'username': 'bernard', 
                'email': 'bernard@example.com', 
                'password': 'police456', 
                'role': 'police_officer', 
                'first_name': 'Bernard',
                'last_name': 'Wilson',
                'service_id': '11111111',
                'police_rank': 'lieutenant'
            },
            {
                'username': 'betty', 
                'email': 'betty@example.com', 
                'password': 'police456', 
                'role': 'police_officer', 
                'first_name': 'Betty',
                'last_name': 'Brown',
                'service_id': '22222222',
                'police_rank': 'general'
            },
            
            # Government Officials
            {
                'username': 'cate', 
                'email': 'cate@example.com', 
                'password': 'official789', 
                'role': 'government_official', 
                'first_name': 'Cate',
                'last_name': 'Davis',
                'government_security_id': '33333333',
                'government_position': 'cs'
            },
            {
                'username': 'dan', 
                'email': 'dan@example.com', 
                'password': 'official789', 
                'role': 'government_official', 
                'first_name': 'Dan',
                'last_name': 'Miller',
                'government_security_id': '44444444',
                'government_position': 'ps'
            },
        ]

        for user_data in demo_users:
            username = user_data['username']
            try:
                user = User.objects.get(username=username)
                # Update existing user with new fields
                user.role = user_data['role']
                user.first_name = user_data['first_name']
                user.last_name = user_data.get('last_name', '')
                user.national_id = user_data.get('national_id')
                user.service_id = user_data.get('service_id')
                user.police_rank = user_data.get('police_rank')
                user.government_security_id = user_data.get('government_security_id')
                user.government_position = user_data.get('government_position')
                user.is_verified = True  # Verify demo users
                user.save()
                self.stdout.write(
                    self.style.SUCCESS(
                        f'Updated user {username} ({user_data["role"]})'
                    )
                )
            except User.DoesNotExist:
                user = User.objects.create_user(
                    username=username,
                    email=user_data['email'],
                    password=user_data['password'],
                    role=user_data['role'],
                    first_name=user_data['first_name'],
                    last_name=user_data.get('last_name', ''),
                    national_id=user_data.get('national_id'),
                    service_id=user_data.get('service_id'),
                    police_rank=user_data.get('police_rank'),
                    government_security_id=user_data.get('government_security_id'),
                    government_position=user_data.get('government_position'),
                    is_verified=True,  # Verify demo users
                )
                self.stdout.write(
                    self.style.SUCCESS(
                        f'Created user {username} ({user_data["role"]}) with password {user_data["password"]}'
                    )
                )

        self.stdout.write(self.style.SUCCESS('\n=== Demo Users Created ==='))
        self.stdout.write('\nFamily Members (family_member):')
        self.stdout.write('  - alex / family123 (National ID: 12345678)')
        self.stdout.write('  - amanda / family123 (National ID: 87654321)')
        self.stdout.write('\nPolice Officers (police_officer):')
        self.stdout.write('  - bernard / police456 (Service ID: 11111111, Rank: Lieutenant)')
        self.stdout.write('  - betty / police456 (Service ID: 22222222, Rank: General)')
        self.stdout.write('\nGovernment Officials (government_official):')
        self.stdout.write('  - cate / official789 (Security ID: 33333333, Position: CS)')
        self.stdout.write('  - dan / official789 (Security ID: 44444444, Position: PS)')
