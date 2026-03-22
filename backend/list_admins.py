import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sura_smart_backend.settings')
django.setup()

from users.models import User

try:
    admins = User.objects.filter(role='admin')
    print(f"Total Admins: {admins.count()}")
    for admin in admins:
        print(f"Username: {admin.username}, Email: {admin.email}, Staff: {admin.is_staff}, Superuser: {admin.is_superuser}")
        
except Exception as e:
    print(f"Error: {e}")
