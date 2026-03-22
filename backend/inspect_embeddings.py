import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sura_smart_backend.settings')
django.setup()

from ai_models.facial_recognition.models import FacialRecognitionImage

images = FacialRecognitionImage.objects.filter(status='completed')
print(f"Total processed images: {images.count()}")

for img in images:
    emb = img.face_embedding
    print(f"ID: {img.id}, Person: {img.missing_person.full_name}, Embedding Hash: {hash(str(emb)) if emb else 'None'}")
    if emb:
         print(f"  First 5 values: {emb[:5]}")
