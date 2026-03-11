# utils/validators.py
"""
Sura Smart Validation Functions
TRD Section 6.2: AI Performance Validation
"""

import re
from typing import Optional, List, Dict
from datetime import datetime


def validate_email(email: str) -> bool:
    """Validate email format"""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email))


def validate_phone(phone: str) -> bool:
    """Validate phone number (E.164 format)"""
    pattern = r'^\+?[1-9]\d{1,14}$'
    return bool(re.match(pattern, phone.replace('-', '').replace(' ', '')))


def validate_date(date_str: str, format: str = '%Y-%m-%d') -> bool:
    """Validate date string"""
    try:
        datetime.strptime(date_str, format)
        return True
    except ValueError:
        return False


def validate_embedding(embedding: List[float], dimension: int = 512) -> bool:
    """
    Validate face embedding.
    
    TRD 3.1: Facial Recognition System
    """
    if not isinstance(embedding, list):
        return False
    
    if len(embedding) != dimension:
        return False
    
    # Check for NaN or Inf
    import math
    for value in embedding:
        if math.isnan(value) or math.isinf(value):
            return False
    
    return True


def validate_user_role(role: str) -> bool:
    """
    Validate user role.
    
    TRD 4.2.3: Permission-based access
    """
    valid_roles = ['family', 'law_enforcement', 'admin', 'auditor']
    return role in valid_roles


def validate_search_query(query: Dict) -> Dict:
    """
    Validate search query parameters.
    
    TRD 6.1.1: Search completion time
    """
    errors = []
    
    if 'image' not in query and 'embedding' not in query:
        errors.append('image or embedding required')
    
    if 'user_id' not in query:
        errors.append('user_id required')
    
    return {
        'valid': len(errors) == 0,
        'errors': errors
    }