# integrations/__init__.py
"""
Sura Smart Database Integration Module
TRD Section 4.1: Database Connections
TRD Section 4.1.1: Government Database Integrations
"""

from .morgue_db import MorgueDatabase
from .police_db import PoliceDatabase
from .prison_db import PrisonDatabase
from .public_records import PublicRecordsDatabase
from .data_normalizer import DataNormalizer

__version__ = '1.0.0'
__all__ = [
    'MorgueDatabase',
    'PoliceDatabase',
    'PrisonDatabase',
    'PublicRecordsDatabase',
    'DataNormalizer'
]

# TRD 4.1.2: Rate limiting configuration
RATE_LIMIT_PER_MINUTE = 60
RATE_LIMIT_PER_HOUR = 1000

# TRD 6.1.1: Database response time SLA
DATABASE_RESPONSE_SLA = 5.0  # seconds