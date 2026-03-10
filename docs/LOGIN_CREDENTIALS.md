# SuraSmart Login Credentials

## Test User Account

**Username:** `testuser`
**Password:** `Test@123`
**Role:** Family Member

This is a verified test account ready for development and testing.

## Login Endpoint

**URL:** `http://localhost:8000/api/auth/token/`
**Method:** POST
**Content-Type:** application/json

### Request Body
```json
{
  "username": "testuser",
  "password": "Test@123"
}
```

### Successful Response (200 OK)
```json
{
  "refresh": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "access": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "user": {
    "id": 9,
    "username": "testuser",
    "email": "test@example.com",
    "first_name": "Test",
    "last_name": "User",
    "role": "family_member",
    "is_staff": false
  }
}
```

## Using the Token

Add the access token to request headers:
```
Authorization: Bearer <access_token>
```

## Creating Additional Test Users

To create more test users with different roles:

```bash
python manage.py shell
```

```python
from users.models import User

user = User.objects.create_user(
    username='police_test',
    email='police@example.com',
    password='Police@123',
    first_name='Police',
    last_name='Officer',
    role='police_officer',
    verification_status='verified',
    is_active_user=True
)
```

### Available Roles
- `family_member` - Report missing persons, upload images
- `police_officer` - Full search and verification capabilities
- `government_official` - Administrative and verification access
- `morgue_staff` - Database management for morgue records
- `admin` - System administrator access

## Troubleshooting

### "Bad Request" (400)
- Check username/password are correct
- Verify user is verified (verification_status='verified')
- Ensure user is active (is_active_user=True and is_active=True in Django)

### "No active account found"
- Username or password is incorrect
- User doesn't exist in the database

### "Account is not verified"
- Update user verification status to 'verified':
  ```python
  user = User.objects.get(username='username')
  user.verification_status = 'verified'
  user.save()
  ```

## Development Mode Notes

In DEBUG mode (development), users don't need to be verified to login - they just need to be active. In production, user verification will be required.
