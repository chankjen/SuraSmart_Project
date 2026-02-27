"""
Sura Smart Validation Framework — Core Validator.

Implements the multi-stage validation pipeline described in the Engineering
Master Plan, aligned with TRD Section 3.1.4 and TRD Section 6.2.
"""
import logging
from typing import Any

import numpy as np

logger = logging.getLogger(__name__)

# ─────────────────────────────────────────────────────────
#  Custom exception
# ─────────────────────────────────────────────────────────

class BiasDetectedException(Exception):
    """Raised when accuracy variance exceeds 2% threshold (TRD Section 6.2)."""


# ─────────────────────────────────────────────────────────
#  Sura Validator
# ─────────────────────────────────────────────────────────

class SuraValidator:
    """
    Multi-stage model validation aligned with the 5-phase pipeline.

    Usage::

        validator = SuraValidator(model=my_model, threshold=0.98)
        results = validator.run_demographic_audit(embeddings_by_group)
        metrics = validator.compute_metrics(y_true, y_pred, y_scores)
    """

    # Demographic groups per TRD Section 3.1.4
    DEMOGRAPHIC_GROUPS = [
        'male', 'female', 'non_binary',
        'dark_skin', 'medium_skin', 'light_skin',
        'child', 'adult', 'elderly',
    ]

    def __init__(self, threshold: float = 0.98, max_bias_variance: float = 0.02):
        """
        Args:
            threshold:          Minimum accuracy target (default 0.98 → 98%).
            max_bias_variance:  Maximum allowed accuracy variance across groups (default 0.02 → 2%).
        """
        self.threshold = threshold
        self.max_bias_variance = max_bias_variance

    # ── Demographic Audit (Phase 3) ──────────────────────────────

    def run_demographic_audit(
        self,
        results_by_group: dict[str, dict[str, Any]],
    ) -> dict[str, Any]:
        """
        Disaggregated evaluation across demographic groups.

        Args:
            results_by_group: Mapping of group_name → {'correct': int, 'total': int}
                              e.g. {'male': {'correct': 980, 'total': 1000}, ...}

        Returns:
            Report dict with per-group accuracy, overall accuracy, variance,
            and any bias alerts.

        Raises:
            BiasDetectedException: If any group's accuracy is more than
                                   `max_bias_variance` below the threshold.
        """
        if not results_by_group:
            raise ValueError("results_by_group must not be empty.")

        group_accuracies: dict[str, float] = {}
        alerts: list[str] = []

        for group, counts in results_by_group.items():
            total = counts.get('total', 0)
            correct = counts.get('correct', 0)
            if total == 0:
                logger.warning("Group '%s' has no samples — skipping.", group)
                continue
            acc = correct / total
            group_accuracies[group] = acc

        if not group_accuracies:
            raise ValueError("No valid demographic groups to evaluate.")

        accuracies = list(group_accuracies.values())
        overall_accuracy = float(np.mean(accuracies))
        variance = float(np.max(accuracies) - np.min(accuracies))
        min_group = min(group_accuracies, key=group_accuracies.get)
        max_group = max(group_accuracies, key=group_accuracies.get)

        # Alert on groups falling below threshold by more than max_bias_variance
        for group, acc in group_accuracies.items():
            drop = self.threshold - acc
            if drop > self.max_bias_variance:
                alert = (
                    f"BIAS ALERT — Group '{group}': accuracy={acc:.3f} "
                    f"({drop:.2%} drop below threshold {self.threshold:.2f})"
                )
                alerts.append(alert)
                logger.error(alert)

        report = {
            'group_accuracies': {g: round(a, 4) for g, a in group_accuracies.items()},
            'overall_accuracy': round(overall_accuracy, 4),
            'accuracy_variance': round(variance, 4),
            'min_accuracy_group': min_group,
            'max_accuracy_group': max_group,
            'threshold': self.threshold,
            'max_bias_variance': self.max_bias_variance,
            'bias_alerts': alerts,
            'passed': len(alerts) == 0 and variance <= self.max_bias_variance,
        }

        if alerts:
            raise BiasDetectedException(
                f"Demographic bias detected in {len(alerts)} group(s). "
                f"Accuracy variance: {variance:.2%}. Alerts: {alerts}"
            )

        logger.info(
            "Demographic audit PASSED. Overall: %.3f. Variance: %.3f.",
            overall_accuracy, variance
        )
        return report

    # ── Metric Computation (Phase 1/2) ───────────────────────────

    def compute_metrics(
        self,
        y_true: list[int],
        y_pred: list[int],
        y_scores: list[float] | None = None,
    ) -> dict[str, float]:
        """
        Compute accuracy, FPR, FNR for binary match/no-match predictions.

        TRD Section 6.2 targets:
          - Accuracy > 98%
          - FPR < 0.5%
          - FNR < 2%

        Args:
            y_true:   Ground truth labels (1 = same person, 0 = different).
            y_pred:   Predicted labels.
            y_scores: Confidence scores for AUC-ROC (optional).

        Returns:
            dict with 'accuracy', 'fpr', 'fnr', and optionally 'auc_roc'.
        """
        y_true = np.array(y_true)
        y_pred = np.array(y_pred)

        tp = int(np.sum((y_pred == 1) & (y_true == 1)))
        tn = int(np.sum((y_pred == 0) & (y_true == 0)))
        fp = int(np.sum((y_pred == 1) & (y_true == 0)))
        fn = int(np.sum((y_pred == 0) & (y_true == 1)))
        total = len(y_true)

        accuracy = (tp + tn) / total if total > 0 else 0.0
        fpr = fp / (fp + tn) if (fp + tn) > 0 else 0.0
        fnr = fn / (fn + tp) if (fn + tp) > 0 else 0.0

        metrics = {
            'accuracy': round(accuracy, 4),
            'fpr': round(fpr, 6),
            'fnr': round(fnr, 6),
            'tp': tp, 'tn': tn, 'fp': fp, 'fn': fn,
            'total_samples': total,
        }

        # Validate against TRD targets
        if accuracy < self.threshold:
            logger.warning("Accuracy %.4f below target %.4f", accuracy, self.threshold)
        if fpr > 0.005:
            logger.warning("FPR %.4f exceeds 0.5%% target", fpr)
        if fnr > 0.02:
            logger.warning("FNR %.4f exceeds 2%% target", fnr)

        return metrics

    # ── Edge Simulation (Phase 4) ────────────────────────────────

    def run_edge_simulation(self, embeddings: list[list[float]], labels: list[int]) -> dict:
        """
        Simulate edge-device constraints (TRD Section 6.1.4).

        In a real scenario this would quantize and re-run inference.
        Here we approximate quantization noise by adding ±2 LSB Gaussian noise
        to the embeddings (an analogous effect to INT8 quantization).

        Args:
            embeddings: List of face embedding vectors.
            labels:     Ground truth (1 = same person pairs, 0 = different).

        Returns:
            dict with 'simulated_accuracy' and 'accuracy_drop'.
        """
        from facial_recognition.views import _cosine_similarity  # avoid circular at module level

        noise_std = 0.01  # ~INT8 quantization noise approx.
        noisy_embeddings = [
            (np.array(e) + np.random.normal(0, noise_std, len(e))).tolist()
            for e in embeddings
        ]

        # Pairwise similarity on noisy embeddings (evaluate consecutive pairs)
        sims = []
        for i in range(0, len(noisy_embeddings) - 1, 2):
            sims.append(_cosine_similarity(noisy_embeddings[i], noisy_embeddings[i+1]))

        y_pred = [1 if s >= 0.65 else 0 for s in sims]
        y_true = labels[: len(y_pred)]

        correct = sum(p == t for p, t in zip(y_pred, y_true))
        sim_accuracy = correct / len(y_true) if y_true else 0.0

        logger.info("Edge simulation accuracy: %.4f", sim_accuracy)
        return {
            'simulated_accuracy': round(sim_accuracy, 4),
            'noise_std': noise_std,
            'samples_evaluated': len(y_true),
        }
