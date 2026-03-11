# SuraSmart Backend - Phase 1 Infrastructure

## Overview

This is the Phase 1 backend implementation of SuraSmart - an AI-powered missing persons search platform. It establishes the core infrastructure for facial recognition, database integration, and notification systems as outlined in the TRD.

**Phase 1 Focus**: Enterprise-grade backend foundation with REST APIs, microservices architecture, PostgreSQL, Redis, and Celery async processing.

---

## Architecture

### Stack Overview
- **Framework**: Django 4.2 + Django REST Framework
- **Database**: PostgreSQL 15 + TimescaleDB (for time-series data in Phase 2)
- **Cache/Queue**: Redis 7 + Celery 5 (async task processing)
- **Authentication**: JWT (djangorestframework-simplejwt)
- **Deployment**: Gunicorn + Docker + Docker Compose
- **ML/AI**: DeepFace, TensorFlow, PyTorch (integrated for future expansion)

### Application Structure
```
backend/
├── sura_smart_backend/     # Django project config
│   ├── settings.py         # All configurations (DB, Redis, Celery, etc.)
│   ├── urls.py             # Root URL routing
│   ├── wsgi.py             # WSGI for deployment
│   ├── celery.py           # Celery configuration
│   └── admin.py            # Django admin customization
├── users/                  # Authentication & RBAC
├── facial_recognition/     # Core ML functionality
├── notifications/          # Real-time alerts
├── database_integration/   # External DB connectors
├── shared/                 # Health checks & utilities
├── docker-compose.yml      # Local development environment
├── Dockerfile              # Production image
├── requirements-backend.txt # Python dependencies
├── .env.example            # Configuration template
└── manage.py               # Django CLI
```

### Core Apps

#### Users (Authentication & RBAC)
- **Models**: `User` (custom, role-based), `AuditLog`, `Permission`
- **Roles**: Family Member, Police Officer, Government Official, Morgue Staff, Admin
- **Features**: 
  - JWT authentication (access + refresh tokens)
  - Immutable audit logs for compliance
  - Permission model ready for granular RBAC
  - User verification workflow

#### Facial Recognition (ML Core)
- **Models**: `MissingPerson`, `FacialRecognitionImage`, `FacialMatch`, `ProcessingQueue`
- **Features**:
  - Store missing person reports with metadata
  - Queue image processing with priority levels
  - Store match results with confidence scores
  - Blockchain placeholder fields for Phase 2
  - Async task processing via Celery

#### Notifications
- **Models**: `Notification`, `NotificationPreference`
- **Channels**: Email, SMS, Push (framework ready)
- **Features**:
  - Real-time alerts when matches found
  - User preference management (digest frequency, quiet hours)
  - Queued delivery via Celery

#### Database Integration (External Connections)
- **Models**: `ExternalDatabase`, `DatabaseSchema`, `SyncLog`, `QueryLog`
- **Features**:
  - Configuration for morgue/jail/police databases
  - Schema mapping for different data formats
  - Sync and query logging for audit trails
  - Rate limiting and retry logic ready for Phase 2

---

## Getting Started

### Prerequisites
- Docker & Docker Compose (recommended)
- OR: Python 3.11+, PostgreSQL 15, Redis 7

### Option 1: Docker (Recommended for Development)

1. **Clone the repository**
   ```bash
   cd backend
   ```

2. **Start services**
   ```bash
   docker-compose up -d
   ```
   This starts:
   - PostgreSQL (port 5432)
   - Redis (port 6379)
   - Django backend (port 8000)
   - Celery worker
   - Celery Beat scheduler

3. **Create superuser**
   ```bash
   docker-compose exec backend python manage.py createsuperuser
   ```

4. **Access the application**
   - API: http://localhost:8000/api/
   - Admin: http://localhost:8000/admin/
   - Health Check: http://localhost:8000/api/health/check/

### Option 2: Local Development

1. **Setup virtual environment**
   ```bash
   python -m venv venv
   source venv/Scripts/activate  # Windows
   source venv/bin/activate       # Linux/Mac
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements-backend.txt
   ```

3. **Configure environment**
   ```bash
   cp .env.example .env
   # Edit .env with your database credentials
   ```

4. **Setup PostgreSQL**
   ```bash
   createdb sura_smart
   ```

