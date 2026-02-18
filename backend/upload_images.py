#!/usr/bin/env python
"""
Script to upload images from sura_smart/static/uploads/ to the backend database.
"""

import os
import sys
import django
from pathlib import Path
import hashlib

# Add the backend directory to the Python path
backend_dir = Path(__file__).resolve().parent
sys.path.insert(0, str(backend_dir))

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sura_smart_backend.settings')
django.setup()

from facial_recognition.models import MissingPerson, FacialRecognitionImage
from users.models import User
from django.core.files import File

def calculate_sha256(file_path):
    """Calculate SHA256 hash of a file."""
    hash_sha256 = hashlib.sha256()
    with open(file_path, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_sha256.update(chunk)
    return hash_sha256.hexdigest()

def upload_images():
    """Upload the four images to the database."""
    
    # Path to the uploads directory
    uploads_dir = Path(r"d:\SuraSmart_Project\sura_smart\static\uploads")
    
    if not uploads_dir.exists():
        print(f"Uploads directory does not exist: {uploads_dir}")
        return
    
    # Get or create a test user
    user, created = User.objects.get_or_create(
        username='test_user',
        defaults={
            'email': 'test@example.com',
            'first_name': 'Test',
            'last_name': 'User'
        }
    )
    if created:
        user.set_password('password123')
        user.save()
        print("Created test user")
    
    # Get or create a missing person
    missing_person, created = MissingPerson.objects.get_or_create(
        full_name='Test Missing Person',
        defaults={
            'reported_by': user,
            'description': 'Test person for image upload',
            'status': 'reported'
        }
    )
    if created:
        print("Created test missing person")
    
    # List of image files
    image_files = ['chakin.jpg', 'female.jpg', 'female2.jpg', 'male.jpg']
    
    for image_name in image_files:
        image_path = uploads_dir / image_name
        if not image_path.exists():
            print(f"Image not found: {image_path}")
            continue
        
        # Calculate hash
        image_hash = calculate_sha256(image_path)
        
        # Check if image already exists
        if FacialRecognitionImage.objects.filter(image_hash=image_hash).exists():
            print(f"Image {image_name} already exists in database")
            continue
        
        # Create FacialRecognitionImage instance
        with open(image_path, 'rb') as f:
            django_file = File(f, name=image_name)
            facial_image = FacialRecognitionImage.objects.create(
                missing_person=missing_person,
                image_file=django_file,
                image_hash=image_hash,
                is_primary=False,
                status='uploaded'
            )
            print(f"Uploaded image: {image_name} -> {facial_image.image_file.name}")

if __name__ == '__main__':
    upload_images()