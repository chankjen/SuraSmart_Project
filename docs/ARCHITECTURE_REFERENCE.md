# SuraSmart Architecture Diagrams & Technical Reference

## Phase 1: Current Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                     Client Applications                         │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │ React Web (3000)  │ React Native (mobile) │ CLI / Scripts │  │
│  └────────────────────────────┬─────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────┘
                                 │
                      ┌──────────▼──────────┐
                      │  HTTP/JSON (REST)  │
                      │   JWT Auth         │
                      │  CORS Enabled      │
                      └──────────┬──────────┘
                                 │
    ┌────────────────────────────▼────────────────────────────┐
    │           Phase 1: Django REST API (8000)              │
    │                                                         │
    │  ┌─────────────┐  ┌──────────────────┐  ┌────────────┐ │
    │  │   Users     │  │  Facial Recog.   │  │Notifs      │ │
    │  │   (Auth &   │  │  (ML Core)       │  │ (Alerts)   │ │
    │  │   RBAC)     │  │                  │  │            │ │
    │  │             │  │  DB Integration  │  │            │ │
    │  │ 5 Endpoints │  │  (External DBs)  │  │ 4 Endpoints│ │
    │  └──────┬──────┘  └─────────┬────────┘  └──────┬─────┘ │
    │         │                   │                  │       │
    │  ┌──────┴───────────────────┴──────────────────┴──────┐ │
    │  │           Shared Services                          │ │
    │  │  - Health Checks  - Admin Interface               │ │
    │  │  - Logging        - Error Handling                │ │
    │  └──────────────────────────────────────────────────┘ │
    │                                                         │
    └─────────────────────────┬──────────────────────────────┘
                              │
        ┌─────────────────────┼─────────────────────┐
        │                     │                     │
    ┌───▼────┐          ┌─────▼─────┐          ┌──▼─────┐
    │         │          │           │          │        │
  ┌─▼───────┐│          │           │          │        │
  │PostgreSQL││  ┌───────▼────┐  ┌──▼────────┐│        │
  │ (5432)   ││  │   Redis    │  │  Celery  ││   Other
  │          ││  │  (6379)    │  │ Worker   ││  Services
  │ Models:  ││  │            │  │          ││   (Phase 2)
  │ - User   ││  │ - Cache    │  │ Tasks:   ││
  │ - Audit  ││  │ - Session  │  │ - Facial ││
  │ - Match  ││  │ - Queue    │  │   Recog. ││
  │ - Notif  ││  │            │  │ - Cleanup││
  │ - ExtDB  ││  └────────────┘  │ - Sync   ││
  └─────────┘│                   │          ││
  14 Models  │   ┌─────────────┐ │          ││
             │   │Celery Beat  │ │  ┌───────▼┘
             │   │(Scheduler)  │ │  │
             │   │ 2 AM        │ │  │
             │   │ Cleanup     │ │  │
             │   └─────────────┘ │  │
             │                   │  │
             │   ┌───────────────┴──▼───┐
             │   │  Message Queue       │
             │   │  (Redis)             │
             │   └──────────────────────┘
             │
             └────────┬────────────┐
                      │            │
                  Docker Compose   │
                  (5 Services)     │
                      │            │
                      ▼            ▼
             ┌─────────────────────────────┐
             │   Development Environment   │
             │   (All Services Local)      │
             └─────────────────────────────┘
