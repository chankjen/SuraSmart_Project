from django.apps import AppConfig


class DatabaseIntegrationConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'database_integration'
    verbose_name = 'Database Integration'
