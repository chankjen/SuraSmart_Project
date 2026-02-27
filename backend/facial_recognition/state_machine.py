"""Case State Machine for Sura Smart Case Lifecycle."""
import logging
from django.utils import timezone
from .models import MissingPerson
from shared.blockchain import BlockchainService

logger = logging.getLogger(__name__)

class CaseStateMachine:
    """
    Handles transitions between case states and triggers side effects.
    """
    
    VALID_TRANSITIONS = {
        'REPORTED': ['UNDER_INVESTIGATION', 'CLOSED'],
        'UNDER_INVESTIGATION': ['MATCH_FOUND', 'NO_MATCH', 'CLOSED'],
        'MATCH_FOUND': ['PENDING_CLOSURE', 'UNDER_INVESTIGATION', 'CLOSED'],
        'PENDING_CLOSURE': ['CLOSED', 'UNDER_INVESTIGATION'],
        'NO_MATCH': ['UNDER_INVESTIGATION', 'CLOSED'],
        'CLOSED': [], # Terminal state
    }

    def __init__(self, case):
        self.case = case

    def transition_to(self, new_state, actor, notes=''):
        """
        Transitions the case to a new state if valid.
        """
        current_state = self.case.status
        
        if new_state not in self.VALID_TRANSITIONS.get(current_state, []):
            raise ValueError(f"Invalid transition from {current_state} to {new_state}")

        # Perform transition
        self.case.status = new_state
        
        if new_state == 'CLOSED':
            self.case.resolved_at = timezone.now()
            
        self.case.save()
        
        # Log to audit trail
        BlockchainService.log_event(
            case_id=self.case.id,
            actor=actor,
            action=f"TRANSITION_{current_state}_TO_{new_state}",
            metadata={'notes': notes}
        )
        logger.info(f"Case {self.case.id} transitioned from {current_state} to {new_state} by {actor.username}")
        
        return True

    def toggle_signature(self, actor_role):
        """
        Handles dual-signature logic for case closure.
        """
        if self.case.status != 'PENDING_CLOSURE':
            # Auto-transition to PENDING_CLOSURE if a signature is provided and it's currently MATCH_FOUND
            if self.case.status == 'MATCH_FOUND':
                self.case.status = 'PENDING_CLOSURE'
            else:
                raise ValueError("Dual-signature can only be applied to cases in PENDING_CLOSURE or MATCH_FOUND state.")

        if actor_role == 'family_member':
            self.case.dual_signature_family = True
        elif actor_role == 'police_officer':
            self.case.dual_signature_police = True
        
        self.case.save()

        if self.case.dual_signature_family and self.case.dual_signature_police:
            self.transition_to('CLOSED', actor=self.case.assigned_officer_id or self.case.reported_by, notes="Dual signature confirmed")
            return True
            
        BlockchainService.log_event(
            case_id=self.case.id,
            actor=self.case.reported_by, # Approximate, better if we pass the current actor
            action=f"SIGNATURE_ADDED_BY_{actor_role}",
            metadata={'role': actor_role}
        )
        return False
