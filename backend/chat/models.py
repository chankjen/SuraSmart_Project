from django.db import models
from django.utils.translation import gettext_lazy as _
from users.models import User
from ai_models.facial_recognition.models import MissingPerson
import uuid

class SecureChannel(models.Model):
    """A secure communication channel associated with a case."""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    case = models.OneToOneField(MissingPerson, on_delete=models.CASCADE, related_name='chat_channel')
    participants = models.ManyToManyField(User, related_name='secure_channels')
    
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = _('Secure Channel')
        verbose_name_plural = _('Secure Channels')

    def __str__(self):
        return f'Chat for Case #{self.case.id}'

class Message(models.Model):
    """An end-to-end encrypted message within a secure channel."""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    channel = models.ForeignKey(SecureChannel, on_delete=models.CASCADE, related_name='messages')
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_messages')
    
    # The actual content is encrypted on the client side (Signal Protocol simulation)
    encrypted_payload = models.TextField(help_text=_('End-to-end encrypted message content'))
    
    # Metadata for Blockchain (TRD §5.1 / PRD §4.2)
    # Storing a hash of the encrypted payload to prevent dispute/tampering
    payload_hash = models.CharField(max_length=64, help_text=_('SHA-256 hash of the encrypted payload'))
    blockchain_tx_id = models.CharField(max_length=100, blank=True, null=True)
    
    # Moderation (PRD §4.2)
    # AI keyword scanning trigger (Simulated via homomorphic conceptually or metadata analysis)
    is_flagged = models.BooleanField(default=False)
    moderation_reason = models.CharField(max_length=255, blank=True, null=True)
    
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        ordering = ['created_at']
        verbose_name = _('Encrypted Message')
        verbose_name_plural = _('Encrypted Messages')

    def __str__(self):
        return f'Message from {self.sender.username} at {self.created_at}'
