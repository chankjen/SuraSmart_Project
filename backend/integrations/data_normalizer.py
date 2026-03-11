# integrations/data_normalizer.py
"""
Sura Smart Data Normalization Layer
TRD Section 4.1.2: Data Normalization
TRD Section 4.1: Database Connections
"""

import logging
from typing import Dict, List, Any, Optional
from datetime import datetime
import re

logger = logging.getLogger(__name__)


class DataNormalizer:
    """
    Normalizes data from different database schemas.
    
    TRD 4.1.2: Data normalization layer to handle different database schemas
    TRD 4.1: Secure API integrations
    """
    
    # Standard field mappings
    STANDARD_FIELDS = {
        'first_name': ['first_name', 'fname', 'given_name', 'firstname'],
        'last_name': ['last_name', 'lname', 'surname', 'family_name'],
        'date_of_birth': ['date_of_birth', 'dob', 'birth_date', 'birthdate'],
        'gender': ['gender', 'sex', 'gender_identity'],
        'ethnicity': ['ethnicity', 'race', 'ethnic_group'],
        'height': ['height', 'height_cm', 'height_ft'],
        'weight': ['weight', 'weight_kg', 'weight_lbs'],
        'photo_url': ['photo_url', 'image_url', 'photo', 'image'],
        'last_seen_date': ['last_seen_date', 'last_seen', 'disappeared_date'],
        'last_seen_location': ['last_seen_location', 'last_seen_place', 'location'],
        'case_number': ['case_number', 'case_id', 'reference_number'],
        'status': ['status', 'case_status', 'record_status']
    }
    
    def __init__(self):
        self.field_mappings = self._build_field_mapping()
        logger.info("✅ Data Normalizer initialized")
    
    def _build_field_mapping(self) -> Dict[str, str]:
        """Build reverse field mapping"""
        mapping = {}
        for standard_field, variants in self.STANDARD_FIELDS.items():
            for variant in variants:
                mapping[variant.lower()] = standard_field
        return mapping
    
    def normalize_record(self, record: Dict, source_type: str) -> Dict:
        """
        Normalize a record from external database.
        
        TRD 4.1.2: Handle different database schemas
        TRD 5.2.1: Data minimization principles
        """
        normalized = {
            'source_type': source_type,
            'normalized_at': datetime.now().isoformat(),
            'data': {}
        }
        
        # Normalize field names
        for key, value in record.items():
            standard_key = self.field_mappings.get(key.lower(), key)
            normalized['data'][standard_key] = self._normalize_value(value, standard_key)
        
        # Add required fields if missing
        normalized['data'] = self._add_missing_fields(normalized['data'])
        
        # TRD 5.2.1: Remove sensitive fields not needed for matching
        normalized['data'] = self._apply_data_minimization(normalized['data'])
        
        return normalized
    
    def _normalize_value(self, value: Any, field_name: str) -> Any:
        """Normalize field value based on field type"""
        if value is None:
            return None
        
        if field_name in ['date_of_birth', 'last_seen_date']:
            return self._normalize_date(value)
        
        elif field_name in ['height', 'weight']:
            return self._normalize_measurement(value, field_name)
        
        elif field_name == 'gender':
            return self._normalize_gender(value)
        
        elif field_name == 'phone_number':
            return self._normalize_phone(value)
        
        else:
            return str(value).strip() if isinstance(value, str) else value
    
    def _normalize_date(self, value: Any) -> Optional[str]:
        """Normalize date to ISO format"""
        if isinstance(value, datetime):
            return value.isoformat()
        
        if isinstance(value, str):
            # Try common date formats
            date_formats = [
                '%Y-%m-%d',
                '%d/%m/%Y',
                '%m/%d/%Y',
                '%Y%m%d',
                '%d-%m-%Y'
            ]
            
            for fmt in date_formats:
                try:
                    return datetime.strptime(value, fmt).isoformat()
                except ValueError:
                    continue
        
        return None
    
    def _normalize_measurement(self, value: Any, field_name: str) -> Optional[float]:
        """Normalize measurements to standard units"""
        if isinstance(value, (int, float)):
            return float(value)
        
        if isinstance(value, str):
            # Extract numeric value
            match = re.search(r'[\d.]+', value)
            if match:
                return float(match.group())
        
        return None
    
    def _normalize_gender(self, value: Any) -> Optional[str]:
        """
        Normalize gender values.
        
        PRD 8: Gender sensitivity & linguistic diversity
        """
        if isinstance(value, str):
            value = value.lower().strip()
            
            gender_map = {
                'm': 'male',
                'male': 'male',
                'man': 'male',
                'f': 'female',
                'female': 'female',
                'woman': 'female',
                'other': 'other',
                'non-binary': 'non-binary',
                'nb': 'non-binary',
                'x': 'non-binary'
            }
            
            return gender_map.get(value, 'other')
        
        return None
    
    def _normalize_phone(self, value: Any) -> Optional[str]:
        """Normalize phone number to E.164 format"""
        if isinstance(value, str):
            # Remove non-numeric characters
            digits = re.sub(r'\D', '', value)
            
            # Add country code if missing (default to US)
            if len(digits) == 10:
                digits = '+1' + digits
            elif len(digits) == 11 and digits[0] == '1':
                digits = '+' + digits
            
            return digits
        
        return None
    
    def _add_missing_fields(self, data: Dict) -> Dict:
        """Add missing required fields with null values"""
        required_fields = [
            'first_name',
            'last_name',
            'date_of_birth',
            'gender',
            'photo_url',
            'case_number',
            'status'
        ]
        
        for field in required_fields:
            if field not in data:
                data[field] = None
        
        return data
    
    def _apply_data_minimization(self, data: Dict) -> Dict:
        """
        Apply data minimization principles.
        
        TRD 5.2.1: Data minimization for privacy
        TRD 8: GDPR/CCPA compliance
        """
        # Fields to exclude from matching (privacy-sensitive)
        exclude_fields = [
            'social_security_number',
            'passport_number',
            'drivers_license',
            'medical_records',
            'financial_information',
            'home_address'
        ]
        
        for field in exclude_fields:
            data.pop(field, None)
        
        return data
    
    def normalize_batch(self, records: List[Dict], source_type: str) -> List[Dict]:
        """
        Normalize multiple records.
        
        TRD 4.1.2: Batch processing for efficiency
        """
        return [self.normalize_record(record, source_type) for record in records]
    
    def validate_normalized_record(self, record: Dict) -> bool:
        """
        Validate normalized record has required fields.
        
        TRD 4.1: Data quality validation
        """
        required_fields = ['first_name', 'last_name', 'case_number']
        
        data = record.get('data', {})
        
        for field in required_fields:
            if not data.get(field):
                logger.warning(f"Missing required field: {field}")
                return False
        
        return True