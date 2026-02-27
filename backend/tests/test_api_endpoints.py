"""
Integration tests: API RBAC, match verification, and missing person endpoints.

Phase 2 of the Validation Testing Framework — aligned with TRD Section 6.2.
"""
import pytest
from rest_framework import status


@pytest.mark.django_db
class TestRBACMissingPersons:
    """Role-Based Access Control on /api/missing-persons/."""

    URL = '/api/facial-recognition/missing-persons/'

    def test_family_only_sees_own_reports(self, family_client, family_user, missing_person, police_user):
        """Family user should NOT see cases reported by another user."""
        from facial_recognition.models import MissingPerson
        other_person = MissingPerson.objects.create(
            reported_by=police_user,
            full_name='Other Person',
        )
        response = family_client.get(self.URL)
        assert response.status_code == status.HTTP_200_OK
        # Handle PageNumberPagination structure
        results = response.data.get('results', response.data)
        ids = [str(r['id']) for r in results]
        assert str(missing_person.id) in ids
        assert str(other_person.id) not in ids

    def test_police_sees_all_cases(self, police_client, missing_person, police_user):
        """Police user should see all cases regardless of reporter."""
        from facial_recognition.models import MissingPerson
        other = MissingPerson.objects.create(
            reported_by=police_user,
            full_name='Other Person',
        )
        response = police_client.get(self.URL)
        assert response.status_code == status.HTTP_200_OK
        results = response.data.get('results', response.data)
        ids = [str(r['id']) for r in results]
        assert str(missing_person.id) in ids
        assert str(other.id) in ids

    def test_unauthenticated_cannot_access(self):
        from rest_framework.test import APIClient
        response = APIClient().get(self.URL)
        assert response.status_code in (
            status.HTTP_401_UNAUTHORIZED,
            status.HTTP_403_FORBIDDEN,
        )

    def test_family_can_create_report(self, family_client):
        response = family_client.post(
            self.URL,
            {'full_name': 'New Missing Person', 'age': 25, 'gender': 'female'},
            format='json',
        )
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data['full_name'] == 'New Missing Person'

    def test_report_filters_by_status(self, family_client, missing_person):
        response = family_client.get(self.URL + '?status=REPORTED')
        assert response.status_code == status.HTTP_200_OK


@pytest.mark.django_db
class TestMatchVerification:
    """Police user can verify/reject matches; family cannot."""

    def test_police_can_verify_match(self, police_client, facial_match):
        url = f'/api/facial-recognition/matches/{facial_match.id}/verify/'
        response = police_client.post(url, {'notes': 'Confirmed identity'}, format='json')
        assert response.status_code == status.HTTP_200_OK
        facial_match.refresh_from_db()
        assert facial_match.status == 'verified'
        assert facial_match.requires_human_review is False

    def test_police_can_reject_match(self, police_client, facial_match):
        url = f'/api/facial-recognition/matches/{facial_match.id}/reject/'
        response = police_client.post(url, {'notes': 'Wrong person'}, format='json')
        assert response.status_code == status.HTTP_200_OK
        facial_match.refresh_from_db()
        assert facial_match.status == 'false_positive'


    def test_family_cannot_verify_match(self, family_client, facial_match):
        url = f'/api/facial-recognition/matches/{facial_match.id}/verify/'
        response = family_client.post(url, {'notes': 'Trying to verify'}, format='json')
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_family_cannot_reject_match(self, family_client, facial_match):
        url = f'/api/facial-recognition/matches/{facial_match.id}/reject/'
        response = family_client.post(url, {'notes': 'Trying to reject'}, format='json')
        assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.django_db
class TestMissingPersonSearch:
    """Text-based search endpoint."""

    def test_search_by_name(self, family_client, missing_person):
        response = family_client.post(
            '/api/facial-recognition/missing-persons/search/',
            {'name': 'Test'},
            format='json',
        )
        assert response.status_code == status.HTTP_200_OK

    def test_search_by_gender(self, family_client, missing_person):
        response = family_client.post(
            '/api/facial-recognition/missing-persons/search/',
            {'gender': 'male'},
            format='json',
        )
        assert response.status_code == status.HTTP_200_OK

    def test_search_by_location(self, family_client, missing_person):
        response = family_client.post(
            '/api/facial-recognition/missing-persons/search/',
            {'location': 'Nairobi'},
            format='json',
        )
        assert response.status_code == status.HTTP_200_OK
        names = [r['full_name'] for r in response.data]
        assert 'Test Person' in names

    def test_found_persons_excluded_from_search(self, family_client, missing_person):
        missing_person.status = 'CLOSED'
        missing_person.save()
        response = family_client.post(
            '/api/facial-recognition/missing-persons/search/',
            {'name': 'Test'},
            format='json',
        )
        ids = [str(r['id']) for r in response.data]
        assert str(missing_person.id) not in ids
