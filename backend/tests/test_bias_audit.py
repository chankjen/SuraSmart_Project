"""
Bias Audit Tests — Phase 3 of the Validation Framework.

Tests the SuraValidator and BiasAuditor classes.
Aligned with PRD Section 8 (Gender Sensitivity) and TRD Section 3.1.4.
No external datasets required — uses synthetic prediction data.
"""
import pytest
from sura_smart.validation.core import SuraValidator, BiasDetectedException
from sura_smart.bias_audit.auditor import BiasAuditor


# ──────────────────────────────────────────────────────────
#  SuraValidator Tests
# ──────────────────────────────────────────────────────────

class TestSuraValidator:
    """Tests for the multi-stage validation framework validator."""

    def setup_method(self):
        self.validator = SuraValidator(threshold=0.98, max_bias_variance=0.02)

    def test_audit_passes_when_all_groups_above_threshold(self):
        results = {
            'male':   {'correct': 990, 'total': 1000},
            'female': {'correct': 985, 'total': 1000},
            'non_binary': {'correct': 980, 'total': 1000},
        }
        report = self.validator.run_demographic_audit(results)
        assert report['passed'] is True
        assert len(report['bias_alerts']) == 0

    def test_audit_raises_when_group_drops_more_than_2pct(self):
        """A group at 94% with threshold 0.98 (drop=4%) must raise BiasDetectedException."""
        results = {
            'male':   {'correct': 990, 'total': 1000},  # 99%
            'female': {'correct': 940, 'total': 1000},  # 94% — 4% below threshold → alert
        }
        with pytest.raises(BiasDetectedException, match='female'):
            self.validator.run_demographic_audit(results)

    def test_audit_variance_check(self):
        """If any group drops > 2% below threshold, BiasDetectedException is raised."""
        results = {
            'male':       {'correct': 999, 'total': 1000},  # 99.9%
            'dark_skin':  {'correct': 940, 'total': 1000},  # 94.0% — 4% below threshold → alert
        }
        with pytest.raises(BiasDetectedException):
            self.validator.run_demographic_audit(results)

    def test_empty_input_raises_value_error(self):
        with pytest.raises(ValueError, match='must not be empty'):
            self.validator.run_demographic_audit({})

    def test_group_with_zero_total_skipped(self):
        results = {
            'male':   {'correct': 980, 'total': 1000},
            'female': {'correct': 0, 'total': 0},   # will be skipped
        }
        # Should not raise since only 'male' is evaluated
        report = self.validator.run_demographic_audit(results)
        assert 'female' not in report['group_accuracies']

    def test_compute_metrics_trd_targets(self):
        """Verify accuracy/FPR/FNR computation against TRD Section 6.2 targets."""
        # Perfect classifier
        y_true = [1, 1, 0, 0] * 250  # 1000 samples
        y_pred = [1, 1, 0, 0] * 250
        metrics = self.validator.compute_metrics(y_true, y_pred)
        assert metrics['accuracy'] == pytest.approx(1.0)
        assert metrics['fpr'] == pytest.approx(0.0)
        assert metrics['fnr'] == pytest.approx(0.0)

    def test_compute_metrics_with_false_positives(self):
        """FPR should be computed correctly."""
        # 10 true negatives, 5 false positives
        y_true = [0] * 15 + [1] * 10
        y_pred = [1] * 5 + [0] * 10 + [1] * 10
        metrics = self.validator.compute_metrics(y_true, y_pred)
        assert metrics['fp'] == 5
        assert metrics['fpr'] == pytest.approx(5 / 15, rel=1e-3)

    def test_compute_metrics_false_negative_rate(self):
        # 10 true positives, 2 false negatives
        y_true = [1] * 12 + [0] * 10
        y_pred = [0] * 2 + [1] * 10 + [0] * 10
        metrics = self.validator.compute_metrics(y_true, y_pred)
        assert metrics['fn'] == 2
        assert metrics['fnr'] == pytest.approx(2 / 12, rel=1e-3)


# ──────────────────────────────────────────────────────────
#  BiasAuditor Tests
# ──────────────────────────────────────────────────────────

