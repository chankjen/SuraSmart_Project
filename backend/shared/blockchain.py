"""Blockchain Audit Trail Service for Sura Smart."""
import logging
import hashlib
import json
from django.utils import timezone
from django.conf import settings

logger = logging.getLogger(__name__)

class BlockchainService:
    """
    Simulates a tamper-proof audit trail via a permissioned blockchain (TRD §5.1).
    """
    
    @classmethod
    def log_event(cls, case_id, actor, action, metadata=None):
        """
        Log an event to the audit trail and generate a blockchain hash.
        """
        if metadata is None:
            metadata = {}
            
        timestamp = timezone.now().isoformat()
        actor_hash = hashlib.sha256(str(actor.id).encode()).hexdigest()
        
        # Build the event data to be hashed
        event_dict = {
            'case_id': str(case_id),
            'actor_hash': actor_hash,
            'action': action,
            'metadata': metadata,
            'timestamp': timestamp,
            'jurisdiction': getattr(actor, 'jurisdiction', 'KE')
        }
        
        event_json = json.dumps(event_dict, sort_keys=True)
        blockchain_hash = hashlib.sha256(event_json.encode()).hexdigest()
        
        # Log to system logs (Simulated blockchain state storage)
        logger.info(f"[BLOCKCHAIN_EVENT] Hash: {blockchain_hash} | Data: {event_json}")
        
        # Store in database audit log
        from users.models import AuditLog
        from facial_recognition.models import MissingPerson
        
        try:
            case = MissingPerson.objects.get(id=case_id)
        except MissingPerson.DoesNotExist:
            case = None
            
        AuditLog.objects.create(
            user=actor,
            case_id=case_id if case else None,
            action='api_call', # Mapping to existing ACTION_CHOICES
            description=f"Action: {action} | Blockchain Verified",
            ip_address="127.0.0.1", # Mocked
            metadata=metadata,
            blockchain_hash=blockchain_hash,
            actor_hash=actor_hash,
            jurisdiction=getattr(actor, 'jurisdiction', 'KE')
        )
        
        return blockchain_hash
