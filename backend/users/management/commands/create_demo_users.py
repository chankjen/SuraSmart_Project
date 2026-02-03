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
            {'username': 'alex', 'email': 'alex@example.com', 'password': 'family123', 'role': 'family_member', 'first_name': 'Alex'},
            {'username': 'amanda', 'email': 'amanda@example.com', 'password': 'family123', 'role': 'family_member', 'first_name': 'Amanda'},
            
            # Police Officers
            {'username': 'bernard', 'email': 'bernard@example.com', 'password': 'police456', 'role': 'police_officer', 'first_name': 'Bernard'},
            {'username': 'betty', 'email': 'betty@example.com', 'password': 'police456', 'role': 'police_officer', 'first_name': 'Betty'},
            
            # Government Officials
            {'username': 'cate', 'email': 'cate@example.com', 'password': 'official789', 'role': 'government_official', 'first_name': 'Cate'},
            {'username': 'dan', 'email': 'dan@example.com', 'password': 'official789', 'role': 'government_official', 'first_name': 'Dan'},
        ]

        for user_data in demo_users:
            username = user_data['username']
            if User.objects.filter(username=username).exists():
                self.stdout.write(self.style.WARNING(f'User {username} already exists'))
            else:
                user = User.objects.create_user(
                    username=username,
                    email=user_data['email'],
                    password=user_data['password'],
                    role=user_data['role'],
                    first_name=user_data['first_name'],
                )
                self.stdout.write(
                    self.style.SUCCESS(
                        f'Created user {username} ({user_data["role"]}) with password {user_data["password"]}'
                    )
                )

        self.stdout.write(self.style.SUCCESS('\n=== Demo Users Created ==='))
        self.stdout.write('\nFamily Members (family_member):')
        self.stdout.write('  - alex / family123')
        self.stdout.write('  - amanda / family123')
        self.stdout.write('\nPolice Officers (police_officer):')
        self.stdout.write('  - bernard / police456')
        self.stdout.write('  - betty / police456')
        self.stdout.write('\nGovernment Officials (government_official):')
        self.stdout.write('  - cate / official789')
        self.stdout.write('  - dan / official789')
