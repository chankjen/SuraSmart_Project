# integrations/morgue_db.py
"""
Sura Smart Morgue Database Integration
TRD Section 4.1.1.a: National and Local Morgue Databases
TRD Section 4.1: Database Connections
"""

import os
import logging
import requests
from typing import Dict, List, Optional
from datetime import datetime
from .data_normalizer import DataNormalizer

logger = logging.getLogger(__name__)


class MorgueDatabase:
    """
    Integration with morgue databases.
    
    TRD 4.1.1.a: National and local morgue databases
    TRD 6.1.1: Database response time < 5 seconds
    TRD 5.1: Security requirements
    """
    
    def __init__(self, 
                 api_endpoint: str = None,
                 api_key: str = None,
                 timeout: int = 5):
        """
        Initialize morgue database connection.
        
        Args:
            api_endpoint: Morgue database API endpoint
            api_key: API authentication key
            timeout: Request timeout (TRD 6.1.1: < 5 seconds)
        """
        self.api_endpoint = api_endpoint or os.environ.get('MORGUE_DB_ENDPOINT')
        self.api_key = api_key or os.environ.get('MORGUE_DB_API_KEY')
        self.timeout = timeout  # TRD 6.1.1: < 5 seconds per query
        self.normalizer = DataNormalizer()
        
        # Performance tracking
        self.query_count = 0
        self.total_response_time = 0.0
        
        logger.info(f"✅ Morgue Database initialized: {self.api_endpoint}")
    
    def search_unidentified(self, 
                           photo_embedding: List[float],
                           date_range: Optional[Dict] = None,
                           location: Optional[str] = None) -> List[Dict]:
        """
        Search unidentified persons in morgue database.
        
        TRD 4.1.1.a: Morgue database integration
        TRD 6.1.1: < 5 seconds per external query
        """
        import time
        start_time = time.time()
        
        try:
            headers = {
                'Authorization': f'Bearer {self.api_key}',
                'Content-Type': 'application/json'
            }
            
            payload = {
                'embedding': photo_embedding,
                'date_range': date_range,
                'location': location,
                'record_type': 'unidentified'
            }
            
            response = requests.post(
                f"{self.api_endpoint}/api/v1/search",
                json=payload,
                headers=headers,
                timeout=self.timeout
            )
            
            response_time = time.time() - start_time
            self.query_count += 1
            self.total_response_time += response_time
            
            # TRD 6.1.1: Log if exceeds SLA
            if response_time > 5.0:
                logger.warning(f"Morgue DB query exceeded SLA: {response_time}s")
            
            if response.status_code == 200:
                results = response.json().get('results', [])
                
                # Normalize results
                normalized_results = self.normalizer.normalize_batch(
                    results, 
                    source_type='morgue'
                )
                
                logger.info(f"🔍 Morgue search: {len(normalized_results)} matches")
                return normalized_results
            else:
                logger.error(f"Morgue DB error: {response.status_code}")
                return []
                
        except Exception as e:
            logger.error(f"Morgue DB search failed: {str(e)}")
            return []
    
    def get_record(self, case_number: str) -> Optional[Dict]:
        """
        Get specific morgue record by case number.
        
        TRD 4.1.1.a: Morgue database access
        """
        try:
            headers = {'Authorization': f'Bearer {self.api_key}'}
            
            response = requests.get(
                f"{self.api_endpoint}/api/v1/records/{case_number}",
                headers=headers,
                timeout=self.timeout
            )
            
            if response.status_code == 200:
                record = response.json()
                return self.normalizer.normalize_record(record, source_type='morgue')
            
            return None
            
        except Exception as e:
            logger.error(f"Failed to get morgue record: {str(e)}")
            return None
    
    def get_statistics(self) -> Dict:
        """
        Get database query statistics.
        
        TRD 7.4: Monitoring
        """
        avg_response_time = (
            self.total_response_time / self.query_count 
            if self.query_count > 0 else 0
        )
        
        return {
            'database_type': 'morgue',
            'total_queries': self.query_count,
            'avg_response_time_seconds': avg_response_time,
            'trd_6.1.1_compliance': avg_response_time < 5.0,
            'last_query': datetime.now().isoformat()
        }
    
    def health_check(self) -> bool:
        """
        Check database connection health.
        
        TRD 6.1.2: 99.95% availability monitoring
        """
        try:
            response = requests.get(
                f"{self.api_endpoint}/api/v1/health",
                headers={'Authorization': f'Bearer {self.api_key}'},
                timeout=5
            )
            return response.status_code == 200
        except Exception:
            return False