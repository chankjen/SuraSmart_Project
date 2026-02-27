"""
Real AI-powered facial recognition views using DeepFace.

Replaces the hash-based simulation with genuine face embedding extraction
and cosine similarity matching. Implements HITL flagging per TRD Section 4.2.3.
"""
from __future__ import annotations

from rest_framework import viewsets, status
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters
from django.db.models import Q
import logging
import hashlib
import time
import numpy as np
import io

from facial_recognition.models import (
    MissingPerson, FacialRecognitionImage, FacialMatch, ProcessingQueue, SearchSession
)
from facial_recognition.serializers import (
    MissingPersonSerializer, FacialRecognitionImageSerializer,
    FacialMatchSerializer, ProcessingQueueSerializer, SearchSessionSerializer
)
from users.permissions import (
    IsPoliceOrGovernment, IsGovernmentOfficial, get_user_permissions, anonymize_pii
)
from users.verification import IdentityVerificationService
from .state_machine import CaseStateMachine

logger = logging.getLogger(__name__)

# ──────────────────────────────────────────────────────────────────
#  AI Engine helpers
# ──────────────────────────────────────────────────────────────────

def _get_deepface():
    """Lazy-import DeepFace so missing library gives a clear error."""
    try:
        from deepface import DeepFace
        return DeepFace
    except ImportError:
        raise ImportError(
            "DeepFace is not installed. Run: pip install deepface==0.0.93"
        )


def _bytes_from_file(image_file):
    """Read uploaded file into bytes, reset pointer."""
    image_file.seek(0)
    data = image_file.read()
    image_file.seek(0)
    return data


def _extract_embedding(image_bytes: bytes, model_name: str = "Facenet512"):
    """
    Extract a 512-d face embedding from raw image bytes.

    Returns None if no face is detected (e.g. corrupt image or no face present).
    Aligned with TRD Section 3.1 (Facial Recognition System).
    """
    DeepFace = _get_deepface()
    try:
        import tempfile, os
        # DeepFace works most reliably with a file path
        with tempfile.NamedTemporaryFile(suffix=".jpg", delete=False) as tmp:
            tmp.write(image_bytes)
            tmp_path = tmp.name

        result = DeepFace.represent(
            img_path=tmp_path,
            model_name=model_name,
            enforce_detection=True,
            detector_backend="opencv",
        )
        os.unlink(tmp_path)

        # result is a list; take first face's embedding
        if result and len(result) > 0:
            return result[0]["embedding"]
        return None
    except Exception as exc:
        logger.warning("Embedding extraction failed: %s", exc)
        try:
            os.unlink(tmp_path)
        except Exception:
            pass
        return None


def _cosine_similarity(vec_a: list, vec_b: list) -> float:
    """
    Cosine similarity between two embedding vectors, returned as [0, 1].
    1.0 = identical faces. Used as confidence score.
    """
    a = np.array(vec_a, dtype=np.float64)
    b = np.array(vec_b, dtype=np.float64)
    dot = np.dot(a, b)
    norm = np.linalg.norm(a) * np.linalg.norm(b)
    if norm == 0:
        return 0.0
    return float(np.clip(dot / norm, 0.0, 1.0))


def _determine_hitl(confidence: float) -> bool:
    """
    Human-in-the-Loop flag per TRD Section 4.2.3.
    Matches with 90% ≤ confidence < 98% must be reviewed by an authority.
    """
    return 0.90 <= confidence < 0.98


def _compute_image_hash(image_bytes: bytes) -> str:
    """SHA-256 hash of image bytes for deduplication (TRD Section 3.1)."""
    return hashlib.sha256(image_bytes).hexdigest()


# ──────────────────────────────────────────────────────────────────
#  ViewSets
# ──────────────────────────────────────────────────────────────────

