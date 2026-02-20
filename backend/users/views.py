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
        user.is_verified = True
        user.save()
        return Response({'detail': 'User verified successfully'})


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


class PermissionViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for viewing permissions."""
    queryset = Permission.objects.all()
    serializer_class = PermissionSerializer
    permission_classes = [permissions.IsAdminUser]