```

---

## Phase 2: Expansion (External Databases & Blockchain)

```
    ┌──────────────────────────────────────────────────────┐
    │            Government Databases                      │
    │  ┌──────────────┐  ┌──────────────┐  ┌────────────┐ │
    │  │  Morgue DB   │  │  Jail DB     │  │ Police DB  │ │
    │  │  (REST API)  │  │  (SOAP API)  │  │ (Direct)   │ │
    │  └────────┬─────┘  └──────┬───────┘  └──────┬─────┘ │
    └───────────┼─────────────────┼────────────────┼────────┘
                │                 │                │
    ┌───────────▼─────────────────▼────────────────▼────────┐
    │      Database Integration Layer (Phase 2)            │
    │  ┌──────────────────────────────────────────────┐    │
    │  │ External Database Connector                 │    │
    │  │ - API Handlers (REST/SOAP)                 │    │
    │  │ - Schema Mappers                            │    │
    │  │ - Query Builders                            │    │
    │  │ - Rate Limiting & Retry Logic              │    │
    │  └──────────────────────────────────────────────┘    │
    └───────────────────────┬──────────────────────────────┘
                            │
                ┌───────────▼──────────────┐
                │   SyncLog & QueryLog     │
                │   (Audit Trail)          │
                └───────────┬──────────────┘
                            │
            ┌───────────────▼───────────────┐
            │  Blockchain Network (Phase 2) │
            │  (Permissioned)               │
            │  - Audit Verification        │
            │  - Immutable Records         │
            │  - Access Control            │
            └───────────────────────────────┘
```

---

## Data Flow: Image Upload to Match

```
Step 1: User uploads image
┌──────────────────────────────────┐
│ POST /api/facial-recognition/    │
│ missing-persons/{id}/upload_image/
└────────────┬─────────────────────┘
             │
             ▼
┌──────────────────────────────────┐
│ Django REST View                 │
│ - Validate JWT token             │
│ - Check permissions              │
│ - Create FacialRecognitionImage  │
│ - Create ProcessingQueue entry   │
└────────────┬─────────────────────┘
             │
Step 2: Queue for processing
             ▼
┌──────────────────────────────────┐
│ Redis Message Queue              │
│ (via Celery)                     │
└────────────┬─────────────────────┘
             │
Step 3: Async processing
             ▼
┌──────────────────────────────────┐
│ Celery Worker Task:              │
│ process_facial_recognition()     │
│ - Load image from disk           │
│ - Extract facial features        │
│ - Compare against database       │
│ - Store FacialMatch results      │
│ - Update ProcessingQueue status  │
└────────────┬─────────────────────┘
             │
Step 4: Results available
             ▼
┌──────────────────────────────────┐
│ GET /api/facial-recognition/     │
│ matches/?missing_person={id}     │
│                                  │
│ Returns: FacialMatch objects     │
│ with confidence scores           │
└────────────┬─────────────────────┘
             │
Step 5: Verification
             ▼
┌──────────────────────────────────┐
│ POST /api/facial-recognition/    │
│ matches/{id}/verify/             │
│                                  │
│ - Officer reviews match          │
│ - Marks as verified/false_pos.   │
│ - Adds verification notes        │
│ - Triggers notification          │
└────────────┬─────────────────────┘
             │
Step 6: Notification sent
             ▼
┌──────────────────────────────────┐
│ POST /api/notifications/         │
│ (via Celery task)                │
│                                  │
│ - Create Notification object     │
│ - Send via email/SMS/push        │
│ - Log in AuditLog                │
└──────────────────────────────────┘
```

---

## Database Schema (Simplified)

```
USERS SYSTEM:
┌─────────────────────────────────────────────┐
│ User                                        │
│ - id (PK)                                   │
│ - username (unique)                         │
│ - password (hashed)                         │
│ - role: {family, police, official, ...}    │
│ - verification_status                      │
│ - created_at, updated_at                   │
└────────┬──────────────────────────────────┬─┘
         │                                  │
         │ 1:N                        1:N   │
         ▼                                  ▼
    ┌─────────────┐              ┌──────────────────┐
    │ AuditLog    │              │ Permission       │
    │ - action    │              │ - resource       │
    │ - timestamp │              │ - can_read       │
    │ - ip_addr   │              │ - can_write      │
    │ - metadata  │              │ - can_delete     │
    └─────────────┘              └──────────────────┘


