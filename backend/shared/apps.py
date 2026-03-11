# shared/apps.py
"""
Sura Smart Shared Django App Configuration
"""

from django.apps import AppConfig


class SharedConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'shared'
    verbose_name = 'Sura Smart Shared Utilities'