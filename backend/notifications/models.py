from django.db import models
from django.utils.translation import gettext_lazy as _
from users.models import User
from facial_recognition.models import FacialMatch
import uuid


class Notification(models.Model):
    """Notification sent when matches are found."""
    
    NOTIFICATION_TYPE = (
        ('match_found', _('Match Found')),
        ('verification_needed', _('Verification Needed')),
        ('case_update', _('Case Update')),
        ('system_alert', _('System Alert')),
    )
    
    STATUS_CHOICES = (
        ('pending', _('Pending')),
        ('sent', _('Sent')),
        ('read', _('Read')),
        ('failed', _('Failed')),
    )
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    recipient = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='notifications'
    )
    notification_type = models.CharField(max_length=30, choices=NOTIFICATION_TYPE)
    title = models.CharField(max_length=255)
    message = models.TextField()
    
    # Reference to related objects
    related_match = models.ForeignKey(
        FacialMatch,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='notifications'
    )
    
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    
    # Channel preferences
    send_email = models.BooleanField(default=True)
    send_sms = models.BooleanField(default=False)
    send_push = models.BooleanField(default=False)
    
    sent_at = models.DateTimeField(null=True, blank=True)
    read_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = _('Notification')
        verbose_name_plural = _('Notifications')
        indexes = [
            models.Index(fields=['recipient', 'status']),
            models.Index(fields=['created_at']),
        ]
    
    def __str__(self):
        return f'{self.recipient.username} - {self.title}'


class NotificationPreference(models.Model):
    """User preferences for notifications."""
    
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='notification_preferences'
    )
    
    # Channel preferences
    email_notifications = models.BooleanField(default=True)
    sms_notifications = models.BooleanField(default=False)
    push_notifications = models.BooleanField(default=False)
    
    # Notification type preferences
    match_found = models.BooleanField(default=True)
    verification_needed = models.BooleanField(default=True)
    case_update = models.BooleanField(default=True)
    
    # Frequency settings
    digest_frequency = models.CharField(
        max_length=20,
        choices=(
            ('instant', _('Instant')),
            ('hourly', _('Hourly')),
            ('daily', _('Daily')),
        ),
        default='instant'
    )
    
    quiet_hours_enabled = models.BooleanField(default=False)
    quiet_hours_start = models.TimeField(null=True, blank=True)
    quiet_hours_end = models.TimeField(null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = _('Notification Preference')
        verbose_name_plural = _('Notification Preferences')
    
    def __str__(self):
        return f'{self.user.username} preferences'
