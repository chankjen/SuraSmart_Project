"""API Serializers for Notifications app."""
from rest_framework import serializers
from notifications.models import Notification, NotificationPreference


class NotificationSerializer(serializers.ModelSerializer):
    """Serializer for notifications."""
    
    class Meta:
        model = Notification
        fields = [
            'id', 'recipient', 'notification_type', 'title', 'message',
            'related_match', 'status', 'sent_at', 'read_at', 'created_at'
        ]
        read_only_fields = ['id', 'sent_at', 'read_at', 'created_at']


class NotificationPreferenceSerializer(serializers.ModelSerializer):
    """Serializer for notification preferences."""
    
    class Meta:
        model = NotificationPreference
        fields = [
            'user', 'email_notifications', 'sms_notifications', 'push_notifications',
            'match_found', 'verification_needed', 'case_update',
            'digest_frequency', 'quiet_hours_enabled', 'quiet_hours_start', 'quiet_hours_end'
        ]
        read_only_fields = ['user']
