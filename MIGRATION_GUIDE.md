# Migration Guide: From MVP Flask App to Phase 1 Backend

## Overview
This guide explains the architectural shift from the simple Flask MVP (`sura_smart/app.py`) to the enterprise-grade Django backend (`backend/`), and how to integrate them.

---

## Architecture Comparison

### MVP (Flask)
```
sura_smart/
├── app.py                    # Single file, all logic
├── templates/
│   ├── index.html           # Upload form
│   └── results.html         # Results display
├── static/
│   ├── db_images/           # Face database (file system)
│   ├── uploads/             # Temporary uploads
│   └── main.css, script.js
└── requirements.txt         # Flask, DeepFace only
```

**Limitations**:
- No database persistence
- Single-threaded processing
- No multi-user support
- No audit logging
- No scalability

### Phase 1 Backend (Django)
```
backend/
├── sura_smart_backend/      # Project config
├── users/                   # Auth & RBAC
├── facial_recognition/      # ML core
├── notifications/           # Alerts
├── database_integration/    # External DBs
├── docker-compose.yml       # Infrastructure
└── Dockerfile              # Production image
```

**Advantages**:
- PostgreSQL for persistence
- Async task processing (Celery)
- Multi-user with RBAC
- Immutable audit logs
- Kubernetes-ready
- RESTful API for mobile/web

---

## Migration Path

### Phase 1a: Keep MVP as Frontend
```
┌─────────────────────────────────────────┐
│  Web Frontend (React)                   │
│  Mobile App (React Native)              │
└──────────────┬──────────────────────────┘
               │ HTTP/JSON API
     ┌─────────▼──────────┐
     │ Phase 1 Backend    │
     │ Django + DRF       │
     │ REST API @ :8000   │
     └─────────┬──────────┘
               │
    ┌──────────┴──────────┬───────────────┐
    │                     │               │
┌───▼────┐          ┌────▼──┐      ┌─────▼────┐
│PostgreSQL         │ Redis │      │ Celery   │
└────────┘          └───────┘      └──────────┘
```

### Phase 1b: Transition Flask Frontend → React Web UI

**Step 1**: Deploy both simultaneously
- Keep MVP at `http://localhost:3001`
- New backend at `http://localhost:8000/api/`
- React frontend at `http://localhost:3000`

**Step 2**: Gradually replace endpoints
- Upload → POST `/api/facial-recognition/missing-persons/{id}/upload_image/`
- Search → GET `/api/facial-recognition/matches/?missing_person={id}`
- Results → Use returned FacialMatch objects

**Step 3**: Migrate data
```bash
# Export images from Flask
python sura_smart/export_images.py  # (to be created)

# Import to Django
python backend/manage.py import_missing_persons --source=export.json
```

---

## Integration Checklist

### ✅ Backend (Phase 1) - READY
- [x] Django project structure
- [x] PostgreSQL models
- [x] REST API endpoints
- [x] JWT authentication
- [x] Celery async tasks
- [x] Docker infrastructure
- [x] Health checks
- [x] RBAC framework

### 🔄 Frontend (MVP Flask) - TO BE REPLACED
- [ ] Replace with React web app
- [ ] Connect to `/api/auth/token/` for login
- [ ] Connect to `/api/facial-recognition/missing-persons/` for upload
- [ ] Connect to `/api/facial-recognition/matches/` for results
- [ ] Use `/api/notifications/` for alerts

### 🔄 Facial Recognition Pipeline - PARTIAL
- [ ] Complete DeepFace integration in Celery tasks
- [ ] Implement database image loading
- [ ] Add image preprocessing
- [ ] Implement result storage

### ❌ External Databases - PHASE 2
- [ ] Morgue database connector
- [ ] Jail database connector
- [ ] Police database connector
- [ ] Schema mappers
- [ ] Sync schedulers

---

## Deployment Scenarios

### Scenario 1: MVP Flask → Backend Transition (Development)
```bash
# Terminal 1: Run Flask MVP (keep for reference)
cd sura_smart/
python app.py  # Runs on :80

# Terminal 2: Run Django Backend
cd backend/
docker-compose up

# Terminal 3: Run React Frontend (to be built)
cd frontend/
npm start  # Runs on :3000
```

**Access**:
- MVP: http://localhost (port 80)
- Backend API: http://localhost:8000/api/
- Frontend: http://localhost:3000 (future)

### Scenario 2: Full Docker Deployment
```bash
# Update docker-compose.yml to include React
docker-compose up -d

# All services run together:
# - Backend: port 8000
# - Frontend: port 3000
# - PostgreSQL: port 5432
# - Redis: port 6379
```

### Scenario 3: Production Kubernetes
```bash
# Build Docker images
docker build -t sura-smart-backend:1.0 backend/
docker push <registry>/sura-smart-backend:1.0

# Deploy to Kubernetes (helm charts to be created)
kubectl apply -f k8s/
```

---

## Data Migration Strategy

