"""
URL configuration for SuraSmart backend.
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/auth/', include('users.urls')),
    path('api/facial-recognition/', include('facial_recognition.urls')),
    path('api/notifications/', include('notifications.urls')),
    path('api/database/', include('database_integration.urls')),
    path('api/health/', include('shared.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
