# security/__init__.py
"""
Sura Smart Security Module
TRD Section 5: Security Requirements
TRD Section 5.1: Data Protection
TRD Section 5.2: Privacy Controls
"""

from .encryption import EncryptionService
from .consent_manager import ConsentManager
from .data_purger import DataPurger
from .access_logger import AccessLogger
from .privacy_controls import PrivacyControls

__version__ = '1.0.0'
__all__ = [
    'EncryptionService',
    'ConsentManager',
    'DataPurger',
    'AccessLogger',
    'PrivacyControls'
]

# TRD 5.1.1: Encryption standards
ENCRYPTION_ALGORITHM = 'AES-256-GCM'

# TRD 5.2.2: Data retention period
DEFAULT_RETENTION_DAYS = 90