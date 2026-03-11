# notifications/apps.py
"""
Sura Smart Notifications Django App Configuration
"""

from django.apps import AppConfig


class NotificationsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'notifications'
    verbose_name = 'Sura Smart Notifications'
    
    def ready(self):
        """Initialize notification services"""
        from .alert_manager import AlertManager
        self.alert_manager = AlertManager()