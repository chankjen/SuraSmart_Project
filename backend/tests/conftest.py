"""Tests conftest — shared fixtures for all Sura Smart test modules."""
import pytest
from django.test import override_settings
from django.core.files.uploadedfile import SimpleUploadedFile
from rest_framework.test import APIClient

from users.models import User
from facial_recognition.models import MissingPerson, FacialRecognitionImage, FacialMatch, SearchSession


# Monkey-patch Django's BaseContext to fix Python 3.14 bug
def patch_django_context():
    try:
        from django.template.context import BaseContext
        import copy

        original_copy = BaseContext.__copy__

        def new_copy(self):
            # The bug is: duplicate = copy(super()); duplicate.dicts = self.dicts[:]
            # We fix it by creating a new instance of the same class
            duplicate = self.__class__()
            for key, value in self.__dict__.items():
                setattr(duplicate, key, value)
            if hasattr(self, 'dicts'):
                duplicate.dicts = self.dicts[:]
            return duplicate

        BaseContext.__copy__ = new_copy
    except ImportError:
        pass

patch_django_context()


# Force DEBUG=False globally for all tests to avoid Python 3.14 + Django template
# context __copy__ bug (`super().dicts`) that fires in error response rendering.
@pytest.fixture(autouse=True)
def force_debug_off(settings):
    settings.DEBUG = False


# ──────────────────────────────────────────────────────────
#  Users
# ──────────────────────────────────────────────────────────

@pytest.fixture
def family_user(db):
    """A family-member user with limited access."""
    return User.objects.create_user(
        username='family01',
        email='family@test.com',
        password='testpass123',
        role='family_member',
        verification_status='verified',
    )


@pytest.fixture
def police_user(db):
    """A police officer with full case access."""
    return User.objects.create_user(
        username='officer01',
        email='police@test.com',
        password='testpass123',
        role='police_officer',
    )


@pytest.fixture
def api_client():
    """Unauthenticated API client."""
    client = APIClient()
    client.defaults['HTTP_ACCEPT'] = 'application/json'
    return client


@pytest.fixture
def family_client(family_user):
    """Authenticated API client for a family user."""
    client = APIClient()
    client.defaults['HTTP_ACCEPT'] = 'application/json'
    client.force_authenticate(user=family_user)
    return client


@pytest.fixture
def police_client(police_user):
    """Authenticated API client for a police user."""
    client = APIClient()
    client.defaults['HTTP_ACCEPT'] = 'application/json'
    client.force_authenticate(user=police_user)
    return client


# ──────────────────────────────────────────────────────────
#  Sample image (1×1 white JPEG, no real face)
# ──────────────────────────────────────────────────────────

@pytest.fixture
def sample_image_file():
    """Minimal valid JPEG bytes (no actual face — for unit tests)."""
    # 1×1 white JPEG (raw bytes, valid JPEG header)
    jpeg_bytes = (
        b'\xff\xd8\xff\xe0\x00\x10JFIF\x00\x01\x01\x00\x00\x01\x00\x01\x00\x00'
        b'\xff\xdb\x00C\x00\x08\x06\x06\x07\x06\x05\x08\x07\x07\x07\t\t'
        b'\x08\n\x0c\x14\r\x0c\x0b\x0b\x0c\x19\x12\x13\x0f\x14\x1d\x1a'
        b'\x1f\x1e\x1d\x1a\x1c\x1c $.\' ",#\x1c\x1c(7),01444\x1f\'9=82<.342\x1e\x1b'
        b'\xff\xc0\x00\x0b\x08\x00\x01\x00\x01\x01\x01\x11\x00\xff\xc4\x00'
        b'\x1f\x00\x00\x01\x05\x01\x01\x01\x01\x01\x01\x00\x00\x00\x00\x00'
        b'\x00\x00\x00\x01\x02\x03\x04\x05\x06\x07\x08\t\n\x0b\xff\xc4\x00'
        b'\xb5\x10\x00\x02\x01\x03\x03\x02\x04\x03\x05\x05\x04\x04\x00\x00'
        b'\x01}\x01\x02\x03\x00\x04\x11\x05\x12!1A\x06\x13Qa\x07"q\x142\x81'
        b'\x91\xa1\x08#B\xb1\xc1\x15R\xd1\xf0$3br\x82\t\n\x16\x17\x18\x19'
        b'\x1a%&\'()*456789:CDEFGHIJSTUVWXYZcdefghijstuvwxyz\x83\x84\x85\x86'
        b'\x87\x88\x89\x8a\x92\x93\x94\x95\x96\x97\x98\x99\x9a\xa2\xa3\xa4'
        b'\xa5\xa6\xa7\xa8\xa9\xaa\xb2\xb3\xb4\xb5\xb6\xb7\xb8\xb9\xba\xc2'
        b'\xc3\xc4\xc5\xc6\xc7\xc8\xc9\xca\xd2\xd3\xd4\xd5\xd6\xd7\xd8\xd9'
        b'\xda\xe1\xe2\xe3\xe4\xe5\xe6\xe7\xe8\xe9\xea\xf1\xf2\xf3\xf4\xf5'
        b'\xf6\xf7\xf8\xf9\xfa\xff\xda\x00\x08\x01\x01\x00\x00?\x00\xfb\xd2'
        b'\x8a(\x03\xff\xd9'
    )
    return SimpleUploadedFile('test.jpg', jpeg_bytes, content_type='image/jpeg')


# ──────────────────────────────────────────────────────────
#  Missing persons
# ──────────────────────────────────────────────────────────

@pytest.fixture
def missing_person(db, family_user):
    return MissingPerson.objects.create(
        reported_by=family_user,
        full_name='Test Person',
        age=30,
        gender='male',
        last_seen_location='Nairobi',
    )


@pytest.fixture
def facial_image_with_embedding(db, missing_person, sample_image_file):
    """A FacialRecognitionImage record with a mock embedding stored."""
    img = FacialRecognitionImage.objects.create(
        missing_person=missing_person,
        image_file=sample_image_file,
        image_hash='aabbccddeeff001122334455aabbccddeeff001122334455aabbccddeeff0011',
        status='completed',
        face_confidence=0.99,
        # 512-d zero vector as mock embedding
        face_embedding=[0.0] * 512,
    )
    return img


@pytest.fixture
def facial_match(db, missing_person, facial_image_with_embedding, police_user):
    return FacialMatch.objects.create(
        missing_person=missing_person,
        source_image=facial_image_with_embedding,
        match_confidence=0.95,
        distance_metric=0.05,
        source_database='user_upload',
        source_reference='test-ref',
        algorithm_version='v2.0',
        model_name='Facenet512',
        requires_human_review=True,
    )
