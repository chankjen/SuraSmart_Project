"""URLs for Users app."""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from users.views import UserViewSet, AuditLogViewSet, PermissionViewSet

router = DefaultRouter()
router.register(r'users', UserViewSet, basename='user')
router.register(r'audit-logs', AuditLogViewSet, basename='audit-log')
router.register(r'permissions', PermissionViewSet, basename='permission')

urlpatterns = [
    path('', include(router.urls)),
    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
]
