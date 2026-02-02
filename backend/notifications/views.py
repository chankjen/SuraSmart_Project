"""API Views for Notifications app."""
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters
from notifications.models import Notification, NotificationPreference
from notifications.serializers import NotificationSerializer, NotificationPreferenceSerializer


class NotificationViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for notifications."""
    serializer_class = NotificationSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['notification_type', 'status']
    ordering_fields = ['created_at']
    ordering = ['-created_at']
    
    def get_queryset(self):
        return Notification.objects.filter(recipient=self.request.user)
    
    @action(detail=True, methods=['post'])
    def mark_as_read(self, request, pk=None):
        """Mark notification as read."""
        notification = self.get_object()
        if notification.recipient != request.user:
            return Response(
                {'error': 'Permission denied'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        from django.utils import timezone
        notification.read_at = timezone.now()
        notification.status = 'read'
        notification.save()
        
        serializer = self.get_serializer(notification)
        return Response(serializer.data)
    
    @action(detail=False, methods=['post'])
    def mark_all_as_read(self, request):
        """Mark all notifications as read."""
        from django.utils import timezone
        
        Notification.objects.filter(
            recipient=request.user,
            status='sent'
        ).update(
            read_at=timezone.now(),
            status='read'
        )
        
        return Response({'detail': 'All notifications marked as read'})


class NotificationPreferenceViewSet(viewsets.ViewSet):
    """ViewSet for notification preferences."""
    permission_classes = [IsAuthenticated]
    
    @action(detail=False, methods=['get', 'put'])
    def my_preferences(self, request):
        """Get or update current user's notification preferences."""
        preference, created = NotificationPreference.objects.get_or_create(
            user=request.user
        )
        
        if request.method == 'GET':
            serializer = NotificationPreferenceSerializer(preference)
            return Response(serializer.data)
        
        elif request.method == 'PUT':
            serializer = NotificationPreferenceSerializer(
                preference,
                data=request.data,
                partial=True
            )
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