FACIAL RECOGNITION:
┌──────────────────────────────────────────────┐
│ MissingPerson (Core)                         │
│ - id (UUID)                                  │
│ - full_name                                  │
│ - status: {reported, searching, found, ...} │
│ - reported_by (FK → User)                    │
│ - date_reported                              │
│ - last_seen_location                         │
│ - created_at, updated_at                     │
└────┬──────────────────────────────────────┬──┘
     │ 1:N                            1:N   │
     ▼                                      ▼
┌──────────────────────┐      ┌────────────────────┐
│FacialRecognitionImage│      │ FacialMatch        │
│ - id (UUID)          │      │ - id (UUID)        │
│ - image_file (blob)  │      │ - confidence       │
│ - status: {uploaded, │      │ - distance_metric  │
│   processing, ...}   │      │ - status: {pending,│
│ - face_embedding     │      │   verified, ...}   │
│ - processed_at       │      │ - verified_by (FK) │
└──────────┬───────────┘      │ - blockchain_hash  │
           │                  └────────────────────┘
           │
           │ 1:1
           ▼
      ┌──────────────────┐
      │ProcessingQueue   │
      │ - status         │
      │ - priority       │
      │ - retries        │
      │ - started_at     │
      │ - error_message  │
      └──────────────────┘


NOTIFICATIONS:
┌────────────────────────────────┐
│ Notification                   │
│ - recipient (FK → User)        │
│ - type: {match_found, alert..} │
│ - status: {pending, sent, ...} │
│ - created_at                   │
└────┬──────────────────────┬────┘
     │ 1:1                  │ 1:1
     ▼                      ▼
┌─────────────────────┐  ┌──────────────────────┐
│NotificationPref     │  │ (via Celery Tasks)   │
│ - user              │  │ - email              │
│ - digest_frequency  │  │ - sms                │
│ - quiet_hours       │  │ - push notifications │
└─────────────────────┘  └──────────────────────┘


DATABASE INTEGRATION:
┌──────────────────────────────┐
│ ExternalDatabase             │
│ - name                       │
│ - type: {morgue, jail, ...}  │
│ - endpoint_url               │
│ - api_key / credentials      │
│ - is_active                  │
│ - rate_limit                 │
└────┬──────────────────────┬──┘
     │ 1:N                  │ 1:N
     ▼                      ▼
┌──────────────────┐   ┌──────────────┐
│ DatabaseSchema   │   │ SyncLog      │
│ - field_mappings │   │ - status     │
│ - custom_mapping │   │ - records_   │
└──────────────────┘   │   synced     │
                       │ - started_at │
                       └──────────────┘
                       
                       1:N
                       │
                       ▼
                  ┌──────────────┐
                  │ QueryLog     │
                  │ - query_type │
                  │ - response_  │
                  │   time_ms    │
                  │ - error_msg  │
                  └──────────────┘
```

---

## API Response Example

### Create Missing Person & Upload Image

```
Request:
POST /api/facial-recognition/missing-persons/
Authorization: Bearer <jwt_token>
Content-Type: application/json

{
  "full_name": "John Doe",
  "description": "Missing since January 1",
  "age": 35,
  "gender": "male",
  "last_seen_location": "Downtown Area",
  "status": "reported"
}

Response (201 Created):
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "reported_by": "family_member_id",
  "full_name": "John Doe",
  "description": "Missing since January 1",
  "status": "reported",
  "age": 35,
  "gender": "male",
  "last_seen_location": "Downtown Area",
  "match_count": 0,
  "created_at": "2026-02-02T10:00:00Z",
  "updated_at": "2026-02-02T10:00:00Z"
}


Request:
POST /api/facial-recognition/missing-persons/550e8400-e29b-41d4-a716-446655440000/upload_image/
Authorization: Bearer <jwt_token>
Content-Type: multipart/form-data

image: <binary_image_file>
priority: "high"

Response (201 Created):
{
  "id": "660f9511-f3ac-52e5-b827-557766551111",
  "missing_person": "550e8400-e29b-41d4-a716-446655440000",
  "image_file": "/media/facial_recognition/2026/02/02/john_doe.jpg",
  "is_primary": false,
  "status": "uploaded",
  "face_confidence": null,
  "created_at": "2026-02-02T10:05:00Z"
}


