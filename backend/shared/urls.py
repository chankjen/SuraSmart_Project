from django.urls import path
from . import views

urlpatterns = [
    path('', views.welcome, name='welcome'),
    path('check/', views.health_check, name='health-check'),
    path('status/', views.status, name='api-status'),
]
