# users/apps.py
"""
Sura Smart Users Django App Configuration
TRD Section 4.2: Authentication & Authorization
"""

from django.apps import AppConfig


class UsersConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'users'
    verbose_name = 'Sura Smart User Management'
    
    def ready(self):
        """Initialize user management"""
        # from . import signals  # Import signals
