import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sura_smart_backend.settings')
django.setup()

from users.models import User

try:
    user = User.objects.get(username='chakin')
    new_password = 'Admin@123'
    user.set_password(new_password)
    user.save()
    
    is_correct = user.check_password(new_password)
    print(f"User: {user.username}")
    print(f"Password reset to '{new_password}'")
    print(f"Check Password Result: {is_correct}")

except Exception as e:
    print(f"Error: {e}")
