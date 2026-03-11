# security/consent_manager.py
"""
Sura Smart Consent Manager
TRD Section 5.2.1: User Consent Management
TRD Section 8: GDPR/CCPA Compliance
"""

import os
import logging
from typing import Dict, Optional
from datetime import datetime, timedelta
from pathlib import Path
import json

logger = logging.getLogger(__name__)


class ConsentManager:
    """
    Manages user consent for data processing.
    
    TRD 5.2.1: User consent management system
    TRD 8: GDPR/CCPA compliant data handling
    TRD 8: BIPA compliance for biometric data
    """
    
    def __init__(self, consent_dir: str = 'data/consents'):
        """
        Initialize consent manager.
        
        Args:
            consent_dir: Directory for consent records
        """
        self.consent_dir = Path(consent_dir)
        self.consent_dir.mkdir(parents=True, exist_ok=True)
        
        # Consent types
        self.consent_types = {
            'facial_recognition': {
                'required': True,
                'regulation': 'BIPA',
                'expiry_days': 365
            },
            'data_processing': {
                'required': True,
                'regulation': 'GDPR',
                'expiry_days': 365
            },
            'data_sharing': {
                'required': False,
                'regulation': 'CCPA',
                'expiry_days': 365
            },
            'marketing': {
                'required': False,
                'regulation': 'GDPR',
                'expiry_days': 180
            }
        }
        
        logger.info("✅ Consent Manager initialized")
    
    def record_consent(self,
                       user_id: str,
                       consent_type: str,
                       granted: bool,
                       metadata: Optional[Dict] = None) -> Dict:
        """
        Record user consent.
        
        TRD 5.2.1: User consent management
        TRD 8: BIPA compliance
        """
        if consent_type not in self.consent_types:
            logger.error(f"Unknown consent type: {consent_type}")
            return {'success': False, 'error': 'Invalid consent type'}
        
        timestamp = datetime.now().isoformat()
        expiry_days = self.consent_types[consent_type]['expiry_days']
        expiry_date = (datetime.now() + timedelta(days=expiry_days)).isoformat()
        
        consent_record = {
            'user_id': user_id,
            'consent_type': consent_type,
            'granted': granted,
            'timestamp': timestamp,
            'expiry_date': expiry_date,
            'ip_address': metadata.get('ip_address') if metadata else None,
            'user_agent': metadata.get('user_agent') if metadata else None,
            'version': '1.0'
        }
        
        # Save consent record
        consent_file = self.consent_dir / f"{user_id}_{consent_type}.json"
        with open(consent_file, 'w') as f:
            json.dump(consent_record, f, indent=2)
        
        logger.info(f"✅ Consent recorded: {user_id} - {consent_type} = {granted}")
        
        return {
            'success': True,
            'consent_record': consent_record,
            'expiry_date': expiry_date
        }
    
    def verify_consent(self,
                       user_id: str,
                       consent_type: str,
                       action: str) -> bool:
        """
        Verify user consent before action.
        
        TRD 5.2.1: Consent verification
        TRD 8: BIPA compliance for biometric searches
        """
        consent_file = self.consent_dir / f"{user_id}_{consent_type}.json"
        
        if not consent_file.exists():
            logger.warning(f"No consent record: {user_id} - {consent_type}")
            return False
        
        with open(consent_file, 'r') as f:
            consent_record = json.load(f)
        
        # Check if consent was granted
        if not consent_record.get('granted', False):
            logger.warning(f"Consent not granted: {user_id} - {consent_type}")
            return False
        
        # Check if consent has expired
        expiry_date = datetime.fromisoformat(consent_record['expiry_date'])
        if datetime.now() > expiry_date:
            logger.warning(f"Consent expired: {user_id} - {consent_type}")
            return False
        
        # Check if consent type is required for action
        if self.consent_types[consent_type]['required']:
            return True
        
        return True
    
    def withdraw_consent(self, user_id: str, consent_type: str) -> Dict:
        """
        Allow user to withdraw consent.
        
        TRD 8: GDPR right to withdraw consent
        TRD 8: CCPA opt-out
        """
        consent_file = self.consent_dir / f"{user_id}_{consent_type}.json"
        
        if not consent_file.exists():
            return {'success': False, 'error': 'No consent record found'}
        
        # Update consent record
        with open(consent_file, 'r') as f:
            consent_record = json.load(f)
        
        consent_record['withdrawn'] = True
        consent_record['withdrawn_at'] = datetime.now().isoformat()
        consent_record['granted'] = False
        
        with open(consent_file, 'w') as f:
            json.dump(consent_record, f, indent=2)
        
        logger.info(f"✅ Consent withdrawn: {user_id} - {consent_type}")
        
        return {
            'success': True,
            'message': 'Consent withdrawn successfully',
            'withdrawn_at': consent_record['withdrawn_at']
        }
    
    def get_consent_status(self, user_id: str) -> Dict:
        """
        Get all consent statuses for user.
        
        TRD 8: User access to consent records
        """
        consent_status = {}
        
        for consent_type in self.consent_types.keys():
            consent_file = self.consent_dir / f"{user_id}_{consent_type}.json"
            
            if consent_file.exists():
                with open(consent_file, 'r') as f:
                    record = json.load(f)
                
                consent_status[consent_type] = {
                    'granted': record.get('granted', False),
                    'expired': datetime.now() > datetime.fromisoformat(record['expiry_date']),
                    'withdrawn': record.get('withdrawn', False),
                    'last_updated': record.get('timestamp')
                }
            else:
                consent_status[consent_type] = {
                    'granted': False,
                    'expired': False,
                    'withdrawn': False,
                    'last_updated': None
                }
        
        return consent_status
    
    def get_expired_consents(self) -> list:
        """
        Get list of expired consents.
        
        TRD 8: Consent expiry management
        """
        expired = []
        
        for consent_file in self.consent_dir.glob('*.json'):
            with open(consent_file, 'r') as f:
                record = json.load(f)
            
            if datetime.now() > datetime.fromisoformat(record['expiry_date']):
                expired.append({
                    'user_id': record['user_id'],
                    'consent_type': record['consent_type'],
                    'expired_at': record['expiry_date']
                })
        
        return expired
    
    def get_statistics(self) -> Dict:
        """Get consent management statistics"""
        total_consents = len(list(self.consent_dir.glob('*.json')))
        expired_consents = len(self.get_expired_consents())
        
        return {
            'total_consent_records': total_consents,
            'expired_consents': expired_consents,
            'consent_types': list(self.consent_types.keys()),
            'trd_compliance': {
                '5.2.1_consent_management': True,
                '8_gdpr_ccpa_bipa': True
            },
            'last_updated': datetime.now().isoformat()
        }