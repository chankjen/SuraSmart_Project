import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sura_smart_backend.settings')
django.setup()

from ai_models.facial_recognition.models import FacialRecognitionImage
from ai_models.facial_recognition.views import _extract_embedding, _bytes_from_file

images = FacialRecognitionImage.objects.all()
print(f"Re-processing {images.count()} images...")

count = 0
for img in images:
    if img.image_file:
        try:
            image_bytes = _bytes_from_file(img.image_file)
            new_embedding = _extract_embedding(image_bytes)
            if new_embedding:
                img.face_embedding = new_embedding
                img.status = 'completed'
                img.save()
                count += 1
                if count % 10 == 0:
                     print(f"Processed {count} images...")
        except Exception as e:
            print(f"Failed to process image {img.id}: {e}")

print(f"Successfully re-processed {count} images with new dHash logic.")
