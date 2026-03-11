"""API Views for Users app."""
from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework_simplejwt.views import TokenObtainPairView
from django.contrib.auth import authenticate
from users.models import User, AuditLog, Permission
from users.serializers import (
    UserSerializer, UserCreateSerializer, AuditLogSerializer, PermissionSerializer,
    CustomTokenObtainPairSerializer
)
from users.permissions import IsGovernmentOrAdmin


class CustomTokenObtainPairView(TokenObtainPairView):
    """Custom token view that returns user info with the token."""
    serializer_class = CustomTokenObtainPairSerializer

class UserViewSet(viewsets.ModelViewSet):
    """ViewSet for user management."""
    queryset = User.objects.all()
    serializer_class = UserSerializer
    
    def get_permissions(self):
        if self.action == 'create':
            return [AllowAny()]
        elif self.action in ['list', 'retrieve']:
            # Government officials and admins can list/view users
            return [permissions.IsAuthenticated(), IsGovernmentOrAdmin()]
        elif self.action == 'verify':
            # Only admins can verify users
            return [permissions.IsAdminUser()]
        return [IsAuthenticated()]
    
    def get_serializer_class(self):
        if self.action == 'create':
            return UserCreateSerializer
        return UserSerializer
    
    def get_queryset(self):
        """Filter queryset based on user permissions."""
        if self.request.user.is_staff:
            return User.objects.all()
        # Non-admins can only see themselves
        return User.objects.filter(id=self.request.user.id)
    
    @action(detail=False, methods=['get'], permission_classes=[IsAuthenticated])
    def me(self, request):
        """Get current user profile."""
        serializer = self.get_serializer(request.user)
        return Response(serializer.data)
    
    @action(detail=False, methods=['post'], permission_classes=[IsAuthenticated])
    def change_password(self, request):
        """Change user password."""
        user = request.user
        old_password = request.data.get('old_password')
        new_password = request.data.get('new_password')
        
        if not user.check_password(old_password):
            return Response(
                {'error': 'Invalid old password'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
    @action(detail=True, methods=['post'], permission_classes=[permissions.IsAdminUser])
    def verify(self, request, pk=None):
        """Verify a user account (admin only)."""
        user = self.get_object()
        user.verification_status = 'verified'
        user.save()
        return Response({'detail': 'User verified successfully'})

    @action(detail=True, methods=['post'], permission_classes=[permissions.IsAdminUser])
    def approve(self, request, pk=None):
        """Approve a user registration (admin only)."""
        user = self.get_object()
        user.verification_status = 'verified'
        # In a real app, record the admin who approved and the verification details
        user.save()
        return Response({'detail': 'User approved successfully'})

    @action(detail=False, methods=['get'], permission_classes=[permissions.IsAdminUser])
    def system_stats(self, request):
        """Get system-wide statistics for the admin dashboard."""
        stats = {
            'totalUsers': User.objects.count(),
            'pendingVerification': User.objects.filter(verification_status='pending').count(),
            'verifiedUsers': User.objects.filter(verification_status='verified').count(),
            'systemUptime': '99.95%' # Mocked
        }
        return Response(stats)

    @action(detail=False, methods=['post'], permission_classes=[permissions.IsAdminUser])
    def verify_mfa(self, request):
        """Mock MFA verification for admin actions."""
        # In production, use pyotp or django-two-factor-auth
        return Response({'detail': 'MFA verified (Mock)'})

    @action(detail=False, methods=['post'], permission_classes=[permissions.IsAdminUser])
    def send_approval_email(self, request):
        """Mock sending approval email."""
        # In production, use SendGrid or Django's send_mail
        return Response({'detail': 'Approval email sent (Mock)'})


class AuditLogViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for audit logs (read-only)."""
    queryset = AuditLog.objects.all()
    serializer_class = AuditLogSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        """Filter logs by user if not admin."""
        if self.request.user.is_staff:
            return AuditLog.objects.all()
        return AuditLog.objects.filter(user=self.request.user)

    @action(detail=False, methods=['post'], permission_classes=[IsAuthenticated])
    def log_event(self, request):
        """Client-side logging of audit events."""
        action = request.data.get('action')
        metadata = request.data.get('metadata', {})
        
        # In production, validate actor_id matches request.user
        AuditLog.objects.create(
            user=request.user,
            action='api_call', # Map to existing choice
            description=f"Client Action: {action}",
            ip_address="127.0.0.1", # In production, get actual IP
            metadata=metadata
        )
        return Response({'detail': 'Event logged'})

    @action(detail=False, methods=['get'], permission_classes=[permissions.IsAdminUser])
    def export(self, request):
        """Export audit logs as CSV."""
        import csv
        from django.http import HttpResponse
        
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="audit_logs.csv"'
        
        writer = csv.writer(response)
        writer.writerow(['Timestamp', 'User', 'Action', 'Description', 'IP Address'])
        
        logs = AuditLog.objects.all()
        for log in logs:
            writer.writerow([log.timestamp, log.user.username if log.user else 'System', log.action, log.description, log.ip_address])
            
        return response


class PermissionViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for viewing permissions."""
    queryset = Permission.objects.all()
    serializer_class = PermissionSerializer
    permission_classes = [permissions.IsAdminUser]
