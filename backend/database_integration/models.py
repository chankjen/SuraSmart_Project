from django.db import models
from django.utils.translation import gettext_lazy as _
import uuid


class ExternalDatabase(models.Model):
    """Configuration for external database connections (morgue, jail, police)."""
    
    DATABASE_TYPE = (
        ('morgue', _('Morgue')),
        ('jail', _('Jail/Detention')),
        ('police', _('Police Records')),
        ('public_records', _('Public Records')),
    )
    
    CONNECTION_TYPE = (
        ('rest_api', _('REST API')),
        ('soap_api', _('SOAP API')),
        ('database', _('Database')),
        ('file_sync', _('File Sync')),
    )
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255)
    database_type = models.CharField(max_length=50, choices=DATABASE_TYPE)
    organization = models.CharField(max_length=255)
    
    # Connection details
    connection_type = models.CharField(max_length=20, choices=CONNECTION_TYPE)
    endpoint_url = models.URLField(null=True, blank=True)
    database_host = models.CharField(max_length=255, blank=True)
    database_port = models.IntegerField(null=True, blank=True)
    database_name = models.CharField(max_length=255, blank=True)
    
    # Authentication
    api_key = models.CharField(max_length=500, blank=True)
    username = models.CharField(max_length=255, blank=True)
    # Password encrypted in production
    password_encrypted = models.TextField(blank=True)
    
    # Configuration
    is_active = models.BooleanField(default=True)
    rate_limit = models.IntegerField(
        default=100,
        help_text=_('Requests per minute')
    )
    timeout_seconds = models.IntegerField(default=30)
    
    # Metadata
    last_sync = models.DateTimeField(null=True, blank=True)
    sync_frequency = models.CharField(
        max_length=20,
        choices=(
            ('realtime', _('Real-time')),
            ('hourly', _('Hourly')),
            ('daily', _('Daily')),
            ('weekly', _('Weekly')),
        ),
        default='daily'
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = _('External Database')
        verbose_name_plural = _('External Databases')
        unique_together = ('name', 'organization')
    
    def __str__(self):
        return f'{self.organization} - {self.get_database_type_display()}'


class DatabaseSchema(models.Model):
    """Schema mapping for external databases."""
    
    external_db = models.ForeignKey(
        ExternalDatabase,
        on_delete=models.CASCADE,
        related_name='schemas'
    )
    
    # Field mappings
    record_id_field = models.CharField(max_length=255)
    image_url_field = models.CharField(max_length=255)
    name_field = models.CharField(max_length=255)
    date_field = models.CharField(max_length=255, blank=True)
    location_field = models.CharField(max_length=255, blank=True)
    status_field = models.CharField(max_length=255, blank=True)
    
    # Custom field mappings (JSON for flexibility)
    custom_field_mappings = models.JSONField(default=dict, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = _('Database Schema')
        verbose_name_plural = _('Database Schemas')
    
    def __str__(self):
        return f'{self.external_db.name} Schema'


class SyncLog(models.Model):
    """Log of database synchronization operations."""
    
    STATUS_CHOICES = (
        ('success', _('Success')),
        ('partial', _('Partial Success')),
        ('failed', _('Failed')),
    )
    
    external_db = models.ForeignKey(
        ExternalDatabase,
        on_delete=models.CASCADE,
        related_name='sync_logs'
    )
    
    status = models.CharField(max_length=20, choices=STATUS_CHOICES)
    records_synced = models.IntegerField(default=0)
    records_failed = models.IntegerField(default=0)
    
    started_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    error_message = models.TextField(blank=True)
    
    class Meta:
        ordering = ['-started_at']
        verbose_name = _('Sync Log')
        verbose_name_plural = _('Sync Logs')
        indexes = [
            models.Index(fields=['external_db', 'started_at']),
        ]
    
    def __str__(self):
        return f'{self.external_db.name} - {self.get_status_display()}'


class QueryLog(models.Model):
    """Log of queries to external databases."""
    
    external_db = models.ForeignKey(
        ExternalDatabase,
        on_delete=models.SET_NULL,
        null=True,
        related_name='query_logs'
    )
    
    query_type = models.CharField(
        max_length=50,
        choices=(
            ('search', _('Search')),
            ('fetch', _('Fetch')),
            ('sync', _('Sync')),
        )
    )
    query_params = models.JSONField(default=dict, blank=True)
    result_count = models.IntegerField(default=0)
    
    response_time_ms = models.IntegerField()
    status_code = models.IntegerField(null=True, blank=True)
    error_message = models.TextField(blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = _('Query Log')
        verbose_name_plural = _('Query Logs')
        indexes = [
            models.Index(fields=['external_db', 'created_at']),
            models.Index(fields=['query_type', 'created_at']),
        ]
    
    def __str__(self):
        return f'{self.external_db.name} - {self.get_query_type_display()}'
