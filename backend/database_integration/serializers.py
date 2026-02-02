"""API Serializers for Database Integration app."""
from rest_framework import serializers
from database_integration.models import (
    ExternalDatabase, DatabaseSchema, SyncLog, QueryLog
)


class DatabaseSchemaSerializer(serializers.ModelSerializer):
    """Serializer for database schema mappings."""
    
    class Meta:
        model = DatabaseSchema
        fields = [
            'id', 'external_db', 'record_id_field', 'image_url_field',
            'name_field', 'date_field', 'location_field', 'status_field',
            'custom_field_mappings', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class ExternalDatabaseSerializer(serializers.ModelSerializer):
    """Serializer for external database configurations."""
    schemas = DatabaseSchemaSerializer(many=True, read_only=True)
    
    class Meta:
        model = ExternalDatabase
        fields = [
            'id', 'name', 'database_type', 'organization', 'connection_type',
            'endpoint_url', 'database_host', 'database_port', 'database_name',
            'is_active', 'rate_limit', 'timeout_seconds', 'last_sync',
            'sync_frequency', 'schemas', 'created_at', 'updated_at'
        ]
        read_only_fields = [
            'id', 'created_at', 'updated_at', 'last_sync', 'schemas',
            'password_encrypted'  # Never expose in API
        ]


class SyncLogSerializer(serializers.ModelSerializer):
    """Serializer for sync logs."""
    external_db_name = serializers.CharField(
        source='external_db.name', read_only=True
    )
    
    class Meta:
        model = SyncLog
        fields = [
            'id', 'external_db', 'external_db_name', 'status',
            'records_synced', 'records_failed', 'started_at',
            'completed_at', 'error_message'
        ]
        read_only_fields = fields


class QueryLogSerializer(serializers.ModelSerializer):
    """Serializer for query logs."""
    external_db_name = serializers.CharField(
        source='external_db.name', read_only=True
    )
    
    class Meta:
        model = QueryLog
        fields = [
            'id', 'external_db', 'external_db_name', 'query_type',
            'result_count', 'response_time_ms', 'status_code',
            'error_message', 'created_at'
        ]
        read_only_fields = fields
