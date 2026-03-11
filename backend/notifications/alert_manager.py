"""Notifications app - Real-time alerting"""
# notifications/alert_manager.py
"""
Sura Smart Alert Manager
TRD Section 1.1.6: Real-time Alerting Framework
TRD Section 6.1.1: Search Completion Time < 30 Seconds
"""

import os
import logging
from typing import Dict, List, Optional
from datetime import datetime
from .email_service import EmailService
from .sms_service import SMSService
from .push_notifications import PushNotificationService

logger = logging.getLogger(__name__)


class AlertManager:
    """
    Manages real-time alerts for match notifications.
    
    TRD 1.1.6: Real-time alerting framework
    TRD 6.1.1: Notification within search completion time
    """
    
    def __init__(self):
        """Initialize alert manager with notification services"""
        self.email_service = EmailService()
        self.sms_service = SMSService()
        self.push_service = PushNotificationService()
        
        # Alert tracking
        self.alert_count = 0
        self.successful_deliveries = 0
        self.failed_deliveries = 0
        
        logger.info("✅ Alert Manager initialized")
    
    def send_match_alert(self,
                         user_id: str,
                         match_data: Dict,
                         priority: str = 'high',
                         channels: List[str] = None) -> Dict:
        """
        Send match alert to user.
        
        TRD 1.1.6: Automatic alerts when potential matches found
        TRD 6.1.1: Real-time notification
        """
        if channels is None:
            channels = ['email', 'push']  # Default channels
        
        alert_id = f"alert_{datetime.now().strftime('%Y%m%d_%H%M%S_%f')}"
        results = {
            'alert_id': alert_id,
            'user_id': user_id,
            'priority': priority,
            'timestamp': datetime.now().isoformat(),
            'channels': {}
        }
        
        # Send through each channel
        if 'email' in channels:
            results['channels']['email'] = self._send_email_alert(user_id, match_data)
        
        if 'sms' in channels:
            results['channels']['sms'] = self._send_sms_alert(user_id, match_data)
        
        if 'push' in channels:
            results['channels']['push'] = self._send_push_alert(user_id, match_data)
        
        # Track results
        self.alert_count += 1
        successful = sum(1 for r in results['channels'].values() if r.get('success'))
        self.successful_deliveries += successful
        self.failed_deliveries += len(channels) - successful
        
        logger.info(f"🔔 Alert sent: {alert_id} ({successful}/{len(channels)} channels)")
        
        return results
    
    def _send_email_alert(self, user_id: str, match_data: Dict) -> Dict:
        """Send email alert"""
        try:
            # Get user email from database
            user_email = self._get_user_email(user_id)
            
            if not user_email:
                return {'success': False, 'error': 'Email not found'}
            
            subject = f"Sura Smart: Potential Match Found"
            body = self._format_email_body(match_data)
            
            result = self.email_service.send(
                to=user_email,
                subject=subject,
                body=body,
                priority='high'
            )
            
            return result
            
        except Exception as e:
            logger.error(f"Email alert failed: {str(e)}")
            return {'success': False, 'error': str(e)}
    
    def _send_sms_alert(self, user_id: str, match_data: Dict) -> Dict:
        """Send SMS alert"""
        try:
            user_phone = self._get_user_phone(user_id)
            
            if not user_phone:
                return {'success': False, 'error': 'Phone not found'}
            
            message = self._format_sms_body(match_data)
            
            result = self.sms_service.send(
                to=user_phone,
                message=message,
                priority='high'
            )
            
            return result
            
        except Exception as e:
            logger.error(f"SMS alert failed: {str(e)}")
            return {'success': False, 'error': str(e)}
    
    def _send_push_alert(self, user_id: str, match_data: Dict) -> Dict:
        """Send push notification alert"""
        try:
            title = "Potential Match Found"
            body = f"A potential match has been found for your search."
            
            result = self.push_service.send(
                user_id=user_id,
                title=title,
                body=body,
                data=match_data,
                priority='high'
            )
            
            return result
            
        except Exception as e:
            logger.error(f"Push alert failed: {str(e)}")
            return {'success': False, 'error': str(e)}
    
    def _format_email_body(self, match_data: Dict) -> str:
        """Format email body for match alert"""
        return f"""
        Dear Sura Smart User,
        
        We have found a potential match for your search.
        
        Match Details:
        - Case Number: {match_data.get('case_number', 'N/A')}
        - Confidence: {match_data.get('confidence', 0):.1%}
        - Location: {match_data.get('last_seen_location', 'N/A')}
        - Date: {match_data.get('last_seen_date', 'N/A')}
        
        Please log in to your Sura Smart account for more details.
        
        Best regards,
        Sura Smart Team
        """
    
    def _format_sms_body(self, match_data: Dict) -> str:
        """Format SMS body for match alert"""
        return f"Sura Smart: Potential match found! Confidence: {match_data.get('confidence', 0):.0%}. Log in for details."
    
    def _get_user_email(self, user_id: str) -> Optional[str]:
        """Get user email from database"""
        # In production: Query user database
        return f"user_{user_id}@example.com"
    
    def _get_user_phone(self, user_id: str) -> Optional[str]:
        """Get user phone from database"""
        # In production: Query user database
        return f"+1234567890"
    
    def send_bulk_alerts(self,
                         user_ids: List[str],
                         match_data: Dict,
                         priority: str = 'normal') -> Dict:
        """
        Send alerts to multiple users.
        
        TRD 6.1.3: Support for 10,000 concurrent users
        """
        results = {
            'total_users': len(user_ids),
            'successful': 0,
            'failed': 0,
            'details': []
        }
        
        for user_id in user_ids:
            alert_result = self.send_match_alert(
                user_id=user_id,
                match_data=match_data,
                priority=priority
            )
            
            if any(c.get('success') for c in alert_result['channels'].values()):
                results['successful'] += 1
            else:
                results['failed'] += 1
            
            results['details'].append(alert_result)
        
        logger.info(f"📢 Bulk alerts: {results['successful']}/{results['total_users']} successful")
        
        return results
    
    def get_alert_statistics(self) -> Dict:
        """
        Get alert delivery statistics.
        
        TRD 7.4: Monitoring
        """
        success_rate = (
            self.successful_deliveries / self.alert_count * 100
            if self.alert_count > 0 else 0
        )
        
        return {
            'total_alerts': self.alert_count,
            'successful_deliveries': self.successful_deliveries,
            'failed_deliveries': self.failed_deliveries,
            'success_rate_percent': success_rate,
            'last_alert': datetime.now().isoformat()
        }
    
    def test_alert_system(self, user_id: str) -> Dict:
        """
        Test alert system functionality.
        
        TRD 7.3: Deployment validation
        """
        test_data = {
            'case_number': 'TEST_001',
            'confidence': 0.95,
            'last_seen_location': 'Test Location',
            'last_seen_date': datetime.now().isoformat()
        }
        
        result = self.send_match_alert(
            user_id=user_id,
            match_data=test_data,
            priority='low',
            channels=['email']
        )
        
        return {
            'test_status': 'completed',
            'result': result,
            'timestamp': datetime.now().isoformat()
        }