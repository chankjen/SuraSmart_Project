"""URLs for Facial Recognition app."""
from django.urls import path, include
from rest_framework.routers import SimpleRouter
from ai_models.facial_recognition.views import (
    MissingPersonViewSet, FacialRecognitionImageViewSet,
    FacialMatchViewSet, ProcessingQueueViewSet, SearchSessionViewSet, search_facial_recognition,
    OfflineSignatureQueueViewSet
)

router = SimpleRouter()
router.register(r'missing-persons', MissingPersonViewSet, basename='missing-person')
router.register(r'images', FacialRecognitionImageViewSet, basename='facial-image')
router.register(r'matches', FacialMatchViewSet, basename='facial-match')
router.register(r'processing-queue', ProcessingQueueViewSet, basename='processing-queue')
router.register(r'search-sessions', SearchSessionViewSet, basename='search-session')
router.register(r'offline-signatures', OfflineSignatureQueueViewSet, basename='offline-signature')

urlpatterns = [
    path('', include(router.urls)),
    path('search/', search_facial_recognition, name='search-facial-recognition'),
]
