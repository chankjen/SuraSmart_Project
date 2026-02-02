"""API Serializers for Users app."""
from rest_framework import serializers
from users.models import User, AuditLog, Permission


class UserSerializer(serializers.ModelSerializer):
    """Serializer for User model."""
    
    class Meta:
        model = User
        fields = [
            'id', 'username', 'email', 'first_name', 'last_name',
            'role', 'phone_number', 'organization', 'verification_status',
            'is_active_user', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class UserCreateSerializer(serializers.ModelSerializer):
    """Serializer for user registration."""
    password = serializers.CharField(write_only=True, min_length=8)
    
    class Meta:
        model = User
        fields = ['username', 'email', 'password', 'first_name', 'last_name', 'role']
    
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
