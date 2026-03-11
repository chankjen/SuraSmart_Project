#!/usr/bin/env python
"""Django's command-line utility for administrative tasks."""
import os
import sys


def main():
    """Run administrative tasks."""
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sura_smart_backend.settings')
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc
    execute_from_command_line(sys.argv)


if __name__ == '__main__':
    main()

# backend/manage.py shell

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand

User = get_user_model()

# Create Admin User "Chakin"
def create_admin_user():
    if not User.objects.filter(username='chakin').exists():
        admin = User.objects.create_superuser(
            username='chakin',
            email='chakin@surasmart.africa',
            first_name='Chakin',
            last_name='Admin',
            role='admin',
            is_verified=True,
            is_staff=True,
            is_superuser=True
        )
        admin.set_password('Zenith@1234#')  # Will be hashed by Django
        admin.save()
        print('✓ Admin user "Chakin" created successfully')
    else:
        print('⚠ Admin user "Chakin" already exists')

# Run this command:
# python manage.py shell < create_admin.py