from rest_framework import serializers
from .models import SecureChannel, Message
from users.serializers import UserSerializer

class MessageSerializer(serializers.ModelSerializer):
    sender_name = serializers.CharField(source='sender.username', read_only=True)
    
    class Meta:
        model = Message
        fields = [
            'id', 'channel', 'sender', 'sender_name', 'encrypted_payload', 
            'payload_hash', 'blockchain_tx_id', 'is_flagged', 
            'moderation_reason', 'is_read', 'created_at'
        ]
        read_only_fields = ['id', 'created_at', 'is_flagged', 'moderation_reason', 'blockchain_tx_id']

class SecureChannelSerializer(serializers.ModelSerializer):
    participants_details = UserSerializer(source='participants', many=True, read_only=True)
    last_message = serializers.SerializerMethodField()
    case_name = serializers.CharField(source='case.full_name', read_only=True)
    
    class Meta:
        model = SecureChannel
        fields = ['id', 'case', 'case_name', 'participants', 'participants_details', 'is_active', 'created_at', 'last_message']
        read_only_fields = ['id', 'created_at']

    def get_last_message(self, obj):
        message = obj.messages.order_by('-created_at').first()
        if message:
            return MessageSerializer(message).data
        return None