Request:
GET /api/facial-recognition/processing-queue/?status=processing

Response (200 OK):
{
  "count": 1,
  "next": null,
  "previous": null,
  "results": [
    {
      "id": "770g0722-g4bd-63f6-c938-668877662222",
      "image": "660f9511-f3ac-52e5-b827-557766551111",
      "priority": "high",
      "status": "processing",
      "retries": 0,
      "started_at": "2026-02-02T10:05:05Z",
      "completed_at": null
    }
  ]
}


Request:
GET /api/facial-recognition/matches/?missing_person=550e8400-e29b-41d4-a716-446655440000

Response (200 OK):
{
  "count": 2,
  "next": null,
  "previous": null,
  "results": [
    {
      "id": "880h1833-h5ce-74g7-d049-779988773333",
      "missing_person": "550e8400-e29b-41d4-a716-446655440000",
      "missing_person_name": "John Doe",
      "match_confidence": 0.985,
      "distance_metric": 0.42,
      "source_database": "morgue",
      "status": "verified",
      "verified_by": "officer_id",
      "verified_at": "2026-02-02T10:10:00Z",
      "verification_notes": "Confirmed by visual inspection",
      "created_at": "2026-02-02T10:07:00Z"
    }
  ]
}
```

---

## Authentication Flow

```
1. Client Login
   POST /api/auth/token/
   {"username": "user", "password": "pass"}
   ↓
2. Backend Returns Tokens
   {
     "access": "eyJhbGc...",  (1 hour)
     "refresh": "eyJhbGc..."  (7 days)
   }
   ↓
3. Client stores tokens (localStorage, cookies, etc.)
   ↓
4. Client makes API request
   GET /api/facial-recognition/missing-persons/
   Headers: Authorization: Bearer eyJhbGc...
   ↓
5. Django verifies JWT signature
   ↓
6. If valid: Execute endpoint
   If expired: Return 401 Unauthorized
   ↓
7. Client can refresh:
   POST /api/auth/token/refresh/
   {"refresh": "eyJhbGc..."}
   ↓
8. Backend returns new access token
   {"access": "new-token-eyJhbGc..."}
```

---

## Deployment Architecture

```
PRODUCTION DEPLOYMENT:

┌─────────────────────────────────────────────────┐
│            Kubernetes Cluster (Phase 3)         │
│  (Or Docker Swarm / EC2 fleet for Phase 1)      │
└──────────────────┬──────────────────────────────┘
                   │
    ┌──────────────┼──────────────┐
    │              │              │
    ▼              ▼              ▼
 ┌─────┐      ┌─────────┐      ┌──────┐
 │Pods │ ─2n  │Pods     │ ─2n  │Pods  │
 │     │      │         │      │      │
 │  +  │  +   │   +     │  +   │  +   │
 │Django       │ Celery  │      │Config
 │Backend      │ Workers │      │ &    │
 │Replicas     │         │      │Logs  │
 └─────┘      └─────────┘      └──────┘
    │              │              │
    └──────────────┼──────────────┘
                   │
    ┌──────────────┼──────────────┐
    │              │              │
    ▼              ▼              ▼
 ┌─────────┐  ┌────────┐      ┌──────────┐
 │PostgreSQL  │ Redis  │      │ S3/Blob  │
 │ StatefulSet│Cluster │      │ Storage  │
 │(Persistent│        │      │(for imgs)│
 │ Volumes) │        │      │          │
 └─────────┘  └────────┘      └──────────┘
    │              │              │
    └──────────────┼──────────────┘
                   │
              ┌────▼────┐
              │   CDN   │
              │ (images)│
              └─────────┘
              
Frontend: React @ CDN
Mobile: React Native
```

---

## Status: ✅ Complete

All diagrams represent current Phase 1 implementation plus future roadmap (Phase 2+).
Architecture is scalable, documented, and AI-agent ready.