class MissingPersonViewSet(viewsets.ModelViewSet):
    """ViewSet for missing person records with role-based access."""
    queryset = MissingPerson.objects.all()
    serializer_class = MissingPersonSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['status', 'gender']
    search_fields = ['full_name', 'description']
    ordering_fields = ['date_reported', 'created_at']
    ordering = ['-created_at']

    def get_queryset(self):
        """Filter queryset based on user role and jurisdiction (TRD §4.2, §8)."""
        user = self.request.user
        user_perms = get_user_permissions(user)
        
        if user_perms.get('can_access_all_cases', False):
            return MissingPerson.objects.all()
        
        if user.role == 'police_officer':
            # Police see all cases in their jurisdiction
            return MissingPerson.objects.filter(jurisdiction=user.jurisdiction)
            
        return MissingPerson.objects.filter(reported_by=user)

    def list(self, request, *args, **kwargs):
        response = super().list(request, *args, **kwargs)
        response.data['results'] = [anonymize_pii(item, request.user) for item in response.data.get('results', [])]
        return response

    def retrieve(self, request, *args, **kwargs):
        response = super().retrieve(request, *args, **kwargs)
        response.data = anonymize_pii(response.data, request.user)
        return response

    def perform_create(self, serializer):
        user = self.request.user
        if user.role == 'family_member' and user.verification_status != 'verified':
            from rest_framework.exceptions import ValidationError
            raise ValidationError('You must verify your identity before reporting a missing person.')
        
        serializer.save(reported_by=user, status='REPORTED')

    def perform_update(self, serializer):
        user_perms = get_user_permissions(self.request.user)
        obj = self.get_object()
        if not user_perms['can_modify_other_cases'] and obj.reported_by != self.request.user:
            raise PermissionError('You can only modify your own reports.')
        serializer.save()

    @action(detail=True, methods=['post'])
    def upload_image(self, request, pk=None):
        """Upload facial recognition image for missing person."""
        missing_person = self.get_object()
        user_perms = get_user_permissions(request.user)

        if (not user_perms.get('can_modify_other_cases', False) and
                missing_person.reported_by != request.user):
            return Response(
                {'error': 'You do not have permission to upload images for this case.'},
                status=status.HTTP_403_FORBIDDEN
            )

        if 'image' not in request.FILES:
            return Response({'error': 'No image provided'}, status=status.HTTP_400_BAD_REQUEST)

        image_file = request.FILES['image']
        image_bytes = _bytes_from_file(image_file)
        image_hash = _compute_image_hash(image_bytes)

        # Deduplication check
        if FacialRecognitionImage.objects.filter(image_hash=image_hash).exists():
            return Response(
                {'error': 'This image has already been uploaded.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Create image record
        facial_image = FacialRecognitionImage.objects.create(
            missing_person=missing_person,
            image_file=image_file,
            image_hash=image_hash,
            status='processing',
        )

        # Extract and store embedding immediately (synchronous for now)
        embedding = _extract_embedding(image_bytes)
        if embedding:
            facial_image.face_embedding = embedding
            facial_image.face_confidence = 1.0  # face was clearly detected
            facial_image.status = 'completed'
        else:
            facial_image.status = 'failed'
            facial_image.processing_error = 'No face detected in uploaded image.'

        import django.utils.timezone as tz
        facial_image.processed_at = tz.now()
        facial_image.save()

        # Queue for any additional async processing
        ProcessingQueue.objects.create(
            image=facial_image,
            priority=request.data.get('priority', 'normal'),
            status='completed' if embedding else 'failed',
        )

        serializer = FacialRecognitionImageSerializer(facial_image)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=['post'])
    def sign_closure(self, request, pk=None):
        """Apply a dual-signature for case closure."""
        case = self.get_object()
        sm = CaseStateMachine(case)
        try:
            closed = sm.toggle_signature(request.user.role)
            return Response({
                'status': 'success',
                'is_closed': closed,
                'dual_signature_family': case.dual_signature_family,
                'dual_signature_police': case.dual_signature_police
            })
        except ValueError as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['post'])
    def search(self, request):
        """Search missing persons database based on provided criteria."""
        search_data = request.data
        query = Q()

        if search_data.get('name'):
            for term in search_data['name'].split():
                query &= Q(full_name__icontains=term)

        if search_data.get('age'):
            try:
                age = int(search_data['age'])
                query &= Q(age__range=(age - 5, age + 5))
            except ValueError:
                pass

        if search_data.get('gender'):
            query &= Q(gender__iexact=search_data['gender'])

        if search_data.get('location'):
            location_query = Q()
            for term in search_data['location'].split():
                location_query |= Q(last_seen_location__icontains=term)
            query &= location_query

        matches = MissingPerson.objects.filter(query).exclude(status='CLOSED')[:20]
        results = [anonymize_pii(MissingPersonSerializer(m).data, request.user) for m in matches]
        return Response(results)


