#!/usr/bin/env python
"""
Script to assign metadata (Name, Age, Gender, Last_Location) to the uploaded images.
"""

import os
import sys
import django
from pathlib import Path

# Add the backend directory to the Python path
backend_dir = Path(__file__).resolve().parent
sys.path.insert(0, str(backend_dir))

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sura_smart_backend.settings')
django.setup()

from facial_recognition.models import MissingPerson, FacialRecognitionImage
from users.models import User
from django.utils import timezone

def assign_image_metadata():
    """Assign metadata to the uploaded images by creating distinct missing persons."""
    
    # Get or create the test user
    user, _ = User.objects.get_or_create(
        username='test_user',
        defaults={
            'email': 'test@example.com',
            'first_name': 'Test',
            'last_name': 'User'
        }
    )
    
    # Image metadata mapping
    image_metadata = {
        'chakin.jpg': {
            'name': 'Andrew Ken',
            'age': 25,
            'gender': 'male',
            'location': 'Thika Prison'
        },
        'female.jpg': {
            'name': 'Mary Johnson',
            'age': 32,
            'gender': 'female',
            'location': 'Nairobi City Center'
        },
        'female2.jpg': {
            'name': 'Sarah Williams',
            'age': 28,
            'gender': 'female',
            'location': 'Mombasa Beach'
        },
        'male.jpg': {
            'name': 'James Thompson',
            'age': 35,
            'gender': 'male',
            'location': 'Kisumu Market'
        }
    }
    
    # Get all uploaded facial recognition images
    images = FacialRecognitionImage.objects.all().order_by('created_at')
    
    if not images.exists():
        print("No images found in the database.")
        return
    
    image_list = list(images)
    image_files = ['chakin.jpg', 'female.jpg', 'female2.jpg', 'male.jpg']
    
    print(f"Found {len(image_list)} images in database")
    print("-" * 60)
    
    # Assign metadata to each image
    for i, image in enumerate(image_list):
        if i < len(image_files):
            image_name = image_files[i]
            metadata = image_metadata.get(image_name)
            
            if metadata:
                # Create a new missing person for this image
                full_name = metadata['name']
                age = metadata['age']
                gender = metadata['gender']
                location = metadata['location']
                
                # Delete old missing person if it exists (and has only this image)
                old_missing_person = image.missing_person
                if old_missing_person.full_name == 'Test Missing Person' and old_missing_person.facial_recognition_images.count() <= 1:
                    old_missing_person.delete()
                
                # Create new missing person with metadata
                missing_person, created = MissingPerson.objects.get_or_create(
                    full_name=full_name,
                    defaults={
                        'reported_by': user,
                        'age': age,
                        'gender': gender,
                        'last_seen_location': location,
                        'description': f'{full_name}, age {age}, {gender}, last seen at {location}',
                        'status': 'reported',
                        'last_seen_date': timezone.now()
                    }
                )
                
                # Update the image's missing_person relationship
                image.missing_person = missing_person
                image.save()
                
                action = "created" if created else "uses existing"
                print(f"Image: {image_name}")
                print(f"  Person: {full_name}")
                print(f"  Age: {age}")
                print(f"  Gender: {gender.capitalize()}")
                print(f"  Last Location: {location}")
                print(f"  Status: {action} missing person record")
                print()

if __name__ == '__main__':
    assign_image_metadata()
    print("-" * 60)
    print("Metadata assignment completed!")
