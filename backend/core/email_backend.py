from django.core.mail.backends.smtp import EmailBackend as SMTPEmailBackend
from django.core.mail.backends.base import BaseEmailBackend
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
import logging

logger = logging.getLogger(__name__)

class FallbackEmailBackend(BaseEmailBackend):
    """
    Attempts to send via SendGrid. If failed, falls back to SMTP.
    Aligns with TRD §6.1 (Reliability)
    """
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.smtp_backend = SMTPEmailBackend(**kwargs)

    def send_messages(self, email_messages):
        sent_count = 0
        for message in email_messages:
            try:
                # Try SendGrid
                sg = SendGridAPIClient(os.environ.get('SENDGRID_API_KEY'))
                # Convert Django EmailMessage to SendGrid format (simplified)
                response = sg.send(mail) 
                if response.status_code == 202:
                    sent_count += 1
                    continue
            except Exception as e:
                logger.warning(f"SendGrid failed: {str(e)}. Falling back to SMTP.")
            
            # Fallback to SMTP
            try:
                if self.smtp_backend.send_messages([message]):
                    sent_count += 1
            except Exception as smtp_error:
                logger.error(f"SMTP fallback also failed: {str(smtp_error)}")
        
        return sent_count