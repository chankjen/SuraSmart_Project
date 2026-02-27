"""
Django Management Command: purge_closed_cases

GDPR Right to be Forgotten — TRD Section 5.2.2.
Deletes biometric image files for resolved cases older than N days.

Usage:
    python manage.py purge_closed_cases
    python manage.py purge_closed_cases --days 90
    python manage.py purge_closed_cases --dry-run
"""
import os
from datetime import timedelta

from django.core.management.base import BaseCommand
from django.utils import timezone

from facial_recognition.models import FacialRecognitionImage, SearchSession, MissingPerson


class Command(BaseCommand):
    help = (
        'Purge biometric image data from resolved cases per GDPR Article 17 '
        '(Right to Erasure) — TRD Section 5.2.2.'
    )

    def add_arguments(self, parser):
        parser.add_argument(
            '--days',
            type=int,
            default=90,
            help='Purge images from cases resolved more than N days ago (default: 90).',
        )
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Preview what would be deleted without actually deleting.',
        )

    def handle(self, *args, **options):
        days = options['days']
        dry_run = options['dry_run']
        cutoff = timezone.now() - timedelta(days=days)

        self.stdout.write(
            self.style.MIGRATE_HEADING(
                f'\n🗑️  GDPR Purge — Cases resolved before {cutoff.date()} ({days}d)\n'
            )
        )

        if dry_run:
            self.stdout.write(self.style.WARNING('  [DRY RUN MODE — no data will be deleted]\n'))

        # ── 1. Purge FacialRecognitionImages from resolved/found cases ────
        resolved_persons = MissingPerson.objects.filter(
            status__in=['found', 'closed'],
            updated_at__lt=cutoff,
        )

        images_to_purge = FacialRecognitionImage.objects.filter(
            missing_person__in=resolved_persons
        )
        image_count = images_to_purge.count()
        self.stdout.write(f'  📸 Facial images to purge: {image_count}')

        if not dry_run:
            for img in images_to_purge:
                # Delete physical file from storage
                if img.image_file and os.path.isfile(img.image_file.path):
                    os.remove(img.image_file.path)
                    self.stdout.write(f'    Deleted file: {img.image_file.path}')
                # Clear embedding and file reference but keep DB record for audit trail
                img.face_embedding = None
                img.image_file.delete(save=False)
                img.status = 'purged'
                img.processing_error = f'Purged per GDPR on {timezone.now().date()}'
                img.save(update_fields=['face_embedding', 'status', 'processing_error'])

        # ── 2. Purge uploaded search images from closed sessions ──────────
        old_sessions = SearchSession.objects.filter(
            is_closed=True,
            closed_at__lt=cutoff,
        )
        session_count = old_sessions.count()
        self.stdout.write(f'  🔍 Search session uploads to purge: {session_count}')

        if not dry_run:
            for session in old_sessions:
                if session.uploaded_image and os.path.isfile(session.uploaded_image.path):
                    os.remove(session.uploaded_image.path)
                session.uploaded_image.delete(save=False)
                session.save(update_fields=['uploaded_image'])

        # ── Summary ───────────────────────────────────────────────────────
        self.stdout.write('\n' + '─' * 55)
        if dry_run:
            self.stdout.write(
                self.style.WARNING(
                    f'  DRY RUN complete. Would purge {image_count} images '
                    f'and {session_count} session uploads.\n'
                )
            )
        else:
            self.stdout.write(
                self.style.SUCCESS(
                    f'  ✅ Purge complete. {image_count} images and '
                    f'{session_count} session uploads removed.\n'
                )
            )