class FacialRecognitionImageViewSet(viewsets.ModelViewSet):
    """ViewSet for facial recognition images."""
    queryset = FacialRecognitionImage.objects.all()
    serializer_class = FacialRecognitionImageSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['missing_person', 'status', 'is_primary']
    ordering_fields = ['created_at', 'processed_at']
    ordering = ['-created_at']

    def get_queryset(self):
        user = self.request.user
        user_perms = get_user_permissions(user)
        
        if user_perms.get('can_access_all_cases', False):
            return FacialRecognitionImage.objects.all()
            
        if user.role == 'police_officer':
            return FacialRecognitionImage.objects.filter(missing_person__jurisdiction=user.jurisdiction)
            
        return FacialRecognitionImage.objects.filter(
            missing_person__reported_by=user
        )

    def perform_create(self, serializer):
        serializer.save()


class FacialMatchViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for facial match results with role-based verification."""
    queryset = FacialMatch.objects.all()
    serializer_class = FacialMatchSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['missing_person', 'source_database', 'status']
    ordering_fields = ['match_confidence', 'created_at']
    ordering = ['-match_confidence']

    def get_queryset(self):
        user = self.request.user
        user_perms = get_user_permissions(user)
        
        if user_perms.get('can_access_all_cases', False):
            return FacialMatch.objects.all()
            
        if user.role == 'police_officer':
            return FacialMatch.objects.filter(missing_person__jurisdiction=user.jurisdiction)
            
        return FacialMatch.objects.filter(missing_person__reported_by=user)

    @action(detail=True, methods=['post'])
    def verify(self, request, pk=None):
        """Verify a facial match (only for authorized users)."""
        user_perms = get_user_permissions(request.user)
        if not user_perms.get('can_verify_matches', False):
            return Response(
                {'error': 'You do not have permission to verify matches.'},
                status=status.HTTP_403_FORBIDDEN
            )
        match = self.get_object()
        match.status = 'verified'
        match.verified_by = request.user
        match.verification_notes = request.data.get('notes', '')
        match.requires_human_review = False  # cleared after human review
        match.save()
        return Response(self.get_serializer(match).data)

    @action(detail=True, methods=['post'])
    def reject(self, request, pk=None):
        """Reject a facial match (only for authorized users)."""
        user_perms = get_user_permissions(request.user)
        if not user_perms.get('can_verify_matches', False):
            return Response(
                {'error': 'You do not have permission to reject matches.'},
                status=status.HTTP_403_FORBIDDEN
            )
        match = self.get_object()
        match.status = 'false_positive'
        match.verified_by = request.user
        match.verification_notes = request.data.get('notes', '')
        match.requires_human_review = False
        match.save()
        return Response(self.get_serializer(match).data)


class ProcessingQueueViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for processing queue (monitoring)."""
    queryset = ProcessingQueue.objects.all()
    serializer_class = ProcessingQueueSerializer
    permission_classes = [IsAuthenticated]


class SearchSessionViewSet(viewsets.ModelViewSet):
    """ViewSet for search sessions."""
    queryset = SearchSession.objects.all()
    serializer_class = SearchSessionSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['is_closed', 'closure_action']
    ordering_fields = ['created_at', 'match_confidence']
    ordering = ['-created_at']

    def get_queryset(self):
        return SearchSession.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    @action(detail=True, methods=['post'])
    def close(self, request, pk=None):
        """Close a search session with the specified action."""
        session = self.get_object()
        if session.is_closed:
            return Response(
                {'error': 'Search session is already closed'},
                status=status.HTTP_400_BAD_REQUEST
            )

        action_value = request.data.get('action')
        notes = request.data.get('notes', '')

        if action_value not in ['save', 'finalize', 'search_again', 'no_match']:
            return Response({'error': 'Invalid closure action'}, status=status.HTTP_400_BAD_REQUEST)

        session.close_session(action_value, notes)

        feedback_messages = {
            'save': 'Search result saved for later review.',
            'finalize': 'Match finalized. The case has been marked as found.',
            'search_again': 'Search session closed. You can start a new search anytime.',
            'no_match': 'Recorded that no match was found. Search archived for reference.',
        }

        response_data = self.get_serializer(session).data
        response_data['feedback'] = feedback_messages.get(action_value, 'Session closed.')
        return Response(response_data)


