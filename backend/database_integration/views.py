"""API Views for Database Integration app."""
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters
from database_integration.models import (
    ExternalDatabase, DatabaseSchema, SyncLog, QueryLog
)
from database_integration.serializers import (
    ExternalDatabaseSerializer, DatabaseSchemaSerializer,
    SyncLogSerializer, QueryLogSerializer
)


class ExternalDatabaseViewSet(viewsets.ModelViewSet):
    """ViewSet for external database configurations."""
    queryset = ExternalDatabase.objects.all()
    serializer_class = ExternalDatabaseSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['database_type', 'is_active']
    search_fields = ['name', 'organization']
    
    @action(detail=True, methods=['post'])
    def test_connection(self, request, pk=None):
        """Test connection to external database."""
        external_db = self.get_object()
        # TODO: Implement connection test
        return Response({
            'status': 'success',
            'message': 'Connection test will be implemented in Phase 2'
        })
    
    @action(detail=True, methods=['post'])
    def sync_now(self, request, pk=None):
        """Trigger immediate sync with external database."""
        external_db = self.get_object()
        # TODO: Implement sync trigger
        return Response({
            'status': 'queued',
            'message': 'Sync will be implemented in Phase 2'
        })


class DatabaseSchemaViewSet(viewsets.ModelViewSet):
    """ViewSet for database schema mappings."""
    queryset = DatabaseSchema.objects.all()
    serializer_class = DatabaseSchemaSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['external_db']


class SyncLogViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for sync logs."""
    queryset = SyncLog.objects.all()
    serializer_class = SyncLogSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['external_db', 'status']
    ordering_fields = ['started_at']
    ordering = ['-started_at']


class QueryLogViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for query logs."""
    queryset = QueryLog.objects.all()
    serializer_class = QueryLogSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['external_db', 'query_type']
    ordering_fields = ['created_at', 'response_time_ms']
    ordering = ['-created_at']
