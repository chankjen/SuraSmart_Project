import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sura_smart_backend.settings')
django.setup()

from users.models import User

try:
    user = User.objects.get(username='chakin')
    passwords_to_test = ['Admin@123', 'Zenith@1234#', 'password123']
    
    print(f"User: {user.username}")
    print(f"Role: {user.role}")
    
    for pwd in passwords_to_test:
        is_correct = user.check_password(pwd)
        print(f"Checking '{pwd}': {is_correct}")

except Exception as e:
    print(f"Error: {e}")
