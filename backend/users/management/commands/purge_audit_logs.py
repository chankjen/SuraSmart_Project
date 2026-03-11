from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta
from users.models import AuditLog

class Command(BaseCommand):
    help = 'Purges audit logs older than 30 days.'

    def handle(self, *args, **options):
        threshold = timezone.now() - timedelta(days=30)
        deleted_count, _ = AuditLog.objects.filter(timestamp__lt=threshold).delete()
        self.stdout.write(self.style.SUCCESS(f'Successfully deleted {deleted_count} old audit logs.'))
