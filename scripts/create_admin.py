# backend/create_admin.py
import os
import sys
import django
import getpass

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
django.setup()

from django.contrib.auth import get_user_model

User = get_user_model()

def create_admin_user():
    username = 'chakin'
    email = 'chakin@surasmart.africa'
    
    if User.objects.filter(username=username).exists():
        print(f"⚠️  Admin user '{username}' already exists.")
        return

    # Secure Password Entry
    print(f"Creating admin user: {username}")
    password = getpass.getpass("Enter password for Chakin (will not echo): ")
    confirm_password = getpass.getpass("Confirm password: ")

    if password != confirm_password:
        print("❌ Passwords do not match.")
        return

    if len(password) < 8:
        print("❌ Password must be at least 8 characters.")
        return

    # Create User
    admin = User.objects.create_superuser(
        username=username,
        email=email,
        first_name='Chakin',
        last_name='Admin',
        role='admin',
        is_verified=True,
        is_staff=True,
        is_superuser=True
    )
    admin.set_password(password) # Hashes the password
    admin.save()
    
    print(f"✅ Admin user '{username}' created successfully.")
    print("🔒 Password has been securely hashed.")

if __name__ == '__main__':
    create_admin_user()