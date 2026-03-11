# security/access_logger.py
"""
Sura Smart Access Logger
TRD Section 5.2.4: Access Logging
TRD Section 5.1.2: Blockchain-based Audit Trails
"""

import os
import logging
import hashlib
import json
from typing import Dict, Optional
from datetime import datetime
from pathlib import Path

logger = logging.getLogger(__name__)


class AccessLogger:
    """
    Logs all access to sensitive data and operations.
    
    TRD 5.2.4: Strict access logging with immutable records
    TRD 5.1.2: Blockchain-based audit trails
    TRD 8: Compliance with privacy regulations
    """
    
    def __init__(self, log_dir: str = 'logs/access', blockchain_enabled: bool = True):
        """
        Initialize access logger.
        
        Args:
            log_dir: Directory for access logs
            blockchain_enabled: Enable blockchain audit trail (TRD 5.1.2)
        """
        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(parents=True, exist_ok=True)
        
        self.blockchain_enabled = blockchain_enabled
        self.blockchain_auditor = None
        
        if blockchain_enabled:
            self._init_blockchain_auditor()
        
        # Access tracking
        self.access_count = 0
        self.flagged_access = 0
        
        logger.info(f"✅ Access Logger initialized (blockchain: {blockchain_enabled})")
    
    def _init_blockchain_auditor(self):
        """Initialize blockchain auditor"""
        try:
            from blockchain_audit import BlockchainAuditor
            self.blockchain_auditor = BlockchainAuditor(
                chain_endpoint=os.environ.get('BLOCKCHAIN_ENDPOINT'),
                salt=os.environ.get('AUDIT_SALT')
            )
            logger.info("✅ Blockchain auditor initialized")
        except Exception as e:
            logger.warning(f"Blockchain auditor initialization failed: {str(e)}")
            self.blockchain_enabled = False
    
    def log_access(self,
                   user_id: str,
                   resource: str,
                   action: str,
                   result: str,
                   metadata: Optional[Dict] = None) -> Dict:
        """
        Log access to sensitive resource.
        
        TRD 5.2.4: Immutable access records
        TRD 5.1.2: Blockchain audit trail
        """
        timestamp = datetime.now().isoformat()
        
        access_record = {
            'access_id': self._generate_access_id(),
            'user_id': user_id,
            'resource': resource,
            'action': action,
            'result': result,
            'timestamp': timestamp,
            'ip_address': metadata.get('ip_address') if metadata else None,
            'user_agent': metadata.get('user_agent') if metadata else None,
            'session_id': metadata.get('session_id') if metadata else None
        }
        
        # Create hash for integrity verification
        access_record['hash'] = self._generate_record_hash(access_record)
        
        # Write to log file
        self._write_to_log(access_record)
        
        # TRD 5.1.2: Log to blockchain
        if self.blockchain_enabled and self.blockchain_auditor:
            self._log_to_blockchain(access_record)
        
        # Track access
        self.access_count += 1
        
        # Flag suspicious access
        if self._is_suspicious_access(access_record):
            self.flagged_access += 1
            logger.warning(f"🚩 Suspicious access flagged: {access_record['access_id']}")
        
        return access_record
    
    def _generate_access_id(self) -> str:
        """Generate unique access ID"""
        timestamp = datetime.now().strftime('%Y%m%d%H%M%S%f')
        return f"access_{timestamp}"
    
    def _generate_record_hash(self, record: Dict) -> str:
        """Generate hash for record integrity"""
        # Exclude hash field from hash calculation
        record_copy = record.copy()
        record_copy.pop('hash', None)
        
        record_string = json.dumps(record_copy, sort_keys=True)
        return hashlib.sha256(record_string.encode()).hexdigest()
    
    def _write_to_log(self, record: Dict):
        """Write access record to log file"""
        log_file = self.log_dir / f"access_{datetime.now().strftime('%Y%m%d')}.log"
        
        with open(log_file, 'a') as f:
            f.write(json.dumps(record) + '\n')
    
    def _log_to_blockchain(self, record: Dict):
        """Log access record to blockchain"""
        try:
            if self.blockchain_auditor:
                self.blockchain_auditor.log_search(
                    user_id=record['user_id'],
                    user_role='system',
                    query_type='access_log',
                    database=record['resource'],
                    match_found=(record['result'] == 'success'),
                    search_id=record['access_id']
                )
        except Exception as e:
            logger.error(f"Blockchain logging failed: {str(e)}")
    
    def _is_suspicious_access(self, record: Dict) -> bool:
        """
        Detect suspicious access patterns.
        
        TRD 5.1.4: Security monitoring
        """
        # Flag failed access attempts
        if record['result'] == 'denied':
            return True
        
        # Flag access outside business hours
        hour = datetime.fromisoformat(record['timestamp']).hour
        if hour < 6 or hour > 22:
            return True
        
        # Flag bulk access
        if record['action'] == 'bulk_export':
            return True
        
        return False
    
    def get_access_history(self,
                           user_id: str,
                           start_date: datetime,
                           end_date: datetime) -> list:
        """
        Get access history for user.
        
        TRD 5.2.4: Access audit capability
        TRD 10.5: Annual third-party audits
        """
        history = []
        
        # Read log files in date range
        current_date = start_date
        while current_date <= end_date:
            log_file = self.log_dir / f"access_{current_date.strftime('%Y%m%d')}.log"
            
            if log_file.exists():
                with open(log_file, 'r') as f:
                    for line in f:
                        record = json.loads(line)
                        if record['user_id'] == user_id:
                            history.append(record)
            
            current_date = current_date.replace(day=current_date.day + 1)
        
        return history
    
    def get_statistics(self) -> Dict:
        """Get access logging statistics"""
        return {
            'total_access_logs': self.access_count,
            'flagged_access': self.flagged_access,
            'blockchain_enabled': self.blockchain_enabled,
            'last_access': datetime.now().isoformat(),
            'trd_compliance': {
                '5.2.4_access_logging': True,
                '5.1.2_blockchain_audit': self.blockchain_enabled
            }
        }
    
    def verify_log_integrity(self, log_date: str) -> bool:
        """
        Verify integrity of access logs.
        
        TRD 5.1.2: Immutable audit trails
        """
        log_file = self.log_dir / f"access_{log_date}.log"
        
        if not log_file.exists():
            return False
        
        with open(log_file, 'r') as f:
            for line in f:
                record = json.loads(line)
                stored_hash = record.pop('hash')
                calculated_hash = self._generate_record_hash(record)
                
                if stored_hash != calculated_hash:
                    logger.error(f"Log integrity check failed: {record['access_id']}")
                    return False
        
        logger.info(f"✅ Log integrity verified: {log_date}")
        return True