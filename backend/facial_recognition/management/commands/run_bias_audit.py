"""
Django Management Command: run_bias_audit

Quarterly bias audit runner per TRD Section 10.5.
Evaluates model performance across demographic groups using verified match data.

Usage:
    python manage.py run_bias_audit
    python manage.py run_bias_audit --output-dir reports/quarterly/
    python manage.py run_bias_audit --dry-run
"""
import json
import logging
from pathlib import Path

from django.core.management.base import BaseCommand, CommandError

from facial_recognition.models import FacialMatch
from sura_smart.bias_audit.auditor import BiasAuditor

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = (
        'Run disaggregated bias audit on verified match records. '
        'Implements TRD Section 10.5 quarterly audit schedule.'
    )

    def add_arguments(self, parser):
        parser.add_argument(
            '--output-dir',
            default='reports/bias_audits/',
            help='Directory to save the JSON report (default: reports/bias_audits/)',
        )
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Print report to stdout without saving to disk.',
        )
        parser.add_argument(
            '--min-samples',
            type=int,
            default=10,
            help='Minimum number of matches required to run the audit (default: 10).',
        )

    def handle(self, *args, **options):
        output_dir = options['output_dir']
        dry_run = options['dry_run']
        min_samples = options['min_samples']

        self.stdout.write(self.style.MIGRATE_HEADING('\n📊 Sura Smart Bias Audit — TRD Section 10.5'))
        self.stdout.write('─' * 60)

        # Pull verified and false_positive matches for ground truth
        matches = FacialMatch.objects.select_related(
            'missing_person', 'verified_by'
        ).filter(status__in=['verified', 'false_positive'])

        total = matches.count()
        self.stdout.write(f'  Found {total} evaluated match records.\n')

        if total < min_samples:
            raise CommandError(
                f'Not enough evaluated matches to run bias audit. '
                f'Need at least {min_samples}, found {total}. '
                f'Use --min-samples to lower the threshold.'
            )

        # Build prediction records
        # NOTE: In production, demographic metadata (skin type, age group) would be stored
        # on MissingPerson or sourced from a separate annotation layer.
        # Here we map from available fields as a best effort.
        predictions = []
        for match in matches:
            person = match.missing_person
            gender = person.gender or 'unknown'
            # Map gender model values to audit groups
            gender_map = {'male': 'male', 'female': 'female', 'other': 'non_binary'}
            predictions.append({
                'y_true': 1 if match.status == 'verified' else 0,
                'y_pred': 1 if match.match_confidence >= 0.98 else 0,
                'confidence': match.match_confidence,
                'gender': gender_map.get(gender, 'unknown'),
                # Skin type and age_group require future annotation layer
                'skin_type': 'unknown',
                'age_group': 'adult' if (person.age or 0) >= 18 else 'child',
            })

        auditor = BiasAuditor()
        try:
            report = auditor.disaggregated_evaluation(predictions)
        except ValueError as exc:
            raise CommandError(str(exc)) from exc

        # ── Display summary ──────────────────────────────────────
        self.stdout.write('\n  📈 Global Metrics:')
        gm = report['global_metrics']
        self.stdout.write(f"      Accuracy : {gm['accuracy']:.2%}")
        self.stdout.write(f"      FPR      : {gm['fpr']:.4%}")
        self.stdout.write(f"      FNR      : {gm['fnr']:.4%}")

        self.stdout.write('\n  👤 By Gender:')
        for group, m in report['by_gender'].items():
            self.stdout.write(
                f"      {group:15s} acc={m['accuracy']:.2%}  fpr={m['fpr']:.4%}  tpr={m['tpr']:.4%}"
            )

        alerts = report['bias_summary']['variance_alerts']
        if alerts:
            self.stdout.write(self.style.ERROR('\n  ⚠️  Bias Alerts:'))
            for alert in alerts:
                self.stdout.write(self.style.ERROR(f'      {alert}'))
        else:
            self.stdout.write(self.style.SUCCESS('\n  ✅  No bias variance alerts. Audit PASSED.'))

        # ── Save report ──────────────────────────────────────────
        if not dry_run:
            report_path = auditor.save_report(report, output_dir=output_dir)
            self.stdout.write(self.style.SUCCESS(f'\n  📁 Report saved: {report_path}'))
        else:
            self.stdout.write('\n  [DRY RUN] Report not saved. Full JSON:')
            self.stdout.write(json.dumps(report, indent=2))

        self.stdout.write('\n' + '─' * 60)
        passed = report['audit_passed']
        if not passed:
            raise CommandError('Bias audit FAILED. Review alerts above.')

        self.stdout.write(self.style.SUCCESS('Bias audit completed successfully.\n'))
