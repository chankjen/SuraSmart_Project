# scripts/bias_audit.py
"""
Bias Audit Protocol
Aligns with PRD Section 8 & TRD Section 3.1.4
"""

import numpy as np
from sklearn.metrics import accuracy_score, confusion_matrix

class BiasAuditor:
    def __init__(self, model, threshold=0.98):
        self.model = model
        self.threshold = threshold
        
    def run_full_audit(self, test_datasets):
        """
        Comprehensive bias audit per TRD Section 10.5 (Quarterly audits)
        """
        audit_report = {
            'overall_accuracy': None,
            'demographic_breakdown': {},
            'bias_metrics': {},
            'compliance_status': 'PASS/FAIL'
        }
        
        # 1. Overall Accuracy (TRD Section 6.2.1)
        if 'combined' in test_datasets:
            audit_report['overall_accuracy'] = self._calculate_accuracy(test_datasets['combined'])
        else:
            audit_report['overall_accuracy'] = 0.0
        
        # 2. Demographic Breakdown (PRD Section 4.3.2)
        for group in ['male', 'female', 'dark_skin', 'light_skin', 'young', 'elderly']:
            if group in test_datasets:
                acc = self._calculate_accuracy(test_datasets[group])
                audit_report['demographic_breakdown'][group] = {
                    'accuracy': acc,
                    'variance_from_mean': acc - audit_report['overall_accuracy']
                }
        
        # 3. Bias Metrics (TRD Section 3.1.4)
        if audit_report['demographic_breakdown']:
            audit_report['bias_metrics'] = self._calculate_bias_metrics(audit_report['demographic_breakdown'])
        
        # 4. Compliance Check
        if audit_report['demographic_breakdown']:
            max_variance = max(
                abs(m['variance_from_mean']) 
                for m in audit_report['demographic_breakdown'].values()
            )
            audit_report['compliance_status'] = 'PASS' if max_variance <= 0.02 else 'FAIL'
        else:
            audit_report['compliance_status'] = 'SKIPPED'
        
        return audit_report
    
    def _calculate_accuracy(self, dataset):
        """Calculate accuracy for a given dataset"""
        # Placeholder: In real scenario, dataset should be (X, y) or a generator
        # y_true, y_pred = self.model.predict(dataset)
        # return accuracy_score(y_true, y_pred)
        return 0.985 # Mock
    
    def _calculate_bias_metrics(self, demographic_data):
        """
        Calculate standardized bias metrics
        NIST FRVT methodology adaptation
        """
        accuracies = [d['accuracy'] for d in demographic_data.values()]
        
        return {
            'max_variance': max(accuracies) - min(accuracies) if accuracies else 0,
            'mean_accuracy': np.mean(accuracies) if accuracies else 0,
            'std_deviation': np.std(accuracies) if accuracies else 0,
            'min_performing_group': min(demographic_data, key=lambda x: demographic_data[x]['accuracy']) if demographic_data else None
        }
    
    def generate_audit_report(self, audit_results):
        """
        Generate compliance report for TRD Section 10.5 (Annual third-party audits)
        """
        report = f"""
        ═══════════════════════════════════════════════════════
        SURA SMART - BIAS AUDIT REPORT
        ═══════════════════════════════════════════════════════
        
        Overall Accuracy: {audit_results.get('overall_accuracy', 0):.2%}
        Compliance Status: {audit_results.get('compliance_status', 'N/A')}
        
        DEMOGRAPHIC BREAKDOWN:
        """
        
        for group, metrics in audit_results.get('demographic_breakdown', {}).items():
            report += f"\n  {group}: {metrics['accuracy']:.2%} (variance: {metrics['variance_from_mean']:+.2%})"
        
        bias_metrics = audit_results.get('bias_metrics', {})
        report += f"""
        
        BIAS METRICS:
          Max Variance: {bias_metrics.get('max_variance', 0):.2%}
          Min Performing Group: {bias_metrics.get('min_performing_group', 'N/A')}
        
        RECOMMENDATIONS:
        """
        
        if audit_results.get('compliance_status') == 'FAIL':
            report += "\n  ⚠️ Model requires retraining with demographic re-weighting"
            report += "\n  ⚠️ Consider synthetic data augmentation for underrepresented groups"
        elif audit_results.get('compliance_status') == 'PASS':
            report += "\n  ✅ Model meets TRD Section 6.2 bias requirements"
        else:
            report += "\n  ℹ️ Insufficient data for full audit."
        
        return report
