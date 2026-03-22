import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sura_smart_backend.settings')
django.setup()

from users.models import User

try:
    users = User.objects.all()
    print(f"Total Users: {users.count()}")
    for u in users:
        if u.role == 'admin' or u.is_staff or u.is_superuser:
             print(f"- [ADMIN/STAFF] {u.username} (Role: {u.role})")
        else:
             print(f"- {u.username} (Role: {u.role})")
             
except Exception as e:
    print(f"Error: {e}")
