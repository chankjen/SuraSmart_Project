import os
import sys
import django

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "sura_smart_backend.settings")
django.setup()

from users.models import User

print("Total Users:", User.objects.count())
print("Verified:", User.objects.filter(verification_status='verified').count())
print("Pending:", User.objects.filter(verification_status='pending').count())

admin = User.objects.filter(username='chakin').first()
if admin:
    print(f"Admin 'chakin': role={admin.role}, is_staff={admin.is_staff}, is_superuser={admin.is_superuser}")
else:
    print("Admin 'chakin' not found")
