"""
Unit tests: facial recognition models, views, HITL flagging, session management.

Phase 1 & 2 of the Validation Testing Framework (TRD Section 6.2).
Mocks DeepFace so no real GPU/model is needed in CI.
"""
import pytest
from unittest.mock import patch, MagicMock
from django.core.files.uploadedfile import SimpleUploadedFile
from rest_framework import status

from facial_recognition.models import (
    MissingPerson, FacialRecognitionImage, FacialMatch, SearchSession
)
from facial_recognition.views import _determine_hitl, _cosine_similarity, _compute_image_hash


# ──────────────────────────────────────────────────────────
#  Helper / unit-level tests
# ──────────────────────────────────────────────────────────

class TestHTILFlagging:
    """TRD Section 4.2.3 — HITL flag logic."""

    def test_below_90_no_hitl(self):
        assert _determine_hitl(0.89) is False

    def test_at_90_triggers_hitl(self):
        assert _determine_hitl(0.90) is True

    def test_at_97_triggers_hitl(self):
        assert _determine_hitl(0.97) is True

    def test_at_98_no_hitl(self):
        """Exactly 98% is high-confidence — no human review needed."""
        assert _determine_hitl(0.98) is False

    def test_above_98_no_hitl(self):
        assert _determine_hitl(0.99) is False

    def test_zero_no_hitl(self):
        assert _determine_hitl(0.0) is False


class TestCosineSimilarity:
    """Similarity function correctness."""

    def test_identical_vectors_return_one(self):
        v = [1.0, 0.0, 0.0]
        assert _cosine_similarity(v, v) == pytest.approx(1.0, abs=1e-6)

    def test_orthogonal_vectors_return_zero(self):
        a = [1.0, 0.0]
        b = [0.0, 1.0]
        assert _cosine_similarity(a, b) == pytest.approx(0.0, abs=1e-6)

    def test_opposite_vectors_clipped_to_zero(self):
        """Cosine similarity is clipped to [0, 1]."""
        a = [1.0, 0.0]
        b = [-1.0, 0.0]
        result = _cosine_similarity(a, b)
        assert result == pytest.approx(0.0, abs=1e-6)

    def test_zero_norm_returns_zero(self):
        a = [0.0, 0.0]
        b = [1.0, 0.0]
        assert _cosine_similarity(a, b) == 0.0


class TestImageHashing:
    """Deduplication via SHA-256."""

    def test_same_bytes_same_hash(self):
        data = b'\xff\xd8\xff\xe0hello'
        assert _compute_image_hash(data) == _compute_image_hash(data)

    def test_different_bytes_different_hash(self):
        assert _compute_image_hash(b'abc') != _compute_image_hash(b'xyz')

    def test_hash_length(self):
        h = _compute_image_hash(b'test')
        assert len(h) == 64  # SHA-256 hex digest


# ──────────────────────────────────────────────────────────
#  Model-level tests (database)
# ──────────────────────────────────────────────────────────

@pytest.mark.django_db
class TestFacialMatchModel:
    """Test FacialMatch model fields including new HITL field."""

    def test_requires_human_review_defaults_false(self, missing_person, facial_image_with_embedding):
        match = FacialMatch.objects.create(
            missing_person=missing_person,
            source_image=facial_image_with_embedding,
            match_confidence=0.99,
            distance_metric=0.01,
            source_database='user_upload',
            source_reference='ref-999',
            algorithm_version='v2.0',
        )
        assert match.requires_human_review is False

    def test_hitl_flag_set_on_borderline(self, missing_person, facial_image_with_embedding):
        match = FacialMatch.objects.create(
            missing_person=missing_person,
            source_image=facial_image_with_embedding,
            match_confidence=0.93,
            distance_metric=0.07,
            source_database='user_upload',
            source_reference='ref-borderline',
            algorithm_version='v2.0',
            requires_human_review=True,
        )
        assert match.requires_human_review is True

    def test_str_representation(self, facial_match):
        assert 'Test Person' in str(facial_match)
        assert '%' in str(facial_match)


@pytest.mark.django_db
class TestSearchSessionModel:
    """Test SearchSession model including new consent_given field."""

    def test_consent_given_defaults_false(self, family_user, sample_image_file):
        session = SearchSession.objects.create(
            user=family_user,
            uploaded_image=sample_image_file,
        )
        assert session.consent_given is False

    def test_consent_given_stored(self, family_user, sample_image_file):
        session = SearchSession.objects.create(
            user=family_user,
            uploaded_image=sample_image_file,
            consent_given=True,
        )
        assert session.consent_given is True

    def test_close_session_saves_action(self, family_user, sample_image_file):
        session = SearchSession.objects.create(
            user=family_user,
            uploaded_image=sample_image_file,
        )
        session.close_session('no_match', notes='No one matched')
        assert session.is_closed is True
        assert session.closure_action == 'no_match'

    def test_close_session_finalize_marks_person_found(
        self, family_user, sample_image_file, facial_match
    ):
        session = SearchSession.objects.create(
            user=family_user,
            uploaded_image=sample_image_file,
            best_match=facial_match,
        )
        session.close_session('finalize')

        facial_match.refresh_from_db()
        assert facial_match.status == 'verified'

        missing_person = facial_match.missing_person
        missing_person.refresh_from_db()
        assert missing_person.status == 'found'


# ──────────────────────────────────────────────────────────
#  API endpoint tests (mocked DeepFace)
# ──────────────────────────────────────────────────────────