5. **Run migrations**
   ```bash
   python manage.py migrate
   ```

6. **Create superuser**
   ```bash
   python manage.py createsuperuser
   ```

7. **Start development server**
   ```bash
   python manage.py runserver
   ```

8. **Start Celery (in another terminal)**
   ```bash
   celery -A sura_smart_backend worker -l info
   celery -A sura_smart_backend beat -l info
   ```

---

## API Endpoints (Phase 1)

### Authentication
- `POST /api/auth/token/` - Obtain JWT tokens
- `POST /api/auth/token/refresh/` - Refresh access token
- `GET /api/auth/users/me/` - Get current user profile
- `POST /api/auth/users/change_password/` - Change password

### Missing Persons & Facial Recognition
- `GET/POST /api/facial-recognition/missing-persons/` - List/create missing person records
- `POST /api/facial-recognition/missing-persons/{id}/upload_image/` - Upload facial image
- `GET/POST /api/facial-recognition/images/` - Manage facial recognition images
- `GET /api/facial-recognition/matches/` - View facial match results
- `POST /api/facial-recognition/matches/{id}/verify/` - Verify a match
- `POST /api/facial-recognition/matches/{id}/reject/` - Reject a match
- `GET /api/facial-recognition/processing-queue/` - Monitor processing queue

### Notifications
- `GET /api/notifications/notifications/` - List notifications
- `POST /api/notifications/notifications/{id}/mark_as_read/` - Mark as read
- `POST /api/notifications/notifications/mark_all_as_read/` - Mark all as read
- `GET/PUT /api/notifications/preferences/my_preferences/` - Notification preferences

### Database Integration (Phase 2)
- `GET/POST /api/database/external-databases/` - External database configuration
- `GET/POST /api/database/schemas/` - Schema mapping
- `GET /api/database/sync-logs/` - Sync operation history
- `GET /api/database/query-logs/` - Query history

### Health & Status
- `GET /api/health/check/` - Health check (database, cache, Celery)
- `GET /api/health/status/` - API status

---

## Database Schema Highlights

### Key Models
- **User**: Custom user with roles (family_member, police_officer, government_official, morgue_staff, admin)
- **AuditLog**: Immutable audit trail for compliance (blockchain-ready placeholder)
- **MissingPerson**: Core missing person report with metadata
- **FacialRecognitionImage**: Uploaded images with processing status
- **FacialMatch**: Match results with confidence scores and verification workflow
- **ProcessingQueue**: Async task queue with priority levels
- **ExternalDatabase**: Configuration for government database integrations
- **Notification**: Real-time alerts with multi-channel support

### Database Features
- **Indexes**: Optimized for common queries (user, timestamp, status)
- **JSON Fields**: Flexible metadata storage (face_embedding, custom_mappings)
- **UUIDs**: Primary keys for distributed systems
- **Timestamps**: Auto-tracked created/updated times
- **Audit Fields**: User tracking and blockchain hash placeholders

---

## Configuration

### Environment Variables (see `.env.example`)
```bash
# Server
DEBUG=True
SECRET_KEY=your-secret-key

# Database
DB_ENGINE=django.db.backends.postgresql
DB_NAME=sura_smart
DB_HOST=localhost
DB_PORT=5432

# Redis & Celery
REDIS_URL=redis://127.0.0.1:6379/1
CELERY_BROKER_URL=redis://127.0.0.1:6379/0

# Features (Phase 2)
BLOCKCHAIN_ENABLED=False
MULTIMODAL_RECOGNITION_ENABLED=False

# API Configuration
ALLOWED_HOSTS=localhost,127.0.0.1
CORS_ALLOWED_ORIGINS=http://localhost:3000
```

---

## Development Workflow

### Creating New API Endpoints
1. Define models in `app/models.py`
2. Create serializers in `app/serializers.py`
3. Create viewsets in `app/views.py`
4. Register routes in `app/urls.py`
5. Register in admin at `sura_smart_backend/admin.py`

### Running Migrations
```bash
python manage.py makemigrations
python manage.py migrate
```

### Testing
```bash
pytest                           # Run all tests
pytest --cov=.                  # With coverage
pytest facial_recognition/      # Specific app
```

### Code Quality
```bash
black .                  # Format code
flake8 .               # Lint
isort .                # Sort imports
```

