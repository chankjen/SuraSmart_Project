import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sura_smart_backend.settings')
django.setup()

from django.contrib.auth import authenticate

username = 'chakin'
password = 'Admin@123'

user = authenticate(username=username, password=password)

if user is not None:
    print(f"AUTHENTICATION SUCCESS for user: {user.username}")
    print(f"Role: {getattr(user, 'role', 'N/A')}")
else:
    print(f"AUTHENTICATION FAILED for user: {username}")
    # List first 3 users just to see usernames
    from users.models import User
    print("User list (first 3):")
    for u in User.objects.all()[:3]:
        print(f"- {u.username}")
