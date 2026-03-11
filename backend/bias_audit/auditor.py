"""
Bias Audit Module — PRD Section 8 & TRD Section 3.1.4.

Implements the NIST FRVT-inspired disaggregated evaluation methodology for
the Sura Smart humanitarian mission. Supports Fitzpatrick-scale skin-type
groups, gender identities, and age groups.

Audit schedule (TRD Section 10.5):
  - Weekly:    Automated drift detection (via Celery beat task)
  - Quarterly: Full bias audit using this module
  - Annually:  Third-party audit (external auditor)
"""
import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Any

import numpy as np

logger = logging.getLogger(__name__)


# ─────────────────────────────────────────────────────────
#  Bias Auditor
# ─────────────────────────────────────────────────────────

class BiasAuditor:
    """
    Disaggregated evaluation engine for facial recognition bias auditing.

    Supports:
      - Per-group accuracy, FPR, TPR (True Positive Rate) reporting
      - Threshold tuning to equalize FPR across demographic groups
      - Detection of accuracy variance exceeding the 2% threshold

    Usage::

        auditor = BiasAuditor()
        report = auditor.disaggregated_evaluation(predictions)
        auditor.save_report(report, output_dir='reports/')
    """

    # Supported demographic axes
    GENDER_GROUPS = ['male', 'female', 'non_binary']
    SKIN_GROUPS = [
        'fitzpatrick_i', 'fitzpatrick_ii', 'fitzpatrick_iii',
        'fitzpatrick_iv', 'fitzpatrick_v', 'fitzpatrick_vi',
    ]
    AGE_GROUPS = ['child', 'adult', 'elderly']

    MAX_BIAS_VARIANCE = 0.02   # 2% — per TRD Section 6.2
    HITL_LOW = 0.90            # HITL range lower bound
    HITL_HIGH = 0.98           # HITL range upper bound

    def __init__(self, target_fpr: float = 0.005):
        """
        Args:
            target_fpr: Global FPR target (default 0.5% per TRD Section 6.2.2).
        """
        self.target_fpr = target_fpr

    def disaggregated_evaluation(
        self,
        predictions: list[dict[str, Any]],
    ) -> dict[str, Any]:
        """
        Full disaggregated evaluation across all demographic axes.

        Args:
            predictions: List of prediction records. Each record must contain:
                {
                  'y_true':      int  (1 = same person, 0 = different),
                  'y_pred':      int  (model prediction),
                  'confidence':  float (model confidence score),
                  'gender':      str  (e.g. 'male', 'female', 'non_binary'),
                  'skin_type':   str  (Fitzpatrick scale, e.g. 'fitzpatrick_iii'),
                  'age_group':   str  (e.g. 'adult'),
                }

        Returns:
            Full audit report as a nested dict.
        """
        if not predictions:
            raise ValueError("No predictions provided for audit.")

        report = {
            'audit_timestamp': datetime.utcnow().isoformat() + 'Z',
            'total_samples': len(predictions),
            'global_metrics': self._compute_group_metrics(predictions),
            'by_gender': self._evaluate_axis(predictions, 'gender'),
            'by_skin_type': self._evaluate_axis(predictions, 'skin_type'),
            'by_age_group': self._evaluate_axis(predictions, 'age_group'),
            'bias_summary': {},
            'audit_passed': True,
        }

        # Cross-axis variance check
        variance_alerts = []
        for axis in ['by_gender', 'by_skin_type', 'by_age_group']:
            axis_data = report[axis]
            accuracies = [v['accuracy'] for v in axis_data.values() if v.get('total', 0) > 0]
            if len(accuracies) < 2:
                continue
            variance = max(accuracies) - min(accuracies)
            if variance > self.MAX_BIAS_VARIANCE:
                alert = f"Variance on '{axis}': {variance:.2%} exceeds {self.MAX_BIAS_VARIANCE:.0%} limit"
                variance_alerts.append(alert)
                logger.error(alert)

        report['bias_summary'] = {
            'variance_alerts': variance_alerts,
            'max_bias_variance_limit': self.MAX_BIAS_VARIANCE,
            'audit_passed': len(variance_alerts) == 0,
        }
        report['audit_passed'] = len(variance_alerts) == 0

        return report

    def _evaluate_axis(
        self, predictions: list[dict], axis: str
    ) -> dict[str, dict[str, Any]]:
        """Group predictions by `axis` and compute metrics for each group."""
        groups: dict[str, list[dict]] = {}
        for pred in predictions:
            group = pred.get(axis, 'unknown')
            groups.setdefault(group, []).append(pred)

        return {
            group: self._compute_group_metrics(preds)
            for group, preds in groups.items()
        }

    def _compute_group_metrics(self, preds: list[dict]) -> dict[str, Any]:
        """Compute TP, FP, FN, TN, accuracy, FPR, TPR for a prediction list."""
        y_true = np.array([p['y_true'] for p in preds])
        y_pred = np.array([p['y_pred'] for p in preds])

        tp = int(np.sum((y_pred == 1) & (y_true == 1)))
        tn = int(np.sum((y_pred == 0) & (y_true == 0)))
        fp = int(np.sum((y_pred == 1) & (y_true == 0)))
        fn = int(np.sum((y_pred == 0) & (y_true == 1)))
        total = len(y_true)

        accuracy = (tp + tn) / total if total > 0 else 0.0
        fpr = fp / (fp + tn) if (fp + tn) > 0 else 0.0
        tpr = tp / (tp + fn) if (tp + fn) > 0 else 0.0  # recall / sensitivity

        return {
            'total': total,
            'tp': tp, 'tn': tn, 'fp': fp, 'fn': fn,
            'accuracy': round(accuracy, 4),
            'fpr': round(fpr, 6),
            'tpr': round(tpr, 6),
            'fnr': round(1.0 - tpr, 6),
        }

    def tune_thresholds(
        self,
        predictions: list[dict[str, Any]],
        axis: str = 'gender',
        target_fpr: float | None = None,
    ) -> dict[str, float]:
        """
        Compute per-group thresholds to equalize FPR across groups (TRD Section 3.1.4).

        Iterates over candidate thresholds [0.50 → 0.99, step 0.01] and selects
        the highest threshold for each demographic group that keeps FPR ≤ target_fpr.

        Args:
            predictions: Same format as `disaggregated_evaluation`.
            axis:        Demographic axis to tune ('gender', 'skin_type', 'age_group').
            target_fpr:  Target FPR per group (default: self.target_fpr).

        Returns:
            dict mapping group_name → optimal_threshold.
        """
        target_fpr = target_fpr or self.target_fpr
        groups: dict[str, list[dict]] = {}
        for pred in predictions:
            group = pred.get(axis, 'unknown')
            groups.setdefault(group, []).append(pred)

        optimal: dict[str, float] = {}
        thresholds = [round(t, 2) for t in np.arange(0.50, 1.00, 0.01)]

        for group, preds in groups.items():
            y_true = np.array([p['y_true'] for p in preds])
            scores = np.array([p['confidence'] for p in preds])

            best_thresh = 0.50
            for thresh in thresholds:
                y_pred = (scores >= thresh).astype(int)
                fp = int(np.sum((y_pred == 1) & (y_true == 0)))
                tn = int(np.sum((y_pred == 0) & (y_true == 0)))
                fpr = fp / (fp + tn) if (fp + tn) > 0 else 0.0
                if fpr <= target_fpr:
                    best_thresh = thresh  # keep raising threshold

            optimal[group] = best_thresh
            logger.info("Group '%s' optimal threshold: %.2f (FPR ≤ %.3f)", group, best_thresh, target_fpr)

        return optimal

    def save_report(self, report: dict, output_dir: str = 'reports/') -> str:
        """Save audit report as a timestamped JSON file."""
        Path(output_dir).mkdir(parents=True, exist_ok=True)
        ts = datetime.utcnow().strftime('%Y%m%d_%H%M%S')
        path = Path(output_dir) / f'bias_audit_{ts}.json'
        with open(path, 'w') as f:
            json.dump(report, f, indent=2)
        logger.info("Bias audit report saved: %s", path)
        return str(path)
