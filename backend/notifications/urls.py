"""URLs for Notifications app."""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from notifications.views import NotificationViewSet, NotificationPreferenceViewSet

router = DefaultRouter()
router.register(r'notifications', NotificationViewSet, basename='notification')
router.register(r'preferences', NotificationPreferenceViewSet, basename='preferences')

urlpatterns = [
    path('', include(router.urls)),
]
