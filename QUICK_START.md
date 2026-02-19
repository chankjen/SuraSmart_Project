# SuraSmart - Quick Reference Card

## 🔑 Login Credentials

```
Username: testuser
Password: Test@123
```

## 🌐 Access URLs

| Service | URL | Status |
|---------|-----|--------|
| Frontend | http://localhost:3000 | ✅ Running |
| Backend API | http://localhost:8000 | ✅ Running |
| Admin Panel | http://localhost:8000/admin | ✅ Running |
| API Docs | http://localhost:8000/api/ | ✅ Running |

## 🚀 Quick Start

### Terminal 1 - Backend
```bash
cd backend
env\Scripts\python.exe manage.py runserver
```

### Terminal 2 - Frontend
```bash
cd frontend
npm start
```

### Terminal 3 - Database (Optional)
```bash
# If using PostgreSQL Docker
docker-compose up -d
```

## 🧪 Testing Login

### Via Frontend
1. Go to http://localhost:3000
2. Enter credentials above
3. Click Login

### Via API (Using PowerShell)
```powershell
$body = @{username="testuser"; password="Test@123"} | ConvertTo-Json
Invoke-WebRequest -Uri "http://localhost:8000/api/auth/token/" `
  -Method Post -ContentType "application/json" -Body $body
```

### Via curl
```bash
curl -X POST http://localhost:8000/api/auth/token/ \
  -H "Content-Type: application/json" \
  -d '{"username":"testuser","password":"Test@123"}'
```

## 👥 Available Roles

| Role | Permissions |
|------|-----------|
| **Family Member** | Report missing, upload images, view own cases |
| **Police Officer** | Full access, verify matches, manage all cases |
| **Government Official** | Administrative access, verify matches |
| **Morgue Staff** | Database management, record updates |
| **Admin** | Full system access, user management |

## 📝 Create Test Users

```bash
python manage.py shell
```

```python
from users.models import User

User.objects.create_user(
    username='officer_test',
    password='Officer@123',
    email='officer@example.com',
    role='police_officer',
    verification_status='verified',
    is_active_user=True
)
```

## 🔍 Common Tasks

### Check if servers are running
```bash
netstat -ano | findstr :8000  # Backend
netstat -ano | findstr :3000  # Frontend
```

### View database users
```bash
python manage.py shell -c "from users.models import User; User.objects.all().values()"
```

### Reset database
```bash
# Delete old database
rm data/db.sqlite3

# Create new one
python manage.py migrate
```

### Run migrations
```bash
python manage.py makemigrations
python manage.py migrate
```

## ⚠️ Troubleshooting

| Problem | Solution |
|---------|----------|
| Login fails | Hard refresh (Ctrl+F5), clear browser cache |
| Backend not found | Check port 8000: `netstat -ano \| findstr :8000` |
| Frontend not loading | Verify npm running on port 3000 |
| Database errors | Run migrations: `python manage.py migrate` |
| "Bad Request" | Ensure user is verified in database |

## 📚 Key Files

| File | Purpose |
|------|---------|
| `backend/users/serializers.py` | Login serializer logic |
| `backend/users/views.py` | User API endpoints |
| `backend/users/models.py` | User data model |
| `frontend/src/pages/Login.js` | Login UI component |
| `frontend/.env` | Frontend configuration |

## 🔐 Security Notes

- **Development Mode**: Verification requirements relaxed for testing
- **Production Mode**: Strict verification required
- **Passwords**: Hashed with PBKDF2, never stored as plain text
- **Tokens**: JWT with 1-hour expiration
- **Data**: Isolated per user/role

## 🎯 Next Steps

1. Login to frontend
2. Create a missing person report
3. Upload facial recognition images
4. Perform a search
5. Test match verification
6. Try different user roles

## 🆘 Support

Check these files for more info:
- `LOGIN_CREDENTIALS.md` - Detailed credential info
- `LOGIN_FIX_SUMMARY.md` - What was fixed and why
- `LOGIN_TEST_REPORT.md` - Full test results
- `README.md` - Architecture overview

---

**Status:** ✅ **FULLY OPERATIONAL**
**Last Updated:** February 19, 2026
