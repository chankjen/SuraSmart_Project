"""URLs for Database Integration app."""
from django.urls import path, include
from rest_framework.routers import SimpleRouter
from database_integration.views import (
    ExternalDatabaseViewSet, DatabaseSchemaViewSet,
    SyncLogViewSet, QueryLogViewSet
)

router = SimpleRouter()
router.register(r'external-databases', ExternalDatabaseViewSet, basename='external-database')
router.register(r'schemas', DatabaseSchemaViewSet, basename='database-schema')
router.register(r'sync-logs', SyncLogViewSet, basename='sync-log')
router.register(r'query-logs', QueryLogViewSet, basename='query-log')

urlpatterns = [
    path('', include(router.urls)),
]
