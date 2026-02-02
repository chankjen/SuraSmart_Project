from django.db import models
from django.utils.translation import gettext_lazy as _
from django.core.validators import FileExtensionValidator
from users.models import User
import uuid


class MissingPerson(models.Model):
    """Record of a reported missing person."""
    
    STATUS_CHOICES = (
        ('reported', _('Reported')),
        ('searching', _('Searching')),
        ('found', _('Found')),
        ('closed', _('Case Closed')),
    )
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    reported_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='reported_missing_persons'
    )
    full_name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='reported'
    )
    date_reported = models.DateTimeField(auto_now_add=True)
    last_seen_date = models.DateTimeField(null=True, blank=True)
    last_seen_location = models.CharField(max_length=255, blank=True)
    
    # Metadata for search optimization
    age = models.IntegerField(null=True, blank=True)
    gender = models.CharField(
        max_length=20,
        choices=(('male', _('Male')), ('female', _('Female')), ('other', _('Other'))),
        blank=True
    )
    identifying_marks = models.TextField(blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = _('Missing Person')
        verbose_name_plural = _('Missing Persons')
        indexes = [
            models.Index(fields=['status', 'date_reported']),
        ]
    
    def __str__(self):
        return f'{self.full_name} - {self.get_status_display()}'


class FacialRecognitionImage(models.Model):
    """Uploaded image for facial recognition processing."""
    
    PROCESSING_STATUS = (
        ('uploaded', _('Uploaded')),
        ('processing', _('Processing')),
        ('completed', _('Completed')),
        ('failed', _('Failed')),
    )
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    missing_person = models.ForeignKey(
        MissingPerson,
        on_delete=models.CASCADE,
        related_name='facial_recognition_images'
    )
    image_file = models.ImageField(
        upload_to='facial_recognition/%Y/%m/%d/',
        validators=[FileExtensionValidator(allowed_extensions=['jpg', 'jpeg', 'png'])]
    )
    image_hash = models.CharField(
        max_length=64,
        unique=True,
        help_text=_('SHA256 hash of image for deduplication')
    )
    is_primary = models.BooleanField(
        default=False,
        help_text=_('Primary image used for searches')
    )
    status = models.CharField(
        max_length=20,
        choices=PROCESSING_STATUS,
        default='uploaded'
    )
    
    # Extracted facial features (for future multimodal matching)
    face_embedding = models.JSONField(null=True, blank=True)
    face_confidence = models.FloatField(
        null=True,
        blank=True,
        help_text=_('Confidence score that image contains a face')
    )
    
    processing_error = models.TextField(blank=True, null=True)
    processed_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = _('Facial Recognition Image')
        verbose_name_plural = _('Facial Recognition Images')
    
    def __str__(self):
        return f'{self.missing_person.full_name} - {self.get_status_display()}'


class FacialMatch(models.Model):
    """Result of facial recognition comparison."""
    
    MATCH_STATUS = (
        ('pending_review', _('Pending Review')),
        ('verified', _('Verified Match')),
        ('false_positive', _('False Positive')),
        ('rejected', _('Rejected')),
    )
    
    SOURCE_CHOICES = (
        ('morgue', _('Morgue Database')),
        ('jail', _('Jail Database')),
        ('police', _('Police Database')),
        ('user_upload', _('User Upload')),
    )
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    missing_person = models.ForeignKey(
        MissingPerson,
        on_delete=models.CASCADE,
        related_name='facial_matches'
    )
    source_image = models.ForeignKey(
        FacialRecognitionImage,
        on_delete=models.SET_NULL,
        null=True,
        related_name='matches'
    )
    
    # Match metadata
    match_confidence = models.FloatField(
        help_text=_('Confidence score between 0 and 1')
    )
    distance_metric = models.FloatField(
        null=True,
        blank=True,
        help_text=_('Facial distance metric from comparison')
    )
    
    source_database = models.CharField(
        max_length=20,
        choices=SOURCE_CHOICES,
        default='user_upload'
    )
    source_reference = models.CharField(
        max_length=255,
        help_text=_('ID/reference from external database')
    )
    
    status = models.CharField(
        max_length=20,
        choices=MATCH_STATUS,
        default='pending_review'
    )
    
    # Audit fields
    verified_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='verified_matches'
    )
    verified_at = models.DateTimeField(null=True, blank=True)
    verification_notes = models.TextField(blank=True)
    
    # Matching algorithm info
    algorithm_version = models.CharField(max_length=50)
    model_name = models.CharField(max_length=50, default='Facenet')
    
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    # Blockchain hash placeholder
    blockchain_hash = models.CharField(max_length=255, blank=True, null=True)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = _('Facial Match')
        verbose_name_plural = _('Facial Matches')
        indexes = [
            models.Index(fields=['missing_person', 'status']),
            models.Index(fields=['match_confidence', 'created_at']),
        ]
    
    def __str__(self):
        return f'{self.missing_person.full_name} - Match {self.match_confidence:.2%}'


class ProcessingQueue(models.Model):
    """Queue for asynchronous facial recognition processing."""
    
    PRIORITY_CHOICES = (
        ('low', _('Low')),
        ('normal', _('Normal')),
        ('high', _('High')),
        ('urgent', _('Urgent')),
    )
    
    STATUS_CHOICES = (
        ('queued', _('Queued')),
        ('processing', _('Processing')),
        ('completed', _('Completed')),
        ('failed', _('Failed')),
    )
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    image = models.OneToOneField(
        FacialRecognitionImage,
        on_delete=models.CASCADE,
        related_name='processing_queue'
    )
    priority = models.CharField(max_length=10, choices=PRIORITY_CHOICES, default='normal')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='queued')
    
    retries = models.IntegerField(default=0)
    max_retries = models.IntegerField(default=3)
    
    started_at = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    error_message = models.TextField(blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    
    class Meta:
        ordering = ['-priority', 'created_at']
        verbose_name = _('Processing Queue Item')
        verbose_name_plural = _('Processing Queue Items')
        indexes = [
            models.Index(fields=['status', 'priority']),
        ]
    
    def __str__(self):
        return f'{self.image.missing_person.full_name} - {self.get_status_display()}'
