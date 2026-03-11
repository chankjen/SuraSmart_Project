# notifications/email_service.py
"""
Sura Smart Email Notification Service
TRD Section 1.1.6: Notification System
"""

import os
import logging
from typing import Dict, Optional
from datetime import datetime
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

logger = logging.getLogger(__name__)


class EmailService:
    """
    Email notification service.
    
    TRD 1.1.6: Notification system
    TRD 6.1.1: Fast notification delivery
    """
    
    def __init__(self,
                 smtp_host: str = None,
                 smtp_port: int = None,
                 smtp_user: str = None,
                 smtp_password: str = None):
        """Initialize email service"""
        self.smtp_host = smtp_host or os.environ.get('SMTP_HOST', 'smtp.gmail.com')
        self.smtp_port = smtp_port or int(os.environ.get('SMTP_PORT', '587'))
        self.smtp_user = smtp_user or os.environ.get('SMTP_USER')
        self.smtp_password = smtp_password or os.environ.get('SMTP_PASSWORD')
        self.from_email = os.environ.get('FROM_EMAIL', 'noreply@surasmart.com')
        
        # Delivery tracking
        self.emails_sent = 0
        self.emails_failed = 0
        
        logger.info(f"✅ Email Service initialized: {self.smtp_host}")
    
    def send(self,
             to: str,
             subject: str,
             body: str,
             priority: str = 'normal',
             html: bool = False) -> Dict:
        """
        Send email notification.
        
        TRD 1.1.6: Automatic alerts
        """
        try:
            msg = MIMEMultipart('alternative')
            msg['Subject'] = subject
            msg['From'] = self.from_email
            msg['To'] = to
            
            # Add priority header
            if priority == 'high':
                msg['X-Priority'] = '1'
                msg['X-MSMail-Priority'] = 'High'
            
            # Attach body
            content_type = 'html' if html else 'plain'
            msg.attach(MIMEText(body, content_type))
            
            # Send email
            with smtplib.SMTP(self.smtp_host, self.smtp_port) as server:
                server.starttls()
                server.login(self.smtp_user, self.smtp_password)
                server.send_message(msg)
            
            self.emails_sent += 1
            
            logger.info(f"📧 Email sent to {to}")
            
            return {
                'success': True,
                'to': to,
                'subject': subject,
                'sent_at': datetime.now().isoformat(),
                'channel': 'email'
            }
            
        except Exception as e:
            self.emails_failed += 1
            logger.error(f"Email send failed: {str(e)}")
            
            return {
                'success': False,
                'error': str(e),
                'channel': 'email'
            }
    
    def get_statistics(self) -> Dict:
        """Get email service statistics"""
        total = self.emails_sent + self.emails_failed
        success_rate = (self.emails_sent / total * 100) if total > 0 else 0
        
        return {
            'emails_sent': self.emails_sent,
            'emails_failed': self.emails_failed,
            'success_rate_percent': success_rate,
            'last_sent': datetime.now().isoformat()
        }