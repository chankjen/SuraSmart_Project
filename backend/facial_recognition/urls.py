"""URLs for Facial Recognition app."""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from facial_recognition.views import (
    MissingPersonViewSet, FacialRecognitionImageViewSet,
    FacialMatchViewSet, ProcessingQueueViewSet, search_facial_recognition
)

router = DefaultRouter()
router.register(r'missing-persons', MissingPersonViewSet, basename='missing-person')
router.register(r'images', FacialRecognitionImageViewSet, basename='facial-image')
router.register(r'matches', FacialMatchViewSet, basename='facial-match')
router.register(r'processing-queue', ProcessingQueueViewSet, basename='processing-queue')

urlpatterns = [
    path('', include(router.urls)),
    path('search/', search_facial_recognition, name='search-facial-recognition'),
]
