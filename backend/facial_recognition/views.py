"""API Views for Facial Recognition app."""
from rest_framework import viewsets, status
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters
from facial_recognition.models import (
    MissingPerson, FacialRecognitionImage, FacialMatch, ProcessingQueue, SearchSession
)
from facial_recognition.serializers import (
    MissingPersonSerializer, FacialRecognitionImageSerializer,
    FacialMatchSerializer, ProcessingQueueSerializer, SearchSessionSerializer
)
from users.permissions import (
    IsPoliceOrGovernment, IsGovernmentOfficial, get_user_permissions
)


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
        """Filter queryset based on user role."""
        user_perms = get_user_permissions(self.request.user)
        
        # Family members can only see their own reports
        if not user_perms['can_access_all_cases']:
            return MissingPerson.objects.filter(reported_by=self.request.user)
        
        # Police and Government officials can see all cases
        return MissingPerson.objects.all()
    
    def perform_create(self, serializer):
        """Create missing person record with current user as reporter."""
        serializer.save(reported_by=self.request.user)
    
    def perform_update(self, serializer):
        """Check permissions before updating."""
        user_perms = get_user_permissions(self.request.user)
        obj = self.get_object()
        
        # Family members can only update their own reports
        if not user_perms['can_modify_other_cases'] and obj.reported_by != self.request.user:
            raise PermissionError('You can only modify your own reports.')
        
        serializer.save()
    
    @action(detail=True, methods=['post'])
    def upload_image(self, request, pk=None):
        """Upload facial recognition image for missing person."""
        missing_person = self.get_object()
        user_perms = get_user_permissions(request.user)
        
        # Check if user can upload image for this case
        if (not user_perms['can_modify_other_cases'] and 
            missing_person.reported_by != request.user):
            return Response(
                {'error': 'You do not have permission to upload images for this case.'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        if 'image' not in request.FILES:
            return Response(
                {'error': 'No image provided'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        image_file = request.FILES['image']
        
        # Create image record
        facial_image = FacialRecognitionImage.objects.create(
            missing_person=missing_person,
            image_file=image_file,
            image_hash='temp'  # Will be computed by preprocessing task
        )
        
        # Queue for processing
        ProcessingQueue.objects.create(
            image=facial_image,
            priority=request.data.get('priority', 'normal')
        )
        
        serializer = FacialRecognitionImageSerializer(facial_image)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class FacialRecognitionImageViewSet(viewsets.ModelViewSet):
    """ViewSet for facial recognition images."""
    queryset = FacialRecognitionImage.objects.all()
    serializer_class = FacialRecognitionImageSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['missing_person', 'status', 'is_primary']
    ordering_fields = ['created_at']


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
        """Filter images based on user permissions."""
        user_perms = get_user_permissions(self.request.user)
        
        # Family members can only see images for their own reports
        if not user_perms['can_access_all_cases']:
            return FacialRecognitionImage.objects.filter(
                missing_person__reported_by=self.request.user
            )
        
        return FacialRecognitionImage.objects.all()
    
    def perform_create(self, serializer):
        """Create image and trigger processing."""
        image = serializer.save()
        # TODO: Trigger async processing task
        # process_facial_recognition.delay(image.id)


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
        """Filter matches based on user role."""
        user_perms = get_user_permissions(self.request.user)
        
        # Family members can only see matches for their own reports
        if not user_perms['can_access_all_cases']:
            return FacialMatch.objects.filter(
                missing_person__reported_by=self.request.user
            )
        
        # Police and Government officials can see all matches
        return FacialMatch.objects.all()
    
    @action(detail=True, methods=['post'])
    def verify(self, request, pk=None):
        """Verify a facial match (only for authorized users)."""
        user_perms = get_user_permissions(request.user)
        
        if not user_perms['can_verify_matches']:
            return Response(
                {'error': 'You do not have permission to verify matches.'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        match = self.get_object()
        match.status = 'verified'
        match.verified_by = request.user
        match.verification_notes = request.data.get('notes', '')
        match.save()
        
        serializer = self.get_serializer(match)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def reject(self, request, pk=None):
        """Reject a facial match (only for authorized users)."""
        user_perms = get_user_permissions(request.user)
        
        if not user_perms['can_verify_matches']:
            return Response(
                {'error': 'You do not have permission to reject matches.'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        match = self.get_object()
        match.status = 'false_positive'
        match.verified_by = request.user
        match.verification_notes = request.data.get('notes', '')
        match.save()
        
        serializer = self.get_serializer(match)
        return Response(serializer.data)


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
        """Users can only see their own search sessions."""
        return SearchSession.objects.filter(user=self.request.user)
    
    def perform_create(self, serializer):
        """Set the user when creating a search session."""
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
        
        action = request.data.get('action')
        notes = request.data.get('notes', '')
        
        if action not in ['save', 'finalize', 'search_again', 'no_match']:
            return Response(
                {'error': 'Invalid closure action'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Close the session
        session.close_session(action, notes)
        
        # Prepare feedback message
        feedback_messages = {
            'save': 'Search result saved for later review. You can access it from your search history.',
            'finalize': 'Match finalized successfully. The case has been marked as found and the match verified.',
            'search_again': 'Search session closed. You can start a new search anytime.',
            'no_match': 'Recorded that no match was found. The search has been archived for reference.'
        }
        
        serializer = self.get_serializer(session)
        response_data = serializer.data
        response_data['feedback'] = feedback_messages.get(action, 'Session closed successfully.')
        
        return Response(response_data)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def search_facial_recognition(request):
    """
    Search for the best facial match against uploaded image.
    Creates a search session and returns the top match with closure options.
    """
    if 'image' not in request.FILES:
        return Response(
            {'error': 'No image provided'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    image_file = request.FILES['image']
    search_query = request.data.get('query', '')
    
    # Create search session
    search_session = SearchSession.objects.create(
        user=request.user,
        uploaded_image=image_file,
        search_query=search_query
    )
    
    # Get all facial recognition images from the database
    db_images = FacialRecognitionImage.objects.filter(status='completed')
    search_session.total_candidates_searched = db_images.count()
    
    best_match = None
    best_confidence = 0.0
    
    if db_images.exists():
        # Simulate facial recognition matching (in a real scenario, this would use
        # computer vision / deep learning models)
        for db_image in db_images:
            # Simulate confidence score (in reality, this would be calculated)
            confidence = 0.85 + (0.15 * (hash(f"{image_file.name}{db_image.id}") % 100 / 100.0))
            
            if confidence > best_confidence:
                best_confidence = confidence
                
                # Create or get existing FacialMatch
                match, created = FacialMatch.objects.get_or_create(
                    missing_person=db_image.missing_person,
                    source_image=db_image,
                    defaults={
                        'match_confidence': confidence,
                        'distance_metric': 0.42,
                        'source_database': 'user_upload',
                        'source_reference': str(db_image.id),
                        'algorithm_version': 'v1.0',
                        'model_name': 'SimulatedMatcher'
                    }
                )
                if not created:
                    match.match_confidence = confidence
                    match.save()
                
                best_match = match
    
    # Update search session with results
    if best_match:
        search_session.best_match = best_match
        search_session.match_confidence = best_confidence
    
    search_session.save()
    
    # Prepare response
    response_data = {
        'search_session_id': search_session.id,
        'total_candidates_searched': search_session.total_candidates_searched,
    }
    
    if best_match:
        response_data.update({
            'match_found': True,
            'match': FacialMatchSerializer(best_match).data,
            'match_confidence': best_confidence,
            'message': f'Best match found with {best_confidence:.1%} confidence',
            'closure_options': [
                {'action': 'save', 'label': 'Save for Later', 'description': 'Save this search result for future review'},
                {'action': 'finalize', 'label': 'Finalize Match', 'description': 'Confirm this is the correct match and close the case'},
                {'action': 'search_again', 'label': 'Search Again', 'description': 'Perform another search with different parameters'}
            ]
        })
    else:
        response_data.update({
            'match_found': False,
            'message': 'No matches found in the database',
            'closure_options': [
                {'action': 'no_match', 'label': 'No Match Found', 'description': 'Record that no match was found'},
                {'action': 'search_again', 'label': 'Search Again', 'description': 'Try searching again'}
            ]
        })
    
    return Response(response_data, status=status.HTTP_200_OK)