# backend/settings.py

import os
from datetime import timedelta

# ... (Standard Django Settings)

# =============================================================================
# 1. Email Fallback Configuration (SendGrid → SMTP)
# =============================================================================
# Custom backend path (see core/email_backends.py)
EMAIL_BACKEND = 'core.email_backends.FallbackEmailBackend'

# Primary: SendGrid
SENDGRID_API_KEY = os.environ.get('SENDGRID_API_KEY')
SENDGRID_SANDBOX_MODE = False

# Fallback: SMTP
EMAIL_FALLBACK_SMTP_HOST = os.environ.get('EMAIL_FALLBACK_HOST', 'smtp.gmail.com')
EMAIL_FALLBACK_SMTP_PORT = int(os.environ.get('EMAIL_FALLBACK_PORT', 587))
EMAIL_FALLBACK_SMTP_USER = os.environ.get('EMAIL_FALLBACK_USER')
EMAIL_FALLBACK_SMTP_PASSWORD = os.environ.get('EMAIL_FALLBACK_PASSWORD')
EMAIL_FALLBACK_USE_TLS = True

# =============================================================================
# 2. Security & Token Expiry (TRD §4.2)
# =============================================================================
# Login Token Expiry: 10 Minutes
ACCOUNT_LOGIN_TOKEN_EXPIRY = timedelta(minutes=10)

# Password Hashing
PASSWORD_HASHERS = [
    'django.contrib.auth.hashers.Argon2PasswordHasher', # Preferred
    'django.contrib.auth.hashers.PBKDF2PasswordHasher',
]

# =============================================================================
# 3. Audit Log Retention (TRD §5.2)
# =============================================================================
# Days to retain audit logs before auto-purge
AUDIT_LOG_RETENTION_DAYS = 30

# =============================================================================
# 4. MFA Settings (TRD §4.2)
# =============================================================================
MFA_ENABLED = True
MFA_REQUIRED_FOR_ADMIN_ACTIONS = True