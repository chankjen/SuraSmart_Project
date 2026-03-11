import os
import django
import sys

# Setup Django environment
sys.path.append(r'd:\SuraSmart_Project\backend')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sura_smart_backend.settings')
django.setup()

from ai_models.facial_recognition.models import MissingPerson
from ai_models.facial_recognition.state_machine import CaseStateMachine
from users.models import User

def verify():
    # 1. Get or create a test case in REPORTED status
    case = MissingPerson.objects.filter(status='REPORTED').first()
    if not case:
        print("No REPORTED case found, creating one...")
        # Get a user to be the reporter
        reporter = User.objects.first()
        case = MissingPerson.objects.create(
            full_name="Test Verification Person",
            reported_by=reporter,
            status='REPORTED'
        )
    
    print(f"Initial status: {case.status}")
    
    # 2. Get a police officer user
    officer = User.objects.filter(role='police_officer').first()
    if not officer:
        print("Creating a test police officer...")
        officer = User.objects.create_user(
            username='test_officer_verify_new',
            password='TestPassword123!',
            role='police_officer'
        )
    
    sm = CaseStateMachine(case)
    
    # 3. Test transition: REPORTED -> ANALYZED (as per our fix in views.py logic)
    print("Attempting transition REPORTED -> ANALYZED...")
    try:
        sm.transition_to('ANALYZED', actor=officer, notes='Verification test')
        # Refresh from DB
        case.refresh_from_db()
        print(f"Status after transition: {case.status}")
    except Exception as e:
        print(f"FAILED transition to ANALYZED: {e}")
        return

    # 4. Test transition: ANALYZED -> PENDING_CLOSURE (original logic)
    print("Attempting transition ANALYZED -> PENDING_CLOSURE...")
    try:
        sm.transition_to('PENDING_CLOSURE', actor=officer, notes='Verification test closure')
        case.refresh_from_db()
        print(f"Status after transition: {case.status}")
    except Exception as e:
        print(f"FAILED transition to PENDING_CLOSURE: {e}")
        return

    print("Verification SUCCESSFUL!")

if __name__ == "__main__":
    verify()
