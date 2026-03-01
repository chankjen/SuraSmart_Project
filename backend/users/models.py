from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.translation import gettext_lazy as _
from django.core.exceptions import ValidationError


def validate_eight_digits(value):
    """Validator for 8-digit IDs."""
    if not str(value).isdigit() or len(str(value)) != 8:
        raise ValidationError('This field must be exactly 8 digits.')


class User(AbstractUser):
    """Custom user model with role-based access control."""
    
    ROLE_CHOICES = (
        ('family_member', _('Family Member')),
        ('police_officer', _('Police Officer')),
        ('government_official', _('Government Official')),
        ('morgue_staff', _('Morgue Staff')),
        ('admin', _('Administrator')),
    )
    
    role = models.CharField(
        max_length=20,
        choices=ROLE_CHOICES,
        default='family_member',
        help_text=_('User role determines database access and permissions')
    )
    jurisdiction = models.CharField(
        max_length=50,
        choices=(('KE', _('Kenya')), ('EU', _('European Union')), ('US', _('United States'))),
        default='KE',
        help_text=_('User jurisdiction for data residency compliance')
    )
    phone_number = models.CharField(max_length=20, blank=True, null=True)
    organization = models.CharField(max_length=255, blank=True, null=True)
    
    # Role-specific identification fields
    national_id = models.CharField(
        max_length=8,
        blank=True,
        null=True,
        help_text=_('8-digit National ID for Family Members'),
        validators=[validate_eight_digits]
    )
    service_id = models.CharField(
        max_length=8,
        blank=True,
        null=True,
        help_text=_('8-digit Service ID for Police Officers'),
        validators=[validate_eight_digits]
    )
    police_rank = models.CharField(
        max_length=50,
        choices=(
            ('ig', _('Inspector-General (IG)')),
            ('dig', _('Deputy Inspector-General (DIG)')),
            ('saig', _('Senior Assistant Inspector-General (SAIG)')),
            ('aig', _('Assistant Inspector-General (AIG)')),
            ('ssp', _('Senior Superintendent of Police (SSP)')),
            ('sp', _('Superintendent of Police (SP)')),
            ('asp', _('Assistant Superintendent of Police (ASP)')),
            ('ci', _('Chief Inspector (CI)')),
            ('ip', _('Inspector of Police (IP)')),
            ('ssgt', _('Senior Sergeant (SSgt)')),
            ('sgt', _('Sergeant (Sgt)')),
            ('cpl', _('Corporal (Cpl)')),
            ('constable', _('Constable')),
        ),
        blank=True,
        null=True,
        help_text=_('Police rank for Police Officers')
    )
    government_security_id = models.CharField(
        max_length=8,
        blank=True,
        null=True,
        help_text=_('8-digit Government Security ID for Government Officials'),
        validators=[validate_eight_digits]
    )
    government_position = models.CharField(
        max_length=20,
        choices=(
            ('cs', _('CS')),
            ('ps', _('PS')),
            ('security_officer', _('Security Officer')),
            ('other', _('Other - specify')),
        ),
        blank=True,
        null=True,
        help_text=_('Government position for Government Officials')
    )
    position_specify = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        help_text=_('Specify position if "Other" is selected')
    )
    
    verification_status = models.CharField(
        max_length=20,
        choices=(
            ('pending', _('Pending')),
            ('verified', _('Verified')),
            ('rejected', _('Rejected')),

        ),
        default='pending'
    )
    is_active_user = models.BooleanField(
        default=True,
        help_text=_('Designates whether this user can log in')
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = _('User')
        verbose_name_plural = _('Users')
    
    def __str__(self):
        return f'{self.username} ({self.get_role_display()})'


class AuditLog(models.Model):
    """Immutable audit trail for all sensitive operations."""
    
    ACTION_CHOICES = (
        ('search', _('Search')),
        ('match_found', _('Match Found')),
        ('data_access', _('Data Access')),
        ('user_login', _('User Login')),
        ('api_call', _('API Call')),
    )
    
    user = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='audit_logs'
    )
    action = models.CharField(max_length=20, choices=ACTION_CHOICES)
    description = models.TextField()
    ip_address = models.GenericIPAddressField()
    user_agent = models.TextField(blank=True)
    metadata = models.JSONField(default=dict, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True, db_index=True)
    
    # Immutable audit log fields (TRD §5.1)
    blockchain_hash = models.CharField(max_length=64, blank=True, null=True, unique=True)
    actor_hash = models.CharField(max_length=64, blank=True, null=True, help_text=_('Privacy-preserving hash of the user ID'))
    jurisdiction = models.CharField(max_length=50, blank=True, null=True)
    
    class Meta:
        ordering = ['-timestamp']
        verbose_name = _('Audit Log')
        verbose_name_plural = _('Audit Logs')
        indexes = [
            models.Index(fields=['user', 'timestamp']),
            models.Index(fields=['action', 'timestamp']),
        ]
    
    def __str__(self):
        return f'{self.user} - {self.get_action_display()} at {self.timestamp}'


class Permission(models.Model):
    """Granular permission model for RBAC system."""
    
    RESOURCE_CHOICES = (
        ('facial_recognition', _('Facial Recognition')),
        ('morgue_database', _('Morgue Database')),
        ('jail_database', _('Jail Database')),
        ('police_database', _('Police Database')),
        ('user_management', _('User Management')),
    )
    
    role = models.CharField(max_length=20, choices=User.ROLE_CHOICES)
    resource = models.CharField(max_length=50, choices=RESOURCE_CHOICES)
    can_read = models.BooleanField(default=False)
    can_write = models.BooleanField(default=False)
    can_delete = models.BooleanField(default=False)
    
    class Meta:
        unique_together = ('role', 'resource')
        verbose_name = _('Permission')
        verbose_name_plural = _('Permissions')
    
    def __str__(self):
        return f'{self.role} - {self.resource}'