### Step 1: Export MVP Data
Create `sura_smart/export_images.py`:
```python
import os
import json
from datetime import datetime

db_folder = 'static/db_images'
export_data = []

for filename in os.listdir(db_folder):
    if filename.endswith(('.png', '.jpg', '.jpeg')):
        export_data.append({
            'original_filename': filename,
            'local_path': f'static/db_images/{filename}',
            'uploaded_at': datetime.now().isoformat(),
            'status': 'imported'
        })

with open('export.json', 'w') as f:
    json.dump(export_data, f, indent=2)

print(f"Exported {len(export_data)} images")
```

### Step 2: Import to Django Backend
Create `backend/import_legacy_data.py`:
```python
import json
import os
from pathlib import Path
from django.core.files.base import ContentFile
from facial_recognition.models import MissingPerson, FacialRecognitionImage
from users.models import User

# Load exported data
with open('export.json') as f:
    data = json.load(f)

# Create admin user if needed
admin_user, _ = User.objects.get_or_create(
    username='admin',
    defaults={'role': 'admin', 'is_staff': True}
)

# Import each image
for item in data:
    # Create missing person record
    missing_person, created = MissingPerson.objects.get_or_create(
        full_name=item['original_filename'].split('.')[0],
        defaults={
            'reported_by': admin_user,
            'status': 'searching'
        }
    )
    
    # Copy image file
    source_path = Path(item['local_path'])
    if source_path.exists():
        with open(source_path, 'rb') as img:
            facial_image = FacialRecognitionImage.objects.create(
                missing_person=missing_person,
                image_file=ContentFile(img.read(), name=item['original_filename']),
                is_primary=True
            )
```

Run import:
```bash
cd backend
python manage.py shell < import_legacy_data.py
```

---

## API Endpoint Mapping

### Upload Image
**Flask MVP** (single file, file system):
```bash
POST / (submit HTML form)
```

**Django Backend** (REST API):
```bash
# 1. Create missing person
POST /api/facial-recognition/missing-persons/
{
  "full_name": "John Doe",
  "description": "Missing since Jan 1",
  "status": "reported"
}
# Response: {"id": "uuid-123", ...}

# 2. Upload image
POST /api/facial-recognition/missing-persons/uuid-123/upload_image/
{
  "image": <file>,
  "priority": "high"
}
# Response: {"id": "image-uuid", "status": "uploaded", ...}
```

### Get Results
**Flask MVP**:
```python
# Inline in Flask route
matches = []
for db_image in db_images:
    result = DeepFace.verify(uploaded_image, db_image)
    if result['verified']:
        matches.append((name, result['distance']))
```

**Django Backend**:
```bash
# 1. Image is queued for processing
# 2. Celery worker processes async:
celery_task = process_facial_recognition(image_id)

# 3. Poll for results
GET /api/facial-recognition/matches/?missing_person=uuid-123

# Response:
{
  "count": 2,
  "results": [
    {
      "id": "match-1",
      "match_confidence": 0.98,
      "status": "verified",
      "verified_by": "officer1"
    }
  ]
}
```

---

## MVP Flask App - Keep or Deprecate?

### Option 1: Keep for Reference (Recommended)
- Store in separate `legacy/` folder
- Document what it did
- Use for comparison/migration testing
- Delete after frontend migration complete

### Option 2: Deprecate Immediately
- Delete `sura_smart/` folder
- Move all documentation to `backend/README.md`
- Focus team on new backend API

### Option 3: Run in Parallel
- Keep MVP on port 80 (internal use)
- Backend API on port 8000 (new development)
- Eventually deprecate Flask when React frontend ready

---

## Validation Checklist

### Backend Ready?
- [ ] PostgreSQL data persists across restarts
- [ ] Celery tasks execute and complete
- [ ] Health check returns OK
- [ ] JWT authentication works
- [ ] Upload endpoint queues images
- [ ] Match results stored in database
- [ ] Audit logs record all actions

### Frontend Ready?
- [ ] React web app deployed
- [ ] Login works with JWT tokens
- [ ] Upload form submits to backend API
- [ ] Results display from database
- [ ] Notifications appear in real-time

### Data Ready?
- [ ] Legacy images imported to PostgreSQL
- [ ] Legacy missing persons records migrated
- [ ] File system references updated to database
- [ ] No data loss confirmed

---

## Next Steps

1. **Build React Frontend**: Connect to backend API endpoints
2. **Complete Facial Recognition Pipeline**: Finish DeepFace integration in Celery
3. **Implement External Databases**: Add morgue/jail/police connectors
4. **Mobile App**: Build React Native version
5. **Deployment**: Set up CI/CD and production infrastructure
6. **Remove MVP**: Delete `sura_smart/app.py` after migration complete

---

## Troubleshooting Migration

### Issue: Images not found after migration
```bash
# Verify images imported
docker-compose exec backend python manage.py shell
>>> from facial_recognition.models import FacialRecognitionImage
>>> FacialRecognitionImage.objects.count()
```

### Issue: Old Flask API calls fail
**Solution**: Update frontend to use new endpoints:
- `/upload` → `POST /api/facial-recognition/missing-persons/{id}/upload_image/`
- `/` (form) → React component connecting to backend

### Issue: Celery tasks not processing
```bash
# Check Celery worker logs
docker-compose logs celery

# Verify Redis connection
docker-compose exec redis redis-cli ping
```

---

## Questions?

See backend/README.md for full documentation.
