import os
import sys
import django
import hashlib
from pathlib import Path

# Add backend to path
backend_path = os.path.join(os.getcwd(), 'backend')
if backend_path not in sys.path:
    sys.path.append(backend_path)
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sura_smart_backend.settings')
django.setup()

from ai_models.facial_recognition.models import MissingPerson, FacialRecognitionImage
from ai_models.facial_recognition.views import _extract_embedding, _cosine_similarity

def verify_match(image_path):
    print(f"Verifying image: {image_path}")
    if not os.path.exists(image_path):
        print("Error: Image path not found.")
        return

    with open(image_path, 'rb') as f:
        image_bytes = f.read()
    
    query_embedding = _extract_embedding(image_bytes)
    if query_embedding is None:
        print("Error: No face detected in query image.")
        return

    db_images = FacialRecognitionImage.objects.filter(status='completed').exclude(face_embedding__isnull=True)
    print(f"Searching across {db_images.count()} indexed images...")

    results = []
    for db_img in db_images:
        # face_embedding is stored as a list (JSONField)
        score = _cosine_similarity(query_embedding, db_img.face_embedding)
        results.append((score, db_img))

    results.sort(key=lambda x: x[0], reverse=True)

    print("\nTop 5 Potential Matches:")
    for i, (score, db_img) in enumerate(results[:5]):
        person = db_img.missing_person
        print(f"[{i+1}] Confidence: {score:.4f} | Person: {person.full_name} ({person.id}) | Source Database: {person.status}")
        print(f"    Image Hash (DB): {db_img.image_hash}")
        # print(f"    Match Image ID: {db_img.id}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        # Default test with one of the indexed images
        test_path = r"d:\SuraSmart_Project\data\vgg_face2\samples\loose_crop (release version)\n008937\0001_01.jpg"
        if os.path.exists(test_path):
            verify_match(test_path)
        else:
            print("Usage: python verify_ai.py <image_path>")
    else:
        verify_match(sys.argv[1])
