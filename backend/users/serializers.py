"""API Serializers for Users app."""
from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from django.conf import settings
from users.models import User, AuditLog, Permission


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    """Custom token serializer that includes user info."""
    
    def validate(self, attrs):
        data = super().validate(attrs)
        
        # In production, require verified status. In development, allow pending.
        if not settings.DEBUG:
            if self.user.verification_status != 'verified':
                raise serializers.ValidationError(
                    'Account is not verified. Please contact administrator.'
                )
        
        if not self.user.is_active_user:
            raise serializers.ValidationError(
                'Account is deactivated. Please contact administrator.'
            )
        
        # Add user information to response (exclude sensitive info)
        data['user'] = {
            'id': self.user.id,
            'username': self.user.username,
            'email': self.user.email,
            'first_name': self.user.first_name,
            'last_name': self.user.last_name,
            'role': self.user.role,
            'is_staff': self.user.is_staff,
        }
        
        return data

class UserSerializer(serializers.ModelSerializer):
    """Serializer for User model."""
    
    class Meta:
        model = User
        fields = [
            'id', 'username', 'email', 'first_name', 'last_name',
            'role', 'phone_number', 'organization', 'verification_status',
            'national_id', 'service_id', 'police_rank', 'government_security_id',
            'government_position', 'position_specify',
            'is_active_user', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class UserCreateSerializer(serializers.ModelSerializer):
    """Serializer for user registration."""
    password = serializers.CharField(write_only=True, min_length=8)
    
    class Meta:
        model = User
        fields = [
            'username', 'email', 'password', 'first_name', 'last_name', 'role',
            'national_id', 'service_id', 'police_rank', 'government_security_id',
            'government_position', 'position_specify'
        ]
    
    def validate(self, attrs):
        """Validate role-specific fields."""
        role = attrs.get('role')
        
        if role == 'family_member':
            if not attrs.get('national_id'):
                raise serializers.ValidationError({'national_id': 'National ID is required for Family Members.'})
        
        elif role == 'police_officer':
            if not attrs.get('service_id'):
                raise serializers.ValidationError({'service_id': 'Service ID is required for Police Officers.'})
            if not attrs.get('police_rank'):
                raise serializers.ValidationError({'police_rank': 'Police rank is required for Police Officers.'})
        
        elif role == 'government_official':
            if not attrs.get('government_security_id'):
                raise serializers.ValidationError({'government_security_id': 'Government Security ID is required for Government Officials.'})
            if not attrs.get('government_position'):
                raise serializers.ValidationError({'government_position': 'Government position is required for Government Officials.'})
            if attrs.get('government_position') == 'other' and not attrs.get('position_specify'):
                raise serializers.ValidationError({'position_specify': 'Please specify the position when selecting "Other".'})
        
        return attrs
    
    def create(self, validated_data):
        user = User.objects.create_user(**validated_data)
        return user


class AuditLogSerializer(serializers.ModelSerializer):
    """Serializer for audit logs."""
    user_username = serializers.CharField(source='user.username', read_only=True)
    
    class Meta:
        model = AuditLog
        fields = [
            'id', 'user', 'user_username', 'action', 'description',
            'ip_address', 'timestamp', 'metadata'
        ]
        read_only_fields = fields


class PermissionSerializer(serializers.ModelSerializer):
    """Serializer for permissions."""
    
    class Meta:
        model = Permission
        fields = ['id', 'role', 'resource', 'can_read', 'can_write', 'can_delete']
