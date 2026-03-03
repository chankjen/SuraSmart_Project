#!/usr/bin/env python3
# scripts/check_validation_results.py
# Sura Smart - TRD Section 6.2: AI Performance Validation
# TRD Section 7.2: CI/CD Pipeline Gates

import argparse
import json
import sys
from pathlib import Path
from typing import Dict, Any


class ValidationResultChecker:
    """
    Validates model performance against TRD requirements.
    
    TRD 6.2.1: Face matching accuracy > 98%
    TRD 6.2.2: False positive rate < 0.5%
    TRD 6.2.3: False negative rate < 2%
    TRD 3.1.4: Bias variance < 2%
    """
    
    def __init__(self, accuracy_threshold: float = 0.98, 
                 bias_threshold: float = 0.02,
                 fp_threshold: float = 0.005,
                 fn_threshold: float = 0.02):
        self.accuracy_threshold = accuracy_threshold
        self.bias_threshold = bias_threshold
        self.fp_threshold = fp_threshold
        self.fn_threshold = fn_threshold
    
    def load_results(self, report_path: str) -> Dict[str, Any]:
        """Load validation report from JSON file"""
        with open(report_path, 'r') as f:
            return json.load(f)
    
    def check_accuracy(self, results: Dict) -> bool:
        """TRD 6.2.1: Check model accuracy"""
        accuracy = results.get('accuracy', {}).get('overall_accuracy', 0)
        passed = accuracy >= self.accuracy_threshold
        
        print(f"📊 Accuracy: {accuracy:.2%} (threshold: {self.accuracy_threshold:.2%})")
        print(f"   Status: {'✅ PASS' if passed else '❌ FAIL'}")
        
        return passed
    
    def check_bias(self, results: Dict) -> bool:
        """TRD 3.1.4: Check bias variance"""
        bias_variance = results.get('bias_audit', {}).get('max_variance', 1.0)
        passed = bias_variance <= self.bias_threshold
        
        print(f"⚖️  Bias Variance: {bias_variance:.2%} (threshold: {self.bias_threshold:.2%})")
        print(f"   Status: {'✅ PASS' if passed else '❌ FAIL'}")
        
        return passed
    
    def check_error_rates(self, results: Dict) -> bool:
        """TRD 6.2.2 & 6.2.3: Check false positive/negative rates"""
        fp_rate = results.get('error_rates', {}).get('false_positive_rate', 1.0)
        fn_rate = results.get('error_rates', {}).get('false_negative_rate', 1.0)
        
        fp_passed = fp_rate <= self.fp_threshold
        fn_passed = fn_rate <= self.fn_threshold
        
        print(f"🎯 False Positive Rate: {fp_rate:.2%} (threshold: {self.fp_threshold:.2%})")
        print(f"   Status: {'✅ PASS' if fp_passed else '❌ FAIL'}")
        
        print(f"🎯 False Negative Rate: {fn_rate:.2%} (threshold: {self.fn_threshold:.2%})")
        print(f"   Status: {'✅ PASS' if fn_passed else '❌ FAIL'}")
        
        return fp_passed and fn_passed
    
    def check_all(self, report_path: str) -> bool:
        """Run all validation checks"""
        print("=" * 60)
        print("SURA SMART - MODEL VALIDATION RESULTS")
        print("TRD Section 6.2: AI Performance Requirements")
        print("=" * 60)
        
        results = self.load_results(report_path)
        
        accuracy_passed = self.check_accuracy(results)
        bias_passed = self.check_bias(results)
        error_rates_passed = self.check_error_rates(results)
        
        overall_passed = accuracy_passed and bias_passed and error_rates_passed
        
        print("=" * 60)
        if overall_passed:
            print("✅ ALL VALIDATION CHECKS PASSED")
            print("   Model meets TRD 6.2 requirements")
        else:
            print("❌ VALIDATION CHECKS FAILED")
            print("   Model does NOT meet TRD 6.2 requirements")
            print("   Deployment blocked until issues resolved")
        print("=" * 60)
        
        return overall_passed


def main():
    parser = argparse.ArgumentParser(description='Check Model Validation Results')
    parser.add_argument('--report-path', required=True, help='Path to validation report JSON')
    parser.add_argument('--accuracy-threshold', type=float, default=0.98, 
                        help='Accuracy threshold (TRD 6.2.1)')
    parser.add_argument('--bias-threshold', type=float, default=0.02, 
                        help='Bias variance threshold (TRD 3.1.4)')
    parser.add_argument('--fp-threshold', type=float, default=0.005, 
                        help='False positive threshold (TRD 6.2.2)')
    parser.add_argument('--fn-threshold', type=float, default=0.02, 
                        help='False negative threshold (TRD 6.2.3)')
    
    args = parser.parse_args()
    
    checker = ValidationResultChecker(
        accuracy_threshold=args.accuracy_threshold,
        bias_threshold=args.bias_threshold,
        fp_threshold=args.fp_threshold,
        fn_threshold=args.fn_threshold
    )
    
    passed = checker.check_all(args.report_path)
    
    # Exit with error code if validation failed (blocks CI/CD pipeline)
    sys.exit(0 if passed else 1)


if __name__ == '__main__':
    main()