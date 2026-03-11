"""Health check and status endpoints."""
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from django.db import connection
from django.core.cache import cache
from celery import current_app as celery_app
import json


@api_view(['GET'])
@permission_classes([AllowAny])
def welcome(request):
    """Welcome endpoint for the SuraSmart API."""
    return Response({
        'message': 'Welcome to SuraSmart Backend API',
        'version': '1.0.0',
        'service': 'SuraSmart - Missing Persons Search Platform',
        'documentation': 'Available endpoints:',
        'endpoints': {
            'health': '/api/health/',
            'auth': '/api/auth/',
            'facial-recognition': '/api/facial-recognition/',
            'notifications': '/api/notifications/',
            'database-integration': '/api/database/',
            'admin': '/admin/',
        }
    })


@api_view(['GET'])
@permission_classes([AllowAny])
def health_check(request):
    """
    Health check endpoint for monitoring.
    Returns status of database, cache, and Celery.
    """
    health_status = {
        'status': 'healthy',
        'services': {}
    }
    
    # Database check
    try:
        with connection.cursor() as cursor:
            cursor.execute('SELECT 1')
        health_status['services']['database'] = 'ok'
    except Exception as e:
        health_status['services']['database'] = f'error: {str(e)}'
        health_status['status'] = 'unhealthy'
    
    # Redis/Cache check
    try:
        cache.set('health_check', 'ok', 10)
        cache.get('health_check')
        health_status['services']['cache'] = 'ok'
    except Exception as e:
        health_status['services']['cache'] = f'error: {str(e)}'
        health_status['status'] = 'degraded'
    
    # Celery check
    try:
        celery_app.control.inspect().active()
        health_status['services']['celery'] = 'ok'
    except Exception as e:
        health_status['services']['celery'] = f'error: {str(e)}'
        health_status['status'] = 'degraded'
    
    status_code = 200 if health_status['status'] == 'healthy' else 503
    return Response(health_status, status=status_code)


@api_view(['GET'])
@permission_classes([AllowAny])
def status(request):
    """API status endpoint."""
    return Response({
        'version': '1.0.0',
        'environment': 'production',
        'service': 'SuraSmart Backend - Phase 1',
    })
