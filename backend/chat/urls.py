from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import SecureChannelViewSet, MessageViewSet

router = DefaultRouter()
router.register(r'channels', SecureChannelViewSet, basename='secure-channel')
router.register(r'messages', MessageViewSet, basename='secure-message')

urlpatterns = [
    path('', include(router.urls)),
]
