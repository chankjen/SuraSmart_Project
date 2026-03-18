import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sura_smart_backend.settings')
django.setup()

from ai_models.facial_recognition.models import MissingPerson

cases = MissingPerson.objects.filter(full_name__icontains='Maria')
for c in cases:
    print(f"ID: {c.id}, Name: {c.full_name}, Location: '{c.last_seen_location}'")
