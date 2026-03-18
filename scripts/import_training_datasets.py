#!/usr/bin/env python
import os
import sys
import django
import logging
import hashlib
from pathlib import Path
from django.core.files import File

# Add backend to path
sys.path.append(os.path.join(os.getcwd(), 'backend'))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sura_smart_backend.settings')
django.setup()

from ai_models.facial_recognition.models import MissingPerson, FacialRecognitionImage
from users.models import User

logger = logging.getLogger(__name__)

def _get_deepface():
    try:
        from deepface import DeepFace
        return DeepFace
    except ImportError:
        print("DeepFace not found. Using simulated embeddings.")
        return None

def _extract_embedding(image_path, model_name="Facenet512"):
    DeepFace = _get_deepface()
    if DeepFace is None:
        # Simulated embedding based on file hash
        with open(image_path, 'rb') as f:
            h = hashlib.sha256(f.read()).digest()
        dummy = []
        for i in range(16):
            part = hashlib.sha256(h + str(i).encode()).digest()
            dummy.extend([float(b) / 255.0 for b in part])
        return dummy[:512]
    
    try:
        # Using Facenet512 as per views.py
        result = DeepFace.represent(
            img_path=str(image_path),
            model_name=model_name,
            enforce_detection=False,
            detector_backend="opencv"
        )
        if result and len(result) > 0:
            return result[0]["embedding"]
    except Exception as e:
        print(f"Embedding error for {image_path}: {e}")
    return None

def import_vgg_samples():
    # 1. Get/Create system user
    user, _ = User.objects.get_or_create(
        username='system_importer',
        defaults={'email': 'system@surasmart.ai', 'role': 'admin'}
    )

    # 2. Path to samples
    vgg_base = Path(r"d:\SuraSmart_Project\data\vgg_face2\samples\loose_crop (release version)")
    if not vgg_base.exists():
        print(f"VGG Base path not found: {vgg_base}")
        return

    identities = [d for d in vgg_base.iterdir() if d.is_dir()]
    print(f"Found {len(identities)} identities in VGGFace2 samples.")

    for identity_dir in identities:
        identity_id = identity_dir.name
        print(f"Processing identity: {identity_id}")
        
        # Create a MissingPerson record for this identity
        person, created = MissingPerson.objects.get_or_create(
            full_name=f"VGGFace2 Reference {identity_id}",
            defaults={
                'reported_by': user,
                'status': 'TRAINING_DATASET',
                'description': f'Reference identity from VGGFace2 dataset (ID: {identity_id})',
                'jurisdiction': 'KE'
            }
        )
        if created:
            print(f"  Created reference person for {identity_id}")

        # Import all images in the folder
        images = list(identity_dir.glob("*.jpg"))
        print(f"  Found {len(images)} images for {identity_id}")
        for idx, img_path in enumerate(images):
            # Calculate hash to avoid duplicates
            with open(img_path, 'rb') as f:
                img_hash = hashlib.sha256(f.read()).hexdigest()
            
            if FacialRecognitionImage.objects.filter(image_hash=img_hash).exists():
                print(f"  Image {img_path.name} already indexed.")
                continue

            print(f"  Indexing {img_path.name}...")
            embedding = _extract_embedding(img_path)
            
            if embedding:
                with open(img_path, 'rb') as f:
                    django_file = File(f, name=f"vgg_{identity_id}_{img_path.name}")
                    face_img = FacialRecognitionImage.objects.create(
                        missing_person=person,
                        image_file=django_file,
                        image_hash=img_hash,
                        is_primary=(idx == 0),
                        status='completed',
                        face_embedding=embedding,
                        face_confidence=1.0
                    )
                print(f"    Successfully indexed with embedding.")
            else:
                print(f"    Failed to extract embedding for {img_path.name}")

if __name__ == "__main__":
    import_vgg_samples()
