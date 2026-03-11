from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta
from core.models import AuditLog
from django.conf import settings

class Command(BaseCommand):
    help = 'Purges audit logs older than retention period (TRD §5.2)'

    def handle(self, *args, **options):
        retention_days = settings.AUDIT_LOG_RETENTION_DAYS
        cutoff_date = timezone.now() - timedelta(days=retention_days)
        
        old_logs = AuditLog.objects.filter(timestamp__lt=cutoff_date)
        count = old_logs.count()
        
        # Keep blockchain hash reference even if log is deleted (Optional based on policy)
        # For this implementation, we delete the log entry but ensure hash was recorded externally
        old_logs.delete()
        
        self.stdout.write(self.style.SUCCESS(f'Successfully purged {count} audit logs older than {retention_days} days.'))