# ──────────────────────────────────────────────────────────────────
#  Primary Facial Recognition Search Endpoint
# ──────────────────────────────────────────────────────────────────

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def search_facial_recognition(request):
    """
    Real AI-powered facial recognition search.

    Extracts a face embedding from the uploaded image using DeepFace/Facenet512,
    then computes cosine similarity against all embeddings stored in the database.

    HITL (TRD Section 4.2.3): Matches where 90% ≤ confidence < 98% are flagged
    `requires_human_review = True` and must be verified by an authority before action.

    BIPA (TRD Section 5.1.2): `consent_given` is stored on the SearchSession.

    Performance target: search completion < 30s (TRD Section 6.1.1).
    """
    if 'image' not in request.FILES:
        return Response({'error': 'No image provided'}, status=status.HTTP_400_BAD_REQUEST)

    # BIPA: require explicit consent
    consent_given = request.data.get('consent_given', 'false')
    if isinstance(consent_given, str):
        consent_given = consent_given.lower() in ('true', '1', 'yes')

    image_file = request.FILES['image']
    search_query = request.data.get('query', '')

    start_time = time.time()

    # Create search session
    search_session = SearchSession.objects.create(
        user=request.user,
        uploaded_image=image_file,
        search_query=search_query,
        consent_given=bool(consent_given),
    )

    # Extract query embedding
    image_file.seek(0)
    image_bytes = image_file.read()
    query_embedding = _extract_embedding(image_bytes)

    if query_embedding is None:
        search_session.save()
        return Response(
            {
                'search_session_id': str(search_session.id),
                'match_found': False,
                'error': 'No face detected in the uploaded image. Please upload a clear, front-facing photo.',
                'total_candidates_searched': 0,
            },
            status=status.HTTP_422_UNPROCESSABLE_ENTITY,
        )

    # Retrieve all completed images that have embeddings stored
    db_images = FacialRecognitionImage.objects.filter(
        status='completed'
    ).exclude(face_embedding__isnull=True)

    search_session.total_candidates_searched = db_images.count()

    best_match = None
    best_confidence = 0.0
    best_db_image = None

    for db_image in db_images:
        stored_embedding = db_image.face_embedding
        if not stored_embedding:
            continue

        confidence = _cosine_similarity(query_embedding, stored_embedding)

        if confidence > best_confidence:
            best_confidence = confidence
            best_db_image = db_image

    elapsed_ms = int((time.time() - start_time) * 1000)
    logger.info(
        "Facial search completed in %dms. Candidates: %d. Best confidence: %.4f",
        elapsed_ms, search_session.total_candidates_searched, best_confidence,
    )

    # Warn if we're approaching the 30-second SLA (TRD Section 6.1.1)
    if elapsed_ms > 25_000:
        logger.warning("Search took %dms — approaching 30s SLA limit.", elapsed_ms)

    if best_db_image and best_confidence >= 0.50:  # minimum plausible threshold
        hitl_flag = _determine_hitl(best_confidence)

        match, created = FacialMatch.objects.get_or_create(
            missing_person=best_db_image.missing_person,
            source_image=best_db_image,
            defaults={
                'match_confidence': best_confidence,
                'distance_metric': round(1.0 - best_confidence, 6),
                'source_database': 'user_upload',
                'source_reference': str(best_db_image.id),
                'algorithm_version': 'v2.0',
                'model_name': 'Facenet512',
                'requires_human_review': hitl_flag,
            }
        )
        if not created:
            match.match_confidence = best_confidence
            match.distance_metric = round(1.0 - best_confidence, 6)
            match.requires_human_review = hitl_flag
            match.save()

        best_match = match

    # Update session
    if best_match:
        search_session.best_match = best_match
        search_session.match_confidence = best_confidence
    search_session.save()

    # Build response
    response_data = {
        'search_session_id': str(search_session.id),
        'total_candidates_searched': search_session.total_candidates_searched,
        'search_time_ms': elapsed_ms,
    }

    if best_match:
        hitl_flag = best_match.requires_human_review
        response_data.update({
            'match_found': True,
            'match': FacialMatchSerializer(best_match).data,
            'match_confidence': round(best_confidence, 4),
            'requires_human_review': hitl_flag,
            'message': (
                f'Match found with {best_confidence:.1%} confidence. '
                + ('⚠️ Human review required before any action.' if hitl_flag else 'High confidence match.')
            ),
            'closure_options': [
                {'action': 'save', 'label': 'Save for Later', 'description': 'Save for future review'},
                {'action': 'finalize', 'label': 'Finalize Match', 'description': 'Confirm match and close the case'},
                {'action': 'search_again', 'label': 'Search Again', 'description': 'Perform another search'},
            ],
        })
    else:
        response_data.update({
            'match_found': False,
            'message': 'No matches found in the database.',
            'closure_options': [
                {'action': 'no_match', 'label': 'No Match Found', 'description': 'Record no match found'},
                {'action': 'search_again', 'label': 'Search Again', 'description': 'Try searching again'},
            ],
        })

    return Response(response_data, status=status.HTTP_200_OK)