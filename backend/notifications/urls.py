# notifications/urls.py
"""
Sura Smart Notifications URL Configuration
"""

from django.urls import path
from . import views

app_name = 'notifications'

urlpatterns = [
    path('test/', views.test_notifications, name='test'),
    path('alert/send/', views.send_alert, name='send_alert'),
    path('alert/bulk/', views.send_bulk_alert, name='send_bulk_alert'),
    path('stats/', views.get_statistics, name='statistics'),
    path('device/register/', views.register_device, name='register_device'),
    path('device/unregister/', views.unregister_device, name='unregister_device'),
]