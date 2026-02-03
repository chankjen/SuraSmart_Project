"""API Views for Facial Recognition app."""
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters
from facial_recognition.models import (
    MissingPerson, FacialRecognitionImage, FacialMatch, ProcessingQueue
)
from facial_recognition.serializers import (
    MissingPersonSerializer, FacialRecognitionImageSerializer,
    FacialMatchSerializer, ProcessingQueueSerializer
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
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['status', 'priority']
    ordering_fields = ['created_at', 'priority']
    ordering = ['priority', 'created_at']
