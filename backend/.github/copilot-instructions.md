# SuraSmart: Facial Recognition Web Application

## Current Status: MVP Phase (v1.0)
**Active Development**: Simple Flask prototype implementing core facial recognition feature  
**Roadmap**: Enterprise-scale distributed system (see Roadmap section below)  
**Focus for Agents**: Enhance MVP functionality; reference roadmap for architectural decisions

## Project Vision
SuraSmart is an innovative AI-powered application designed to revolutionize the search for missing persons by leveraging advanced facial recognition and government database integrations. The platform aims to provide fast, accurate matches to bring closure to families and improve efficiency for authorities.

---

## CURRENT MVP: Architecture & Implementation

### Service Boundary (MVP)
- **Backend**: Single-file Flask application (`app.py`)
- **Frontend**: Minimal HTML/CSS/JS (templates in `templates/`, assets in `static/`)
- **ML Engine**: DeepFace library with FaceNet model (pre-trained)
- **Storage**: File-system based (no database)
- **Deployment**: Gunicorn WSGI server on port 80
- **Scale**: Single-instance, local image database only

### Core Data Flow (MVP)
1. User uploads image via HTML form → `/upload` POST endpoint
2. Flask saves uploaded file to `static/uploads/`
3. DeepFace.verify() compares against all images in `static/db_images/` sequentially
4. Returns first verified match (binary: matched/not matched) with distance metric
5. Rendered via `results.html` template

### File Organization
- `app.py`: Single Flask app with all routes and ML integration
- `templates/`: HTML templates (index.html for upload, results.html for results)
- `static/`: CSS, JS, and image folders (db_images = face database, uploads = temp uploads)
- `requirements.txt`: Core dependencies (deepface, flask, gunicorn, werkzeug)
- `env/`: Virtual environment with all ML model dependencies pre-installed

## Critical Conventions

### Face Database
- Location: `static/db_images/` (must exist, auto-created in app.py)
- Format: PNG, JPG, JPEG images only (see `get_all_images()` filter)
- Naming: Filename used as match label in results (e.g., "john_doe.jpg" displays as match)
- Pattern: One face per image file; no batch/multi-face handling

### Image Upload & Verification
- Uploaded files saved to `static/uploads/` with original filename
- DeepFace.verify() model: **FaceNet** (model_name='Facenet')
- Comparison logic: Stops at first verified match (`break` after match found)
- Distance metric returned but not used for ranking (simple verified/not-verified binary)

### Route Structure
- `/` (GET): Renders index.html (upload form)
- `/upload` (POST): Processes image, runs comparison, returns results.html
- Image file upload via `request.files['image']` multipart form

## Development Workflows

### Running Locally
```bash
# Activate virtual environment (env/ folder exists)
./env/Scripts/activate  # Windows
# Or: source env/Scripts/activate  # Linux/Mac

# Install dependencies (should already be in env/)
pip install -r requirements.txt

# Run Flask development server
python app.py  # Runs on http://0.0.0.0:80
```

### Deployment
- **Server**: Gunicorn (specified in Procfile)
- **Command**: `gunicorn app:app` (Procfile shows incorrect module name—may need update)
- **Port**: 80 (hardcoded in app.py)

## Important Implementation Details

### Why Single File?
- Simple prototype/MVP design; no complex business logic separation needed
- All routes, ML integration, and file handling in one place

### Verification Logic Limitation
- Current design: Returns on **first match** (early exit via break)
- No ranking, no threshold configuration, no confidence scoring beyond verified/unverified
- **Consider**: For production, may want to collect all matches with distances for user ranking

### No Database
- File-system based: images stored directly in folders
- No user authentication, no match history, no persistence beyond file storage

## Common Tasks & Patterns

### Adding a New Face to Database
- Place image in `static/db_images/` with descriptive filename
- Filename becomes the label shown in results

### Modifying Verification Behavior
- Change model: Edit `model_name='Facenet'` in DeepFace.verify() call (line 49)
- Adjust distance threshold: Wrap result['verified'] with custom distance check
- Collect all matches: Remove `break` statement to compare against all db_images

### Frontend Customization
- Style: Edit `static/style.css` and `static/main.css`
- Layout: Modify `templates/index.html` and `templates/results.html`
- JS logic: Add to `static/script.js` (currently minimal)

## Integration Points & Dependencies

### DeepFace
- Version: 0.0.93 (locked in requirements.txt)
- Required for: `DeepFace.verify()` method with FaceNet model
- Note: Downloads pre-trained model on first run; ensure sufficient disk space