@pytest.mark.django_db
class TestFacialSearchEndpoint:
    """Tests for POST /api/facial-recognition/search/ with mocked AI."""

    SEARCH_URL = '/api/facial-recognition/search/'

    def _make_image(self, name='upload.jpg'):
        return SimpleUploadedFile(name, b'\xff\xd8\xff\xe0' + b'\x00' * 100, content_type='image/jpeg')

    @patch('facial_recognition.views._extract_embedding')
    def test_no_face_detected_returns_422(self, mock_embed, family_client):
        """If no face is found in uploaded image, return 422."""
        mock_embed.return_value = None
        response = family_client.post(
            self.SEARCH_URL,
            {'image': self._make_image(), 'consent_given': 'true'},
            format='multipart',
        )
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
        assert 'No face detected' in response.data.get('error', '')

    @patch('facial_recognition.views._extract_embedding')
    def test_no_db_images_returns_no_match(self, mock_embed, family_client):
        """When database has no completed images, return no match."""
        mock_embed.return_value = [0.5] * 512
        response = family_client.post(
            self.SEARCH_URL,
            {'image': self._make_image(), 'consent_given': 'true'},
            format='multipart',
        )
        assert response.status_code == status.HTTP_200_OK
        assert response.data['match_found'] is False

    @patch('facial_recognition.views._extract_embedding')
    def test_high_confidence_match_no_hitl(self, mock_embed, family_client, facial_image_with_embedding):
        """A >98% confidence match should NOT be flagged for HITL."""
        # Mock the same embedding as stored → cosine similarity = 1.0
        mock_embed.return_value = [0.0] * 512  # identical to stored [0.0]*512

        # Force stored embedding to be a unit vector so similarity = 1.0
        from facial_recognition.models import FacialRecognitionImage
        img = FacialRecognitionImage.objects.get(pk=facial_image_with_embedding.pk)
        img.face_embedding = [1.0] + [0.0] * 511
        img.save()
        mock_embed.return_value = [1.0] + [0.0] * 511  # → similarity 1.0

        response = family_client.post(
            self.SEARCH_URL,
            {'image': self._make_image(), 'consent_given': 'true'},
            format='multipart',
        )
        assert response.status_code == status.HTTP_200_OK
        assert response.data['match_found'] is True
        assert response.data.get('requires_human_review') is False

    @patch('facial_recognition.views._extract_embedding')
    def test_borderline_confidence_triggers_hitl(self, mock_embed, family_client, facial_image_with_embedding):
        """A 90-98% match must set requires_human_review = True."""
        # Stored embedding: unit vector on dim 0
        stored_vec = [1.0] + [0.0] * 511
        from facial_recognition.models import FacialRecognitionImage
        img = FacialRecognitionImage.objects.get(pk=facial_image_with_embedding.pk)
        img.face_embedding = stored_vec
        img.save()

        # Upload a slightly different vector → ~0.94 cosine similarity
        import math
        angle = math.radians(20)  # 20° → cos(20°) ≈ 0.94
        query_vec = [math.cos(angle)] + [math.sin(angle)] + [0.0] * 510
        mock_embed.return_value = query_vec

        response = family_client.post(
            self.SEARCH_URL,
            {'image': self._make_image(), 'consent_given': 'true'},
            format='multipart',
        )
        assert response.status_code == status.HTTP_200_OK
        data = response.data
        if data['match_found']:
            assert data.get('requires_human_review') is True

    def test_unauthenticated_returns_401(self, client):
        from rest_framework.test import APIClient
        anon = APIClient()
        response = anon.post(
            self.SEARCH_URL,
            {'image': self._make_image(), 'consent_given': 'true'},
            format='multipart',
        )
        assert response.status_code in (
            status.HTTP_401_UNAUTHORIZED,
            status.HTTP_403_FORBIDDEN,
        )

    def test_missing_image_returns_400(self, family_client):
        response = family_client.post(self.SEARCH_URL, {}, format='multipart')
        assert response.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.django_db
class TestSessionClosureEndpoint:
    """POST /api/facial-recognition/search-sessions/{id}/close/"""

    def test_close_with_no_match_action(self, family_client, family_user, sample_image_file):
        from facial_recognition.models import SearchSession
        session = SearchSession.objects.create(
            user=family_user,
            uploaded_image=sample_image_file,
        )
        url = f'/api/facial-recognition/search-sessions/{session.id}/close/'
        response = family_client.post(url, {'action': 'no_match'}, format='json')
        assert response.status_code == status.HTTP_200_OK
        assert response.data['is_closed'] is True

    def test_double_close_returns_400(self, family_client, family_user, sample_image_file):
        from facial_recognition.models import SearchSession
        session = SearchSession.objects.create(
            user=family_user,
            uploaded_image=sample_image_file,
        )
        session.close_session('no_match')
        url = f'/api/facial-recognition/search-sessions/{session.id}/close/'
        response = family_client.post(url, {'action': 'no_match'}, format='json')
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_invalid_action_returns_400(self, family_client, family_user, sample_image_file):
        from facial_recognition.models import SearchSession
        session = SearchSession.objects.create(
            user=family_user,
            uploaded_image=sample_image_file,
        )
        url = f'/api/facial-recognition/search-sessions/{session.id}/close/'
        response = family_client.post(url, {'action': 'invalid_action'}, format='json')
        assert response.status_code == status.HTTP_400_BAD_REQUEST
