import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sura_smart_backend.settings')
django.setup()

from ai_models.facial_recognition.models import MissingPerson

cases = MissingPerson.objects.filter(full_name__icontains='Maria')
for c in cases:
    print(c.id)
    print("Status:", c.status)
    print("Location:", repr(c.last_seen_location))
    print("Jurisdiction:", c.jurisdiction)
