# Role-Based Access Control (RBAC) Documentation

## Demo User Accounts

### Family Members (family_member)
- **Alex** - Username: `alex`, Password: `family123`
- **Amanda** - Username: `amanda`, Password: `family123`

### Police Officers (police_officer)
- **Bernard** - Username: `bernard`, Password: `police456`
- **Betty** - Username: `betty`, Password: `police456`

### Government Officials (government_official)
- **Cate** - Username: `cate`, Password: `official789`
- **Dan** - Username: `dan`, Password: `official789`

---

## Access Control by Role

### Family Members
**Permissions:**
- ✅ Report missing persons
- ✅ Upload images for their own cases
- ✅ View only their own reports
- ❌ Cannot verify facial matches
- ❌ Cannot access other users' cases
- ❌ Cannot modify other users' cases

**Use Cases:**
- Report a missing family member
- Upload photos of the missing person
- Track the status of their own case
- Receive notifications about their case

---

### Police Officers
**Permissions:**
- ✅ Report missing persons
- ✅ Upload images for any case
- ✅ View all missing person cases
- ✅ Verify facial matches
- ✅ Reject false positive matches
- ✅ Access and modify all cases

**Use Cases:**
- Investigate missing person cases
- Access database of all missing persons
- Verify and validate facial matches
- Add investigation notes and evidence
- Collaborate on cases

---

### Government Officials
**Permissions:**
- ✅ Report missing persons
- ✅ Upload images for any case
- ✅ View all missing person cases
- ✅ Verify facial matches
- ✅ Reject false positive matches
- ✅ Access and modify all cases

**Use Cases:**
- Official government investigation support
- Access to nationwide missing person database
- Verify matches with government records
- Inter-agency collaboration
- Generate official reports

---

## API Endpoint Access Control

### Missing Persons (`/api/facial-recognition/missing-persons/`)

| Operation | Family Member | Police Officer | Government Official |
|-----------|--------------|-----------------|-------------------|
| Create | ✅ | ✅ | ✅ |
| List Own | ✅ | ✅ | ✅ |
| List All | ❌ | ✅ | ✅ |
| Retrieve Own | ✅ | ✅ | ✅ |
| Retrieve Other | ❌ | ✅ | ✅ |
| Update Own | ✅ | ✅ | ✅ |
| Update Other | ❌ | ✅ | ✅ |
| Delete Own | ❌ | ✅ | ✅ |
| Delete Other | ❌ | ✅ | ✅ |

### Facial Matches (`/api/facial-recognition/matches/`)

| Operation | Family Member | Police Officer | Government Official |
|-----------|--------------|-----------------|-------------------|
| List Own | ✅ | ✅ | ✅ |
| List All | ❌ | ✅ | ✅ |
| View Match | ✅ (Own) | ✅ (All) | ✅ (All) |
| Verify Match | ❌ | ✅ | ✅ |
| Reject Match | ❌ | ✅ | ✅ |

### Image Upload (`/api/facial-recognition/missing-persons/{id}/upload_image/`)

| Operation | Family Member | Police Officer | Government Official |
|-----------|--------------|-----------------|-------------------|
| Upload Own | ✅ | ✅ | ✅ |
| Upload Other | ❌ | ✅ | ✅ |

---

## How RBAC is Implemented

### Permission Classes (`users/permissions.py`)
- `IsFamilyMember` - Restricts to family member role
- `IsPoliceOfficer` - Restricts to police officer role
- `IsGovernmentOfficial` - Restricts to government official role
- `IsPoliceOrGovernment` - Allows police and government officials

### Role-Based Filters
Views automatically filter queryset based on user role:
```python
def get_queryset(self):
    user_perms = get_user_permissions(self.request.user)
    
    # Family members see only their own cases
    if not user_perms['can_access_all_cases']:
        return MissingPerson.objects.filter(reported_by=self.request.user)
    
    # Police/Government see all cases
    return MissingPerson.objects.all()
```

### Permission Checks on Actions
Sensitive actions like verifying matches check permissions:
```python
@action(detail=True, methods=['post'])
def verify(self, request, pk=None):
    user_perms = get_user_permissions(request.user)
    
    if not user_perms['can_verify_matches']:
        return Response(
            {'error': 'You do not have permission to verify matches.'},
            status=status.HTTP_403_FORBIDDEN
        )
```

---

## Testing the RBAC

### Test with Family Member (Alex)
```bash
curl -X POST http://localhost:8000/api/auth/token/ \
  -d "username=alex&password=family123"

# Will get access token
# Can create and view own cases
# Cannot verify matches or see other cases
```

### Test with Police Officer (Bernard)
```bash
curl -X POST http://localhost:8000/api/auth/token/ \
  -d "username=bernard&password=police456"

# Will get access token
# Can view all cases and verify matches
```

### Test with Government Official (Cate)
```bash
curl -X POST http://localhost:8000/api/auth/token/ \
  -d "username=cate&password=official789"

# Will get access token
# Can view all cases and verify matches
```

---

## Adding New Roles

To add a new role:

1. Update `User` model ROLE_CHOICES in `users/models.py`
2. Add role to `ROLE_PERMISSIONS` dictionary in `users/permissions.py`
3. Create permission class in `users/permissions.py` if needed
4. Update views to use the new permission class or role check

---

## Security Notes

1. **Always authenticate** - All endpoints except `/api/health/` require authentication
2. **Role is immutable** - Users cannot change their own role (enforced in serializers)
3. **Audit logging** - All sensitive operations are logged in `AuditLog` model
4. **Token expiry** - JWT tokens expire after 60 minutes for security
5. **HTTPS in production** - Always use HTTPS for authentication in production

