from django.db import models
from django.utils.translation import gettext_lazy as _
from django.core.validators import FileExtensionValidator
from users.models import User
import uuid


class MissingPerson(models.Model):
    """Record of a reported missing person."""
    
    STATUS_CHOICES = (
        ('REPORTED', _('Reported')),
        ('UNDER_INVESTIGATION', _('Under Investigation')),
        ('MATCH_FOUND', _('Match Found')),
        ('PENDING_CLOSURE', _('Pending Closure')),
        ('CLOSED', _('Closed')),
        ('NO_MATCH', _('No Match')),
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
    
    jurisdiction = models.CharField(
        max_length=50,
        choices=(('KE', _('Kenya')), ('EU', _('European Union')), ('US', _('United States'))),
        default='KE'
    )
    emergency_flag = models.BooleanField(default=False)
    dual_signature_family = models.BooleanField(default=False)
    dual_signature_police = models.BooleanField(default=False)
    resolved_at = models.DateTimeField(null=True, blank=True)
    retention_expiry_date = models.DateTimeField(null=True, blank=True)
    
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

    def save(self, *args, **kwargs):
        """Override save to handle retention logic."""
        import django.utils.timezone as tz
        from datetime import timedelta
        
        if not self.created_at:
            # For new objects, created_at isn't set yet
            now = tz.now()
        else:
            now = self.created_at

        if self.status == 'CLOSED' and not self.resolved_at:
            self.resolved_at = tz.now()
            self.retention_expiry_date = self.resolved_at # Purge immediately on close per TRD 5.2
        elif not self.retention_expiry_date:
            # Default 5 years for open cases
            self.retention_expiry_date = now + timedelta(days=5*365)
            
        super().save(*args, **kwargs)


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
    # Blockchain hash (TRD §5.1)
    blockchain_hash = models.CharField(max_length=64, blank=True, null=True, unique=True)

    # Human-in-the-Loop flag (TRD Section 4.2.3)
    # Automatically set True when 90% <= confidence < 98%
    requires_human_review = models.BooleanField(
        default=False,
        help_text=_('Flagged for human review when confidence is borderline (90-98%)')
    )
    
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


class BiometricEmbedding(models.Model):
    """Vector storage for facial embeddings (Optimized for TimescaleDB/pgvector)."""
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    case = models.ForeignKey(
        MissingPerson,
        on_delete=models.CASCADE,
        related_name='biometric_embeddings'
    )
    # Using JSONField as fallback for pgvector if not configured
    embedding_vector = models.JSONField(help_text=_('512-dimensional facial embedding vector'))
    voice_print = models.BinaryField(null=True, blank=True)
    image_quality_score = models.FloatField(default=0.0)
    uploaded_at = models.DateTimeField(auto_now_add=True)
    purge_after = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['-uploaded_at']
        verbose_name = _('Biometric Embedding')
        verbose_name_plural = _('Biometric Embeddings')

    def __str__(self):
        return f'Embedding for {self.case.full_name} ({self.uploaded_at})'


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


class SearchSession(models.Model):
    """Tracks facial recognition search sessions and their outcomes."""
    
    CLOSURE_CHOICES = (
        ('save', _('Save for Later')),
        ('finalize', _('Finalize Match')),
        ('search_again', _('Search Again')),
        ('no_match', _('No Match Found')),
    )
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='search_sessions'
    )
    
    # Search input
    uploaded_image = models.ImageField(
        upload_to='search_sessions/%Y/%m/%d/',
        validators=[FileExtensionValidator(allowed_extensions=['jpg', 'jpeg', 'png'])]
    )
    search_query = models.TextField(blank=True, help_text=_('Optional search parameters'))
    
    # Search results
    best_match = models.ForeignKey(
        FacialMatch,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='search_sessions'
    )
    match_confidence = models.FloatField(null=True, blank=True)
    total_candidates_searched = models.IntegerField(default=0)
    
    # Session status
    is_closed = models.BooleanField(default=False)
    closure_action = models.CharField(
        max_length=20,
        choices=CLOSURE_CHOICES,
        null=True,
        blank=True
    )
    closure_notes = models.TextField(blank=True)
    closed_at = models.DateTimeField(null=True, blank=True)

    # BIPA Compliance (TRD Section 5.1.2): explicit consent before biometric search
    consent_given = models.BooleanField(
        default=False,
        help_text=_('User explicitly confirmed consent before biometric search')
    )

    # Audit
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = _('Search Session')
        verbose_name_plural = _('Search Sessions')
        indexes = [
            models.Index(fields=['user', 'is_closed']),
            models.Index(fields=['created_at', 'is_closed']),
        ]
    
    def __str__(self):
        return f'Search by {self.user.username} - {self.created_at.date()}'
    
    def close_session(self, action, notes=''):
        """Close the search session with the specified action."""
        import django.utils.timezone as tz
        self.closure_action = action
        self.closure_notes = notes
        self.is_closed = True
        self.closed_at = tz.now()
        self.save()
        
        # If finalizing a match, update the match status
        if action == 'finalize' and self.best_match:
            self.best_match.status = 'verified'
            self.best_match.verified_by = self.user
            self.best_match.verification_notes = f'Finalized from search session: {notes}'
            self.best_match.save()
            
            # Update missing person status
            missing_person = self.best_match.missing_person
            missing_person.status = 'CLOSED'
            missing_person.save()
