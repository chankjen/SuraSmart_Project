# notifications/views.py
"""
Sura Smart Notifications API Views
TRD Section 1.1.6: Notification System
"""

from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
import json
from .alert_manager import AlertManager

alert_manager = AlertManager()


@csrf_exempt
@require_http_methods(["POST"])
def test_notifications(request):
    """Test notification system"""
    try:
        data = json.loads(request.body)
        user_id = data.get('user_id')
        
        if not user_id:
            return JsonResponse({'error': 'user_id required'}, status=400)
        
        result = alert_manager.test_alert_system(user_id)
        
        return JsonResponse(result)
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@csrf_exempt
@require_http_methods(["POST"])
def send_alert(request):
    """Send match alert to user"""
    try:
        data = json.loads(request.body)
        user_id = data.get('user_id')
        match_data = data.get('match_data', {})
        priority = data.get('priority', 'high')
        channels = data.get('channels', ['email', 'push'])
        
        if not user_id:
            return JsonResponse({'error': 'user_id required'}, status=400)
        
        result = alert_manager.send_match_alert(
            user_id=user_id,
            match_data=match_data,
            priority=priority,
            channels=channels
        )
        
        return JsonResponse(result)
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@csrf_exempt
@require_http_methods(["POST"])
def send_bulk_alert(request):
    """Send bulk alerts to multiple users"""
    try:
        data = json.loads(request.body)
        user_ids = data.get('user_ids', [])
        match_data = data.get('match_data', {})
        priority = data.get('priority', 'normal')
        
        if not user_ids:
            return JsonResponse({'error': 'user_ids required'}, status=400)
        
        result = alert_manager.send_bulk_alerts(
            user_ids=user_ids,
            match_data=match_data,
            priority=priority
        )
        
        return JsonResponse(result)
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@require_http_methods(["GET"])
def get_statistics(request):
    """Get notification statistics"""
    try:
        stats = alert_manager.get_alert_statistics()
        return JsonResponse(stats)
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@csrf_exempt
@require_http_methods(["POST"])
def register_device(request):
    """Register device for push notifications"""
    try:
        data = json.loads(request.body)
        user_id = data.get('user_id')
        device_token = data.get('device_token')
        device_type = data.get('device_type', 'mobile')
        
        if not all([user_id, device_token]):
            return JsonResponse({'error': 'user_id and device_token required'}, status=400)
        
        from .push_notifications import PushNotificationService
        push_service = PushNotificationService()
        push_service.register_device(user_id, device_token, device_type)
        
        return JsonResponse({'success': True, 'message': 'Device registered'})
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@csrf_exempt
@require_http_methods(["POST"])
def unregister_device(request):
    """Unregister device from push notifications"""
    try:
        data = json.loads(request.body)
        user_id = data.get('user_id')
        device_token = data.get('device_token')
        
        if not all([user_id, device_token]):
            return JsonResponse({'error': 'user_id and device_token required'}, status=400)
        
        from .push_notifications import PushNotificationService
        push_service = PushNotificationService()
        push_service.unregister_device(user_id, device_token)
        
        return JsonResponse({'success': True, 'message': 'Device unregistered'})
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)