### Database Backups
```bash
# Export
pg_dump -U postgres sura_smart > backup.sql

# Import
psql -U postgres sura_smart < backup.sql
```

---

## Async Tasks (Celery)

### Built-in Tasks
- `process_facial_recognition`: Process uploaded images (placeholder for Phase 1)
- `cleanup_old_uploads`: Daily cleanup of old images (runs at 2 AM)
- `sync_external_databases`: Periodic sync with government databases (Phase 2)

### Adding New Tasks
Create in `app/tasks.py`:
```python
from celery import shared_task

@shared_task
def my_task(param):
    # Task logic here
    pass
```

Queue from views:
```python
from app.tasks import my_task
my_task.delay(param)
```

---

## Monitoring & Debugging

### Health Checks
```bash
curl http://localhost:8000/api/health/check/
```

### Logs
```bash
# Backend logs
docker-compose logs backend

# Celery logs
docker-compose logs celery

# Follow logs in real-time
docker-compose logs -f backend
```

### Database Access
```bash
docker-compose exec postgres psql -U postgres sura_smart
```

### Celery Monitoring
```bash
# Install Flower (Celery UI)
pip install flower
celery -A sura_smart_backend flower

# Access at http://localhost:5555
```

---

## Phase 1 Roadmap & Phase 2 Preparation

### ✅ Implemented in Phase 1
- Django REST framework with JWT auth
- PostgreSQL + Redis infrastructure
- RBAC with Permission model
- Immutable audit logging (blockchain-ready)
- Async task processing (Celery)
- External database schema (Phase 2)
- Notification framework (Phase 2)
- Health check endpoints

### 🔄 Phase 2 (Partial Implementation Ready)
- Government database integrations (morgue, jail, police)
- DeepFace processing workflow completion
- Multimodal recognition (voice, biometrics)
- Blockchain audit trail implementation
- Mobile app API endpoints
- Multilingual support (i18n framework ready)
- Advanced RBAC enforcement
- Edge node integration

### ❌ Phase 3+ (Architecture Prepared)
- Mobile apps (React Native)
- Microservices expansion
- Kubernetes orchestration
- Cloud deployment (AWS/GCP)
- Advanced ML models
- Blockchain network setup

---

## Security Considerations

### Authentication
- JWT tokens with 1-hour expiration (configurable)
- Refresh token rotation enabled
- Password validation enforced

### Data Protection
- CORS enabled for frontend domains only
- CSRF protection active
- SSL/TLS ready (set `SECURE_SSL_REDIRECT=True` in production)
- Sensitive fields (passwords, API keys) encrypted

### Audit & Compliance
- All user actions logged (AuditLog model)
- Blockchain hash fields ready (Phase 2)
- GDPR-ready user deletion workflow (Phase 2)

### Production Deployment
- Change `SECRET_KEY` to strong random value
- Set `DEBUG=False`
- Enable `SECURE_SSL_REDIRECT`
- Use strong database passwords
- Secure Redis with AUTH
- Use environment-specific `.env` files

---

## Troubleshooting

### Database Connection Error
```bash
# Check PostgreSQL is running
docker-compose ps
docker-compose logs postgres

# Verify credentials in .env
```

### Celery Not Processing Tasks
```bash
# Check Celery worker is running
docker-compose logs celery

# Check Redis connection
redis-cli ping
```

### Migration Errors
```bash
# Create new migration
python manage.py makemigrations

# Apply migrations
python manage.py migrate

# Rollback migration
python manage.py migrate app_name XXXX
```

---

## Next Steps

1. **Frontend Development**: Build React web app connecting to `/api/` endpoints
2. **Mobile Apps**: Create React Native apps using same API
3. **External Database Integration**: Implement morgue/jail/police API connectors
4. **ML Pipeline**: Complete DeepFace integration and training
5. **Blockchain Setup**: Implement audit trail on permissioned blockchain
6. **Deployment**: Set up CI/CD pipeline and cloud infrastructure

---

## Support & Documentation

- Django Docs: https://docs.djangoproject.com/
- DRF Docs: https://www.django-rest-framework.org/
- Celery Docs: https://docs.celeryproject.org/
- PostgreSQL Docs: https://www.postgresql.org/docs/

---

## License

Proprietary - SuraSmart Project
