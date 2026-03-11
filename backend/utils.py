from django.core import signing
from django.conf import settings
from django.utils import timezone

def generate_login_token(user_id):
    """Generates a signed token with 10-minute expiry"""
    return signing.dumps(user_id, salt='login-token', max_age=600) # 600 seconds = 10 mins

def verify_login_token(token):
    """Verifies token and checks expiry"""
    try:
        user_id = signing.loads(token, salt='login-token', max_age=600)
        return user_id
    except signing.SignatureExpired:
        raise Exception("Token has expired (10 minute limit).")
    except signing.BadSignature:
        raise Exception("Invalid token.")