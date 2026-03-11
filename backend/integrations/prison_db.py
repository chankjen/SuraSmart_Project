# integrations/prison_db.py
"""
Sura Smart Prison Database Integration
TRD Section 4.1.1.b: Prison and Detention Facility Records
TRD Section 4.2.3: Permission-based Access
"""

import os
import logging
import requests
from typing import Dict, List, Optional
from datetime import datetime
from .data_normalizer import DataNormalizer

logger = logging.getLogger(__name__)


class PrisonDatabase:
    """
    Integration with prison and detention facility records.
    
    TRD 4.1.1.b: Prison and detention facility records
    TRD 4.2.3: Restricted access for security
    TRD 6.1.1: Database response time < 5 seconds
    """
    
    def __init__(self,
                 api_endpoint: str = None,
                 api_key: str = None,
                 timeout: int = 5):
        """
        Initialize prison database connection.
        
        Args:
            api_endpoint: Prison database API endpoint
            api_key: API authentication key
            timeout: Request timeout (TRD 6.1.1)
        """
        self.api_endpoint = api_endpoint or os.environ.get('PRISON_DB_ENDPOINT')
        self.api_key = api_key or os.environ.get('PRISON_DB_API_KEY')
        self.timeout = timeout
        self.normalizer = DataNormalizer()
        
        # Prison database requires highest access level
        self.required_access_level = 'law_enforcement'
        
        # Performance tracking
        self.query_count = 0
        self.total_response_time = 0.0
        
        logger.info(f"✅ Prison Database initialized: {self.api_endpoint}")
    
    def search_inmates(self,
                       photo_embedding: List[float],
                       user_role: str,
                       facility_id: Optional[str] = None) -> List[Dict]:
        """
        Search prison inmate records.
        
        TRD 4.1.1.b: Prison database integration
        TRD 4.2.3: Law enforcement access only
        """
        # TRD 4.2.3: Strict access control
        if user_role not in ['law_enforcement', 'admin']:
            logger.warning(f"Unauthorized prison DB access: {user_role}")
            return []
        
        import time
        start_time = time.time()
        
        try:
            headers = {
                'Authorization': f'Bearer {self.api_key}',
                'Content-Type': 'application/json',
                'X-Access-Level': 'law_enforcement',
                'X-User-Role': user_role
            }
            
            payload = {
                'embedding': photo_embedding,
                'facility_id': facility_id
            }
            
            response = requests.post(
                f"{self.api_endpoint}/api/v1/inmates/search",
                json=payload,
                headers=headers,
                timeout=self.timeout
            )
            
            response_time = time.time() - start_time
            self.query_count += 1
            self.total_response_time += response_time
            
            # TRD 6.1.1: Log if exceeds SLA
            if response_time > 5.0:
                logger.warning(f"Prison DB query exceeded SLA: {response_time}s")
            
            if response.status_code == 200:
                results = response.json().get('results', [])
                
                # TRD 5.2.1: Apply data minimization for prison records
                filtered_results = self._apply_prison_privacy_filters(results)
                
                normalized_results = self.normalizer.normalize_batch(
                    filtered_results,
                    source_type='prison'
                )
                
                logger.info(f"🔍 Prison search: {len(normalized_results)} matches")
                return normalized_results
            else:
                logger.error(f"Prison DB error: {response.status_code}")
                return []
                
        except Exception as e:
            logger.error(f"Prison DB search failed: {str(e)}")
            return []
    
    def _apply_prison_privacy_filters(self, results: List[Dict]) -> List[Dict]:
        """
        Apply privacy filters for prison records.
        
        TRD 5.2.1: Data minimization
        TRD 8: Privacy compliance
        """
        filtered = []
        
        for result in results:
            # Remove sensitive prison-specific fields
            filtered_result = {
                'case_number': result.get('case_number'),
                'facility_id': result.get('facility_id'),
                'admission_date': result.get('admission_date'),
                'status': result.get('status'),
                'photo_url': result.get('photo_url'),
                # Exclude: cell number, security level, disciplinary records, etc.
            }
            filtered.append(filtered_result)
        
        return filtered
    
    def get_facility_list(self, user_role: str) -> List[Dict]:
        """
        Get list of prison facilities.
        
        TRD 4.2.3: Access control
        """
        if user_role not in ['law_enforcement', 'admin']:
            return []
        
        try:
            headers = {'Authorization': f'Bearer {self.api_key}'}
            
            response = requests.get(
                f"{self.api_endpoint}/api/v1/facilities",
                headers=headers,
                timeout=self.timeout
            )
            
            if response.status_code == 200:
                return response.json().get('facilities', [])
            
            return []
            
        except Exception as e:
            logger.error(f"Failed to get facility list: {str(e)}")
            return []
    
    def get_statistics(self) -> Dict:
        """Get database query statistics"""
        avg_response_time = (
            self.total_response_time / self.query_count
            if self.query_count > 0 else 0
        )
        
        return {
            'database_type': 'prison',
            'total_queries': self.query_count,
            'avg_response_time_seconds': avg_response_time,
            'trd_6.1.1_compliance': avg_response_time < 5.0,
            'access_level_required': self.required_access_level,
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