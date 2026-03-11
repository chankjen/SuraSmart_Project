from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .models import SecureChannel, Message
from .serializers import SecureChannelSerializer, MessageSerializer
from django.db.models import Q
import hashlib

class SecureChannelViewSet(viewsets.ModelViewSet):
    """ViewSet for managing secure communication channels."""
    queryset = SecureChannel.objects.all()
    serializer_class = SecureChannelSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        return SecureChannel.objects.filter(participants=user)

    def perform_create(self, serializer):
        # Channels should ideally be auto-created when a case is 'taken'
        serializer.save()

class MessageViewSet(viewsets.ModelViewSet):
    """ViewSet for secure messages."""
    queryset = Message.objects.all()
    serializer_class = MessageSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        return Message.objects.filter(
            Q(channel__participants=user)
        )

    def perform_create(self, serializer):
        payload = self.request.data.get('encrypted_payload', '')
        # Compute hash for blockchain audit (TRD §5.1 / PRD §4.2)
        payload_hash = hashlib.sha256(payload.encode()).hexdigest()
        
        # Simple Simulated Moderation (Keyword scanning on the 'encrypted' string 
        # as a placeholder for more advanced homomorphic concepts)
        is_flagged = False
        reason = None
        suspicious_patterns = ['bribery', 'money', 'threat'] # Conceptually mapped to patterns
        if any(pattern in payload.lower() for pattern in suspicious_patterns):
            is_flagged = True
            reason = "Suspicious activity detected (AI scan)"
        
        message = serializer.save(
            sender=self.request.user, 
            payload_hash=payload_hash,
            is_flagged=is_flagged,
            moderation_reason=reason
        )
        
        # Log to blockchain (metadata only)
        from shared.blockchain import BlockchainService
        BlockchainService.log_event(
            case_id=message.channel.case.id,
            actor=self.request.user,
            action="SECURE_MESSAGE_SENT",
            metadata={
                'message_id': str(message.id),
                'payload_hash': payload_hash,
                'is_flagged': is_flagged
            }
        )

    @action(detail=False, methods=['get'])
    def by_channel(self, request):
        channel_id = request.query_params.get('channel_id')
        if not channel_id:
            return Response({'error': 'channel_id is required'}, status=status.HTTP_400_BAD_REQUEST)
        
        messages = self.get_queryset().filter(channel_id=channel_id).order_by('created_at')
        serializer = self.get_serializer(messages, many=True)
        return Response(serializer.data)