### Flask & Werkzeug
- Flask 3.0.3 for routing and templating
- Werkzeug 3.0.4 for WSGI utilities and file handling
- CORS not enabled (flask_cors 5.0.1 in env but not used in app.py)

### Static File Serving
- Flask serves static files from `static/` directory by default
- `{{ url_for('static', filename='...') }}` used in templates (Jinja2)

## Known Issues & TODOs (MVP)

1. **Procfile module name mismatch**: Says `wuzu-smart-no-db:app` but should be `app:app`
2. **Results.html content missing**: Only template referenced; need to verify implementation
3. **Error handling**: No try-catch around DeepFace.verify(); model failures not handled
4. **File cleanup**: Uploaded files in `static/uploads/` never deleted (grows over time)
5. **Security**: No authentication/authorization; anyone can upload and search

---

## ROADMAP: Enterprise Architecture (Per PRD/TRD)

### Product Vision (Target State)
Transform MVP into comprehensive missing persons search platform with government database integrations, multimodal identification, and distributed processing across low-connectivity regions.

### Feature Implementation Status

#### ✅ IMPLEMENTED (MVP)
- Facial recognition (FaceNet model)
- Web-based UI for image upload
- Single database image comparison
- Basic deployment (Gunicorn)

#### 🔄 PLANNED (Phase 2-3)
**Core Expansion:**
- Multimodal Identification: Voice matching, biometric data support
- Multiple Database Integration: Morgue, jail, police custody records
- Real-time Notification System: Automatic alerts on matches
- Multilingual Interface: Support multiple languages via i18n framework
- Advanced Search: >98% accuracy, partial face recognition, adaptive learning

**Infrastructure Upgrade:**
- Microservices Architecture: Containerized services (Python/Django, Node.js)
- Kubernetes Orchestration: Multi-region deployment
- Blockchain Integration: Tamper-proof audit trails (permissioned network)
- Cloud Scaling: AWS/GCP with auto-scaling groups, Redis caching
- Edge Computing: Functionality in <100kbps connectivity areas

**Enterprise Features:**
- Role-Based Access Control (RBAC) with OAuth 2.0
- Mobile Apps: React Native for iOS/Android
- Performance: <30 second searches, 99.95% uptime, 10K+ concurrent users
- Security: End-to-end encryption, GDPR/CCPA compliance, blockchain audit logs
- Government APIs: Secure integrations with national/local databases

#### ❌ NOT YET STARTED
- Blockchain implementation
- Mobile applications
- Government database connectors
- Multimodal processing
- Voice/biometric matching
- Multilingual support
- Edge node deployment
- Advanced RBAC system

### Future Architecture Overview (Reference for Design Decisions)
When expanding this MVP, refer to these TRD principles:
- **Technology Stack**: Python/Django backend, Node.js notifications, TensorFlow/PyTorch for ML, Kubernetes for orchestration
- **Data Integration**: Secure APIs for morgue/jail/police databases with normalization layer
- **Performance Targets**: <30s search time, >98% accuracy, <0.5% false positive rate
- **Security Model**: Blockchain audit trails, end-to-end encryption, immutable access logs
- **Compliance**: BIPA, law enforcement protocols, WCAG 2.1 AA accessibility, cross-border data transfers

---

## MVP Development Guidance for AI Agents

### When to Focus on MVP Features
- Improving facial recognition accuracy with current FaceNet model
- Enhancing image handling (quality, formats, edge cases)
- Fixing deployment issues (Procfile, port configuration)
- Improving error handling and user experience
- Adding basic validation and security measures

### When to Consider Roadmap Architecture
- **Refactoring for Scale**: If adding multiple databases, structure for microservices separation
- **Security Decisions**: Implement patterns that can evolve toward blockchain/audit trails
- **Data Handling**: Design with future government API integrations in mind (validation layers, rate limiting)
- **Multilingual Prep**: Use i18n patterns from the start, even if single language now
- **Error Handling**: Build resilient patterns for future external database fallbacks

### Red Flags: Don't Implement Enterprise Features on MVP
- ❌ Don't add blockchain layer to single-file Flask app
- ❌ Don't build Kubernetes deployment configs without microservices
- ❌ Don't create complex RBAC for prototype with no authentication
- ❌ Don't implement edge node logic without distributed architecture first

**Focus Rule**: Enhance MVP functionality and stability first. Make design decisions that *prepare* for enterprise scale without *requiring* it today.
