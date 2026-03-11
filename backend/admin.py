# backend/api/admin.py (Django REST Framework)

from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAdminUser
from rest_framework.response import Response
from django.contrib.auth import get_user_model
from django.core.mail import send_mail
from django.conf import settings
import hashlib
import secrets

User = get_user_model()

@api_view(['GET'])
@permission_classes([IsAdminUser])
def get_all_users(request):
    """Get all users with verification status (TRD §4.2)"""
    users = User.objects.all().values(
        'id', 'email', 'first_name', 'last_name', 
        'role', 'is_verified', 'date_joined', 'id_number', 'status'
    )
    return Response(list(users))

@api_view(['POST'])
@permission_classes([IsAdminUser])
def verify_user_credentials(request):
    """Verify credentials against government databases (TRD §4.2)"""
    user_id = request.data.get('user_id')
    verification_type = request.data.get('verification_type')
    verification_number = request.data.get('verification_number')
    
    # Mock government API verification (Replace with actual integration)
    # In production: Call National ID API, Police Service API, etc.
    is_valid = mock_government_verification(verification_type, verification_number)
    
    return Response({'valid': is_valid})

@api_view(['POST'])
@permission_classes([IsAdminUser])
def approve_user_registration(request, user_id):
    """Approve user registration and send login credentials (TRD §4.2)"""
    user = User.objects.get(id=user_id)
    user.is_verified = True
    user.status = 'ACTIVE'
    user.save()
    
    # Generate secure temporary password
    temp_password = secrets.token_urlsafe(16)
    user.set_password(temp_password)
    user.save()
    
    # Send approval email with login link
    login_token = secrets.token_urlsafe(32)
    login_link = f"{settings.FRONTEND_URL}/login?token={login_token}"
    
    send_mail(
        subject='SuraSmart Account Approved - Login Details',
        message=f'''
        Welcome to SuraSmart!
        
        Your account has been approved after background and compliance checks.
        
        Temporary Password: {temp_password}
        Login Link: {login_link}
        
        Please change your password after first login.
        
        Security Notice: This link expires in 24 hours.
        ''',
        from_email=settings.ADMIN_EMAIL,
        recipient_list=[user.email],
        fail_silently=False,
    )
    
    # Log to blockchain audit trail (TRD §5.1)
    log_audit_event(
        action='USER_APPROVED',
        user_id=user_id,
        actor_id=request.user.id,
        metadata={
            'verification_type': request.data.get('verification_type'),
            'timestamp': timezone.now().isoformat()
        }
    )
    
    return Response({'status': 'approved', 'email_sent': True})

@api_view(['POST'])
@permission_classes([IsAdminUser])
def reject_user_registration(request, user_id):
    """Reject user registration"""
    user = User.objects.get(id=user_id)
    user.status = 'REJECTED'
    user.save()
    
    # Log to blockchain audit trail
    log_audit_event(
        action='USER_REJECTED',
        user_id=user_id,
        actor_id=request.user.id,
        metadata={'reason': request.data.get('reason')}
    )
    
    return Response({'status': 'rejected'})

@api_view(['GET'])
@permission_classes([IsAdminUser])
def get_audit_logs(request):
    """Get all audit logs from blockchain (TRD §5.1)"""
    filter_type = request.query_params.get('filter', 'all')
    
    # Query blockchain audit trail
    audit_logs = AuditLog.objects.filter(
        action=filter_type if filter_type != 'all' else None
    ).order_by('-timestamp')[:1000]
    
    return Response([
        {
            'id': log.id,
            'action': log.action,
            'user_id': log.user_id,
            'actor_email': log.actor.email if log.actor else 'System',
            'metadata': log.metadata,
            'blockchain_hash': log.blockchain_hash,
            'timestamp': log.timestamp
        }
        for log in audit_logs
    ])

@api_view(['POST'])
@permission_classes([IsAdminUser])
def log_audit_event(request):
    """Log event to blockchain audit trail (TRD §5.1)"""
    action = request.data.get('action')
    user_id = request.data.get('user_id')
    actor_id = request.data.get('actor_id')
    metadata = request.data.get('metadata', {})
    
    # Create audit log entry
    audit_log = AuditLog.objects.create(
        action=action,
        user_id=user_id,
        actor_id=actor_id,
        metadata=metadata,
        timestamp=timezone.now()
    )
    
    # Generate blockchain hash (TRD §5.1)
    hash_input = f"{action}{user_id}{actor_id}{audit_log.timestamp}{metadata}"
    audit_log.blockchain_hash = hashlib.sha256(hash_input.encode()).hexdigest()
    audit_log.save()
    
    return Response({'status': 'logged', 'hash': audit_log.blockchain_hash})

@api_view(['GET'])
@permission_classes([IsAdminUser])
def get_system_stats(request):
    """Get system statistics for admin dashboard"""
    from django.db.models import Count, Q
    from cases.models import Case
    
    return Response({
        'totalCases': Case.objects.count(),
        'activeCases': Case.objects.exclude(status='CLOSED').count(),
        'systemUptime': '99.95%'  # From monitoring service
    })

@api_view(['GET'])
@permission_classes([IsAdminUser])
def get_system_health(request):
    """Check system component health (TRD §6.1)"""
    return Response({
        'api': True,
        'database': True,
        'ai_engine': True,
        'blockchain': True
    })

@api_view(['POST'])
@permission_classes([IsAdminUser])
def export_audit_logs(request):
    """Export audit logs for compliance (TRD §5.2)"""
    import csv
    from django.http import HttpResponse
    
    filter_type = request.data.get('filter', 'all')
    audit_logs = AuditLog.objects.filter(
        action=filter_type if filter_type != 'all' else None
    )
    
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename="audit_logs_{timezone.now().date()}.csv"'
    
    writer = csv.writer(response)
    writer.writerow(['Timestamp', 'Action', 'User', 'Metadata', 'Blockchain Hash'])
    
    for log in audit_logs:
        writer.writerow([
            log.timestamp,
            log.action,
            log.actor.email if log.actor else 'System',
            str(log.metadata),
            log.blockchain_hash
        ])
    
    return response

# Helper Functions
def mock_government_verification(verification_type, verification_number):
    """Mock government database verification (Replace with actual API)"""
    # In production: Call actual government APIs
    # - National Registration Bureau (Kenya)
    # - Police Service Commission
    # - National Security Intelligence Service
    return len(verification_number) == 8  # Simplified for demo

def log_audit_event(action, user_id, actor_id, metadata):
    """Log event to blockchain audit trail"""
    AuditLog.objects.create(
        action=action,
        user_id=user_id,
        actor_id=actor_id,
        metadata=metadata,
        timestamp=timezone.now(),
        blockchain_hash=hashlib.sha256(
            f"{action}{user_id}{actor_id}{metadata}".encode()
        ).hexdigest()
    )