def _make_predictions(groups_data: dict) -> list[dict]:
    """
    Generate synthetic prediction records.

    groups_data: {group_name: (total_samples, num_correct, num_positive)}
    - total_samples: Total number of prediction records for this group
    - num_correct:   Number of predictions that are correct (y_pred == y_true)
    - num_positive:  Number of true positive samples (y_true == 1)

    Incorrect predictions are set as False Negatives (y_true=1, y_pred=0).
    """
    preds = []
    for group, (total, num_correct, num_positive) in groups_data.items():
        num_negative = total - num_positive
        num_incorrect = total - num_correct

        gender = group if group in BiasAuditor.GENDER_GROUPS else 'male'
        skin = group if group in BiasAuditor.SKIN_GROUPS else 'fitzpatrick_iii'
        age = group if group in BiasAuditor.AGE_GROUPS else 'adult'

        # Correct positive predictions (true positives)
        correct_pos = num_positive - num_incorrect  # some positives predicted wrong
        correct_pos = max(0, correct_pos)
        for _ in range(correct_pos):
            preds.append({'y_true': 1, 'y_pred': 1, 'confidence': 0.97,
                          'gender': gender, 'skin_type': skin, 'age_group': age})

        # Incorrect: False negatives (y_true=1, y_pred=0)
        for _ in range(num_incorrect):
            preds.append({'y_true': 1, 'y_pred': 0, 'confidence': 0.45,
                          'gender': gender, 'skin_type': skin, 'age_group': age})

        # Correct negative predictions (true negatives)
        for _ in range(num_negative):
            preds.append({'y_true': 0, 'y_pred': 0, 'confidence': 0.20,
                          'gender': gender, 'skin_type': skin, 'age_group': age})

    return preds


class TestBiasAuditor:
    """Tests for the BiasAuditor disaggregated evaluation engine."""

    def setup_method(self):
        self.auditor = BiasAuditor(target_fpr=0.005)

    def test_audit_passes_for_balanced_groups(self):
        preds = _make_predictions({
            'male':       (1000, 990, 500),
            'female':     (1000, 988, 500),
            'non_binary': (1000, 985, 500),
        })
        report = self.auditor.disaggregated_evaluation(preds)
        assert report['audit_passed'] is True
        assert len(report['bias_summary']['variance_alerts']) == 0

    def test_audit_flags_variance_across_groups(self):
        """Groups with a large accuracy gap (>2%) should produce variance alerts."""
        preds = _make_predictions({
            'male':   (1000, 990, 500),  # ~99% accuracy — high performance
            'female': (1000, 700, 500),  # ~85% accuracy — very low → large variance
        })
        report = self.auditor.disaggregated_evaluation(preds)
        assert report['audit_passed'] is False
        assert len(report['bias_summary']['variance_alerts']) > 0

    def test_empty_predictions_raises(self):
        with pytest.raises(ValueError, match='No predictions'):
            self.auditor.disaggregated_evaluation([])

    def test_report_contains_all_axes(self):
        preds = _make_predictions({'male': (100, 95, 50)})
        report = self.auditor.disaggregated_evaluation(preds)
        assert 'by_gender' in report
        assert 'by_skin_type' in report
        assert 'by_age_group' in report
        assert 'global_metrics' in report

    def test_group_metrics_structure(self):
        preds = _make_predictions({'male': (200, 190, 100)})
        report = self.auditor.disaggregated_evaluation(preds)
        gender_metrics = report['by_gender'].get('male', {})
        assert 'accuracy' in gender_metrics
        assert 'fpr' in gender_metrics
        assert 'tpr' in gender_metrics
        assert 'fnr' in gender_metrics

    def test_threshold_tuning_returns_per_group_thresholds(self):
        """tune_thresholds should return a threshold for each group."""
        preds = _make_predictions({
            'male': (500, 480, 250),
            'female': (500, 470, 250),
        })
        thresholds = self.auditor.tune_thresholds(preds, axis='gender')
        assert 'male' in thresholds
        assert 'female' in thresholds
        # All thresholds should be in [0.50, 1.00]
        for group, thresh in thresholds.items():
            assert 0.50 <= thresh <= 1.00, f"Threshold for {group} out of range: {thresh}"
