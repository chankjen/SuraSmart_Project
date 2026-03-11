# integrations/police_db.py
"""
Sura Smart Police Database Integration
TRD Section 4.1.1.c: Police Custody and Missing Persons Databases
TRD Section 4.2.3: Permission-based Access
"""

import os
import logging
import requests
from typing import Dict, List, Optional
from datetime import datetime
from .data_normalizer import DataNormalizer

logger = logging.getLogger(__name__)


class PoliceDatabase:
    """
    Integration with police custody and missing persons databases.
    
    TRD 4.1.1.c: Police custody and missing persons databases
    TRD 4.2.3: Different access levels for families vs. authorized officials
    TRD 6.1.1: Database response time < 5 seconds
    """
    
    def __init__(self,
                 api_endpoint: str = None,
                 api_key: str = None,
                 timeout: int = 5):
        """
        Initialize police database connection.
        
        Args:
            api_endpoint: Police database API endpoint
            api_key: API authentication key
            timeout: Request timeout (TRD 6.1.1)
        """
        self.api_endpoint = api_endpoint or os.environ.get('POLICE_DB_ENDPOINT')
        self.api_key = api_key or os.environ.get('POLICE_DB_API_KEY')
        self.timeout = timeout
        self.normalizer = DataNormalizer()
        
        # Access level tracking
        self.access_level = 'standard'  # standard, law_enforcement, admin
        
        # Performance tracking
        self.query_count = 0
        self.total_response_time = 0.0
        
        logger.info(f"✅ Police Database initialized: {self.api_endpoint}")
    
    def set_access_level(self, level: str):
        """
        Set access level based on user role.
        
        TRD 4.2.3: Permission-based access
        PRD 4.2.3: Different access levels
        """
        valid_levels = ['standard', 'law_enforcement', 'admin']
        if level in valid_levels:
            self.access_level = level
            logger.info(f"Access level set to: {level}")
        else:
            logger.warning(f"Invalid access level: {level}")
    
    def search_missing_persons(self,
                               photo_embedding: List[float],
                               user_role: str = 'standard') -> List[Dict]:
        """
        Search missing persons database.
        
        TRD 4.1.1.c: Missing persons databases
        TRD 4.2.3: Role-based access control
        """
        import time
        start_time = time.time()
        
        try:
            headers = {
                'Authorization': f'Bearer {self.api_key}',
                'Content-Type': 'application/json',
                'X-Access-Level': self.access_level,
                'X-User-Role': user_role
            }
            
            payload = {
                'embedding': photo_embedding,
                'access_level': self.access_level
            }
            
            response = requests.post(
                f"{self.api_endpoint}/api/v1/missing-persons/search",
                json=payload,
                headers=headers,
                timeout=self.timeout
            )
            
            response_time = time.time() - start_time
            self.query_count += 1
            self.total_response_time += response_time
            
            if response.status_code == 200:
                results = response.json().get('results', [])
                
                # TRD 4.2.3: Filter results based on access level
                filtered_results = self._filter_by_access_level(results)
                
                normalized_results = self.normalizer.normalize_batch(
                    filtered_results,
                    source_type='police'
                )
                
                logger.info(f"🔍 Police DB search: {len(normalized_results)} matches")
                return normalized_results
            else:
                logger.error(f"Police DB error: {response.status_code}")
                return []
                
        except Exception as e:
            logger.error(f"Police DB search failed: {str(e)}")
            return []
    
    def search_custody_records(self,
                               photo_embedding: List[float],
                               user_role: str = 'law_enforcement') -> List[Dict]:
        """
        Search police custody records.
        
        TRD 4.1.1.c: Police custody databases
        TRD 4.2.3: Restricted to law enforcement
        """
        # TRD 4.2.3: Only law enforcement can access custody records
        if user_role not in ['law_enforcement', 'admin']:
            logger.warning(f"Unauthorized access attempt to custody records: {user_role}")
            return []
        
        import time
        start_time = time.time()
        
        try:
            headers = {
                'Authorization': f'Bearer {self.api_key}',
                'Content-Type': 'application/json',
                'X-Access-Level': 'law_enforcement'
            }
            
            payload = {'embedding': photo_embedding}
            
            response = requests.post(
                f"{self.api_endpoint}/api/v1/custody/search",
                json=payload,
                headers=headers,
                timeout=self.timeout
            )
            
            response_time = time.time() - start_time
            self.query_count += 1
            self.total_response_time += response_time
            
            if response.status_code == 200:
                results = response.json().get('results', [])
                normalized_results = self.normalizer.normalize_batch(
                    results,
                    source_type='police_custody'
                )
                
                logger.info(f"🔍 Custody search: {len(normalized_results)} matches")
                return normalized_results
            else:
                logger.error(f"Custody DB error: {response.status_code}")
                return []
                
        except Exception as e:
            logger.error(f"Custody DB search failed: {str(e)}")
            return []
    
    def _filter_by_access_level(self, results: List[Dict]) -> List[Dict]:
        """
        Filter results based on access level.
        
        TRD 4.2.3: Permission-based data access
        TRD 5.2.1: Data minimization
        """
        if self.access_level == 'admin':
            return results
        
        elif self.access_level == 'law_enforcement':
            # Law enforcement sees most fields
            return results
        
        else:  # standard (family)
            # Families see limited information
            filtered = []
            for result in results:
                filtered_result = {
                    'case_number': result.get('case_number'),
                    'status': result.get('status'),
                    'last_seen_date': result.get('last_seen_date'),
                    'last_seen_location': result.get('last_seen_location'),
                    # Hide sensitive fields
                    'photo_url': result.get('photo_url'),  # Blurred or limited
                    'confidence': result.get('confidence')
                }
                filtered.append(filtered_result)
            return filtered
    
    def get_statistics(self) -> Dict:
        """Get database query statistics"""
        avg_response_time = (
            self.total_response_time / self.query_count
            if self.query_count > 0 else 0
        )
        
        return {
            'database_type': 'police',
            'access_level': self.access_level,
            'total_queries': self.query_count,
            'avg_response_time_seconds': avg_response_time,
            'trd_6.1.1_compliance': avg_response_time < 5.0,
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