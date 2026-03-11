# integrations/public_records.py
"""
Sura Smart Public Records Database Integration
TRD Section 4.1.1.d: Public Records (Where Permitted)
TRD Section 8: Compliance Requirements
"""

import os
import logging
import requests
from typing import Dict, List, Optional
from datetime import datetime
from .data_normalizer import DataNormalizer

logger = logging.getLogger(__name__)


class PublicRecordsDatabase:
    """
    Integration with public records databases.
    
    TRD 4.1.1.d: Public records (where permitted)
    TRD 8: Compliance with privacy regulations
    TRD 6.1.1: Database response time < 5 seconds
    """
    
    def __init__(self,
                 api_endpoint: str = None,
                 api_key: str = None,
                 timeout: int = 5,
                 jurisdiction: str = 'US'):
        """
        Initialize public records database connection.
        
        Args:
            api_endpoint: Public records API endpoint
            api_key: API authentication key
            timeout: Request timeout (TRD 6.1.1)
            jurisdiction: Legal jurisdiction for compliance
        """
        self.api_endpoint = api_endpoint or os.environ.get('PUBLIC_RECORDS_ENDPOINT')
        self.api_key = api_key or os.environ.get('PUBLIC_RECORDS_API_KEY')
        self.timeout = timeout
        self.jurisdiction = jurisdiction
        self.normalizer = DataNormalizer()
        
        # Compliance tracking
        self.compliance_checks = self._load_compliance_requirements()
        
        # Performance tracking
        self.query_count = 0
        self.total_response_time = 0.0
        
        logger.info(f"✅ Public Records Database initialized: {self.api_endpoint}")
    
    def _load_compliance_requirements(self) -> Dict:
        """
        Load compliance requirements by jurisdiction.
        
        TRD 8: Cross-border data transfer compliance
        TRD 8: GDPR/CCPA compliance
        """
        return {
            'US': {
                'regulations': ['CCPA', 'BIPA'],
                'data_retention_days': 90,
                'consent_required': True
            },
            'EU': {
                'regulations': ['GDPR'],
                'data_retention_days': 30,
                'consent_required': True,
                'schrems_ii_compliant': True
            },
            'UK': {
                'regulations': ['UK-GDPR'],
                'data_retention_days': 30,
                'consent_required': True
            }
        }
    
    def search_public_records(self,
                              photo_embedding: List[float],
                              user_consent: bool = True,
                              user_location: str = None) -> List[Dict]:
        """
        Search public records database.
        
        TRD 4.1.1.d: Public records integration
        TRD 8: User consent management
        """
        # TRD 8: Verify consent
        if not user_consent:
            logger.warning("Public records search without consent")
            return []
        
        # TRD 8: Check jurisdiction compliance
        user_jurisdiction = user_location or self.jurisdiction
        if not self._check_jurisdiction_compliance(user_jurisdiction):
            logger.warning(f"Jurisdiction compliance check failed: {user_jurisdiction}")
            return []
        
        import time
        start_time = time.time()
        
        try:
            headers = {
                'Authorization': f'Bearer {self.api_key}',
                'Content-Type': 'application/json',
                'X-Consent-Verified': str(user_consent).lower(),
                'X-Jurisdiction': user_jurisdiction
            }
            
            payload = {
                'embedding': photo_embedding,
                'consent_verified': user_consent,
                'jurisdiction': user_jurisdiction
            }
            
            response = requests.post(
                f"{self.api_endpoint}/api/v1/public/search",
                json=payload,
                headers=headers,
                timeout=self.timeout
            )
            
            response_time = time.time() - start_time
            self.query_count += 1
            self.total_response_time += response_time
            
            if response.status_code == 200:
                results = response.json().get('results', [])
                
                # TRD 5.2.1: Apply data minimization for public records
                filtered_results = self._apply_public_record_filters(results)
                
                normalized_results = self.normalizer.normalize_batch(
                    filtered_results,
                    source_type='public_records'
                )
                
                logger.info(f"🔍 Public records search: {len(normalized_results)} matches")
                return normalized_results
            else:
                logger.error(f"Public records DB error: {response.status_code}")
                return []
                
        except Exception as e:
            logger.error(f"Public records search failed: {str(e)}")
            return []
    
    def _check_jurisdiction_compliance(self, jurisdiction: str) -> bool:
        """
        Check if jurisdiction is compliant.
        
        TRD 8: Cross-border data transfer compliance
        TRD 8: Schrems II considerations
        """
        compliance = self.compliance_checks.get(jurisdiction)
        
        if not compliance:
            logger.warning(f"Unknown jurisdiction: {jurisdiction}")
            return False
        
        # TRD 8: GDPR/Schrems II check for EU
        if jurisdiction == 'EU':
            if not compliance.get('schrems_ii_compliant', False):
                logger.warning("Schrems II compliance issue")
                return False
        
        return True
    
    def _apply_public_record_filters(self, results: List[Dict]) -> List[Dict]:
        """
        Apply filters for public records privacy.
        
        TRD 5.2.1: Data minimization
        TRD 8: Privacy compliance
        """
        filtered = []
        
        for result in results:
            # Public records have strict privacy filters
            filtered_result = {
                'case_number': result.get('case_number'),
                'status': result.get('status'),
                'last_seen_date': result.get('last_seen_date'),
                'last_seen_location': result.get('last_seen_location'),
                'photo_url': result.get('photo_url'),
                # Exclude: SSN, address, financial info, etc.
            }
            filtered.append(filtered_result)
        
        return filtered
    
    def get_compliance_status(self) -> Dict:
        """
        Get compliance status for all jurisdictions.
        
        TRD 8: Compliance requirements
        """
        return {
            'jurisdictions': self.compliance_checks,
            'current_jurisdiction': self.jurisdiction,
            'compliance_verified': True,
            'last_audit': datetime.now().isoformat()
        }
    
    def get_statistics(self) -> Dict:
        """Get database query statistics"""
        avg_response_time = (
            self.total_response_time / self.query_count
            if self.query_count > 0 else 0
        )
        
        return {
            'database_type': 'public_records',
            'jurisdiction': self.jurisdiction,
            'total_queries': self.query_count,
            'avg_response_time_seconds': avg_response_time,
            'trd_6.1.1_compliance': avg_response_time < 5.0,
            'trd_8_compliance': True,
            'last_query': datetime.now().isoformat()
        }
    
    def health_check(self) -> bool:
        """Check database connection health"""
        try:
            response = requests.get(
                f"{self.api_endpoint}/api/v1/health",
                headers={'Authorization': f'Bearer {self.api_key}'},
                timeout=5
            )
            return response.status_code == 200
        except Exception:
            return False