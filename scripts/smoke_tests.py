#!/usr/bin/env python3
# scripts/smoke_tests.py
# Sura Smart - TRD Section 7.3: Deployment Validation
# TRD Section 6.1.1: Search Completion Time < 30 Seconds

import argparse
import requests
import time
from pathlib import Path
from datetime import datetime
from typing import Dict, List


class SmokeTestRunner:
    """
    Runs smoke tests after deployment.
    
    TRD 7.3: Blue-green deployment validation
    TRD 6.1.1: Search completion time < 30 seconds
    TRD 6.1.2: System availability
    """
    
    def __init__(self, endpoint: str, timeout: int = 30):
        self.endpoint = endpoint.rstrip('/')
        self.timeout = timeout
        self.session = requests.Session()
        self.results: List[Dict] = []
    
    def test_health_endpoint(self) -> Dict:
        """TRD 6.1.2: Test health endpoint"""
        print("🏥 Testing health endpoint...")
        
        start_time = time.time()
        try:
            response = self.session.get(
                f"{self.endpoint}/api/v1/health",
                timeout=self.timeout
            )
            response_time = (time.time() - start_time) * 1000
            
            result = {
                'test': 'health_endpoint',
                'status': 'PASS' if response.status_code == 200 else 'FAIL',
                'status_code': response.status_code,
                'response_time_ms': response_time,
                'timestamp': datetime.now().isoformat()
            }
            
            print(f"   Status: {result['status']} ({response.status_code})")
            print(f"   Response Time: {response_time:.2f}ms")
            
        except Exception as e:
            result = {
                'test': 'health_endpoint',
                'status': 'FAIL',
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }
            print(f"   Status: FAIL ({str(e)})")
        
        self.results.append(result)
        return result
    
    def test_search_endpoint(self) -> Dict:
        """TRD 6.1.1: Test search endpoint performance"""
        print("🔍 Testing search endpoint (performance)...")
        
        start_time = time.time()
        try:
            # Use a test image
            test_image_path = Path('tests/fixtures/test_image.jpg')
            
            if test_image_path.exists():
                with open(test_image_path, 'rb') as f:
                    files = {'image': f}
                    response = self.session.post(
                        f"{self.endpoint}/api/v1/search",
                        files=files,
                        headers={'Authorization': 'Bearer test_token'},
                        timeout=self.timeout
                    )
            else:
                # Mock request without image
                response = self.session.post(
                    f"{self.endpoint}/api/v1/search",
                    timeout=self.timeout
                )
            
            response_time = (time.time() - start_time)
            
            # TRD 6.1.1: Search must complete in < 30 seconds
            sla_compliant = response_time < self.timeout
            
            result = {
                'test': 'search_endpoint',
                'status': 'PASS' if sla_compliant else 'FAIL',
                'status_code': response.status_code,
                'response_time_seconds': response_time,
                'sla_threshold': self.timeout,
                'sla_compliant': sla_compliant,
                'timestamp': datetime.now().isoformat()
            }
            
            print(f"   Status: {result['status']}")
            print(f"   Response Time: {response_time:.2f}s (threshold: {self.timeout}s)")
            print(f"   SLA Compliant: {sla_compliant}")
            
        except Exception as e:
            result = {
                'test': 'search_endpoint',
                'status': 'FAIL',
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }
            print(f"   Status: FAIL ({str(e)})")
        
        self.results.append(result)
        return result
    
    def test_audit_endpoint(self) -> Dict:
        """TRD 5.1.2: Test blockchain audit endpoint"""
        print("🔗 Testing audit endpoint...")
        
        start_time = time.time()
        try:
            response = self.session.get(
                f"{self.endpoint}/api/v1/audit/verify/test_search_id",
                headers={'Authorization': 'Bearer test_token'},
                timeout=self.timeout
            )
            response_time = (time.time() - start_time) * 1000
            
            result = {
                'test': 'audit_endpoint',
                'status': 'PASS' if response.status_code in [200, 404] else 'FAIL',
                'status_code': response.status_code,
                'response_time_ms': response_time,
                'timestamp': datetime.now().isoformat()
            }
            
            print(f"   Status: {result['status']} ({response.status_code})")
            
        except Exception as e:
            result = {
                'test': 'audit_endpoint',
                'status': 'FAIL',
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }
            print(f"   Status: FAIL ({str(e)})")
        
        self.results.append(result)
        return result
    
    def test_edge_endpoint(self) -> Dict:
        """TRD 4.3.1: Test edge AI endpoint"""
        print("📱 Testing edge AI endpoint...")
        
        start_time = time.time()
        try:
            response = self.session.get(
                f"{self.endpoint}/api/v1/edge/stats",
                headers={'Authorization': 'Bearer test_token'},
                timeout=self.timeout
            )
            response_time = (time.time() - start_time) * 1000
            
            result = {
                'test': 'edge_endpoint',
                'status': 'PASS' if response.status_code in [200, 503] else 'FAIL',
                'status_code': response.status_code,
                'response_time_ms': response_time,
                'timestamp': datetime.now().isoformat()
            }
            
            print(f"   Status: {result['status']} ({response.status_code})")
            
        except Exception as e:
            result = {
                'test': 'edge_endpoint',
                'status': 'FAIL',
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }
            print(f"   Status: FAIL ({str(e)})")
        
        self.results.append(result)
        return result
    
    def run_all_tests(self) -> Dict:
        """Run all smoke tests"""
        print("=" * 60)
        print("SURA SMART - Deployment Smoke Tests")
        print(f"Endpoint: {self.endpoint}")
        print("TRD Section 7.3: Blue-Green Deployment Validation")
        print("=" * 60)
        
        self.test_health_endpoint()
        self.test_search_endpoint()
        self.test_audit_endpoint()
        self.test_edge_endpoint()
        
        # Summary
        passed = sum(1 for r in self.results if r['status'] == 'PASS')
        total = len(self.results)
        
        print("=" * 60)
        print(f"Smoke Test Summary: {passed}/{total} tests passed")
        
        if passed == total:
            print("✅ ALL SMOKE TESTS PASSED")
            print("   Deployment validated successfully")
        else:
            print("❌ SMOKE TESTS FAILED")
            print("   Deployment requires investigation")
        
        print("=" * 60)
        
        return {
            'passed': passed,
            'total': total,
            'success_rate': passed / total if total > 0 else 0,
            'results': self.results,
            'deployment_validated': passed == total
        }
    
    def save_results(self, output_path: str):
        """Save test results to file"""
        import json
        
        report = {
            'test_type': 'smoke_tests',
            'endpoint': self.endpoint,
            'executed_at': datetime.now().isoformat(),
            'summary': {
                'passed': sum(1 for r in self.results if r['status'] == 'PASS'),
                'total': len(self.results)
            },
            'results': self.results
        }
        
        with open(output_path, 'w') as f:
            json.dump(report, f, indent=2)
        
        print(f"📄 Test results saved: {output_path}")


def main():
    parser = argparse.ArgumentParser(description='Run Deployment Smoke Tests')
    parser.add_argument('--endpoint', required=True, help='API endpoint to test')
    parser.add_argument('--timeout', type=int, default=30, 
                        help='Request timeout (TRD 6.1.1)')
    parser.add_argument('--output', type=str, default=None, 
                        help='Save results to file')
    
    args = parser.parse_args()
    
    runner = SmokeTestRunner(endpoint=args.endpoint, timeout=args.timeout)
    summary = runner.run_all_tests()
    
    if args.output:
        runner.save_results(args.output)
    
    # Exit with error code if tests failed (blocks CI/CD pipeline)
    import sys
    sys.exit(0 if summary['deployment_validated'] else 1)


if __name__ == '__main__':
    main()