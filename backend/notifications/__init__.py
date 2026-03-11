# notifications/__init__.py
"""
Sura Smart Notification System
TRD Section 1.1.6: Notification System
TRD Section 4.1: Real-time Alerts
"""

from .email_service import EmailService
from .sms_service import SMSService
from .push_notifications import PushNotificationService
from .alert_manager import AlertManager

__version__ = '1.0.0'
__all__ = [
    'EmailService',
    'SMSService',
    'PushNotificationService',
    'AlertManager'
]

# Notification priority levels
PRIORITY_LOW = 'low'
PRIORITY_NORMAL = 'normal'
PRIORITY_HIGH = 'high'
PRIORITY_CRITICAL = 'critical'

# TRD 6.1.1: Notification delivery SLA
NOTIFICATION_DELIVERY_SLA = 5.0  # seconds