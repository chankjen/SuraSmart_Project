"""
Admin configuration for SuraSmart backend.
"""
from django.contrib import admin
from users.models import User, AuditLog, Permission
from facial_recognition.models import (
    MissingPerson, FacialRecognitionImage, FacialMatch, ProcessingQueue
)
from notifications.models import Notification, NotificationPreference
from database_integration.models import (
    ExternalDatabase, DatabaseSchema, SyncLog, QueryLog
)


# Users Admin
@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ('username', 'email', 'role', 'verification_status', 'created_at')
    list_filter = ('role', 'verification_status', 'created_at')
    search_fields = ('username', 'email')
    readonly_fields = ('created_at', 'updated_at')
    
    fieldsets = (
        ('Personal Information', {'fields': ('username', 'email', 'first_name', 'last_name')}),
        ('Contact', {'fields': ('phone_number', 'organization')}),
        ('Role & Permissions', {'fields': ('role', 'is_active_user', 'verification_status')}),
        ('Timestamps', {'fields': ('created_at', 'updated_at'), 'classes': ('collapse',)}),
    )


@admin.register(AuditLog)
class AuditLogAdmin(admin.ModelAdmin):
    list_display = ('user', 'action', 'timestamp', 'ip_address')
    list_filter = ('action', 'timestamp')
    search_fields = ('user__username', 'description')
    readonly_fields = ('timestamp',)


@admin.register(Permission)
class PermissionAdmin(admin.ModelAdmin):
    list_display = ('role', 'resource', 'can_read', 'can_write', 'can_delete')
    list_filter = ('role', 'resource')


# Facial Recognition Admin
@admin.register(MissingPerson)
class MissingPersonAdmin(admin.ModelAdmin):
    list_display = ('full_name', 'status', 'reported_by', 'date_reported')
    list_filter = ('status', 'date_reported', 'gender')
    search_fields = ('full_name', 'description')
    readonly_fields = ('created_at', 'updated_at')
    
    fieldsets = (
        ('Basic Information', {'fields': ('full_name', 'reported_by', 'status')}),
        ('Details', {'fields': ('description', 'age', 'gender', 'identifying_marks')}),
        ('Location', {'fields': ('last_seen_date', 'last_seen_location')}),
        ('Timestamps', {'fields': ('date_reported', 'created_at', 'updated_at'), 'classes': ('collapse',)}),
    )


@admin.register(FacialRecognitionImage)
class FacialRecognitionImageAdmin(admin.ModelAdmin):
    list_display = ('missing_person', 'status', 'is_primary', 'created_at')
    list_filter = ('status', 'is_primary', 'created_at')
    search_fields = ('missing_person__full_name',)
    readonly_fields = ('image_hash', 'created_at', 'processed_at')


@admin.register(FacialMatch)
class FacialMatchAdmin(admin.ModelAdmin):
    list_display = ('missing_person', 'match_confidence', 'status', 'source_database', 'created_at')
    list_filter = ('status', 'source_database', 'created_at')
    search_fields = ('missing_person__full_name',)
    readonly_fields = ('created_at', 'updated_at')


@admin.register(ProcessingQueue)
class ProcessingQueueAdmin(admin.ModelAdmin):
    list_display = ('image', 'status', 'priority', 'retries', 'created_at')
    list_filter = ('status', 'priority')
    readonly_fields = ('created_at',)


# Notifications Admin
@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ('recipient', 'notification_type', 'status', 'created_at')
    list_filter = ('notification_type', 'status', 'created_at')
    search_fields = ('recipient__username', 'title')
    readonly_fields = ('created_at',)


@admin.register(NotificationPreference)
class NotificationPreferenceAdmin(admin.ModelAdmin):
    list_display = ('user', 'digest_frequency', 'email_notifications', 'sms_notifications')
    list_filter = ('digest_frequency',)


# Database Integration Admin
@admin.register(ExternalDatabase)
class ExternalDatabaseAdmin(admin.ModelAdmin):
    list_display = ('name', 'database_type', 'organization', 'is_active', 'last_sync')
    list_filter = ('database_type', 'is_active')
    search_fields = ('name', 'organization')
    readonly_fields = ('last_sync', 'created_at', 'updated_at')


@admin.register(DatabaseSchema)
class DatabaseSchemaAdmin(admin.ModelAdmin):
    list_display = ('external_db', 'record_id_field', 'created_at')
    search_fields = ('external_db__name',)


@admin.register(SyncLog)
class SyncLogAdmin(admin.ModelAdmin):
    list_display = ('external_db', 'status', 'records_synced', 'started_at')
    list_filter = ('status', 'started_at')
    search_fields = ('external_db__name',)
    readonly_fields = ('started_at', 'completed_at')


@admin.register(QueryLog)
class QueryLogAdmin(admin.ModelAdmin):
    list_display = ('external_db', 'query_type', 'response_time_ms', 'created_at')
    list_filter = ('query_type', 'created_at')
    search_fields = ('external_db__name',)
