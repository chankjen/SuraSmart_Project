import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import '../../styles/Documentation.css';
import '../../styles/ChaseUI.css';

const sections = [
  { id: 'setup', label: 'Developer Setup' },
  { id: 'api-auth', label: 'API: Authentication' },
  { id: 'api-cases', label: 'API: Missing Persons' },
  { id: 'api-facial', label: 'API: Facial Recognition' },
  { id: 'blockchain', label: 'Blockchain Audit API' },
  { id: 'models', label: 'Database Models' },
  { id: 'env', label: 'Environment Variables' },
];

const TechnicalDoc = () => {
  const navigate = useNavigate();
  const [activeSection, setActiveSection] = useState('setup');

  const scrollTo = (id) => {
    setActiveSection(id);
    document.getElementById(id)?.scrollIntoView({ behavior: 'smooth' });
  };

  return (
    <div className="docs-page">
      <header className="chase-header">
        <div className="chase-logo">Sura<span>Smart</span> &nbsp;|&nbsp; <span style={{ fontWeight: 400, fontSize: '1rem', opacity: 0.85 }}>Technical Documentation</span></div>
        <div style={{ display: 'flex', gap: 12 }}>
          <button className="chase-button-outline" style={{ color: 'white', borderColor: 'white', background: 'transparent', padding: '6px 18px', borderRadius: 8, cursor: 'pointer', fontSize: '0.9rem' }} onClick={() => navigate('/docs')}>← Docs</button>
          <button className="chase-button-outline" style={{ color: 'white', borderColor: 'white', background: 'transparent', padding: '6px 18px', borderRadius: 8, cursor: 'pointer', fontSize: '0.9rem' }} onClick={() => navigate('/')}>Home</button>
        </div>
      </header>

      <div className="docs-layout">
        <aside className="docs-sidebar">
          <h3>On This Page</h3>
          {sections.map(s => (
            <button key={s.id} className={`docs-sidebar-link ${activeSection === s.id ? 'active' : ''}`} onClick={() => scrollTo(s.id)}>{s.label}</button>
          ))}
          <hr className="docs-sidebar-divider" />
          <button className="docs-sidebar-link" onClick={() => navigate('/docs/requirements')}>Requirements Doc →</button>
          <button className="docs-sidebar-link" onClick={() => navigate('/docs/architecture')}>Architecture Doc →</button>
          <button className="docs-sidebar-link" onClick={() => navigate('/docs/end-user')}>End-User Guide →</button>
        </aside>

        <main className="docs-content">
          <div className="docs-version-badge">v1.0 • March 2026</div>
          <h1>Technical Documentation</h1>
          <p className="docs-intro-lead">
            This document provides API references, backend conventions, blockchain integration details, database models, and environment configuration for the SuraSmart platform.
          </p>
          <div className="docs-warn-box"><strong>⚠️ Developer Access Only:</strong> This document contains internal API structures and infrastructure details. Do not distribute externally.</div>

          {/* SETUP */}
          <section id="setup" className="docs-section-anchor">
            <h2>🛠️ Developer Setup</h2>
            <h3>Prerequisites</h3>
            <ul>
              <li>Python 3.10+ (with <code className="inline">venv</code>)</li>
              <li>Node.js 18+ and npm</li>
              <li>PostgreSQL 15+</li>
              <li>Redis (for Celery async tasks)</li>
            </ul>

            <h3>Backend Setup</h3>
            <pre className="docs-code">{`# Clone repository
git clone https://github.com/chankjen/SuraSmart_Project.git
cd SuraSmart_Project/backend

# Create virtual environment
python -m venv venv
.\\venv\\Scripts\\activate      # Windows
# source venv/bin/activate   # Linux/macOS

# Install dependencies
pip install -r requirements.txt

# Run migrations
python manage.py migrate

# Create superuser
python manage.py createsuperuser

# Start development server
python manage.py runserver 0.0.0.0:8000`}</pre>

            <h3>Frontend Setup</h3>
            <pre className="docs-code">{`cd SuraSmart_Project/frontend/web
npm install
$env:PORT=3000; $env:BROWSER='none'; npm start`}</pre>
          </section>

          <hr className="docs-divider" />

          {/* API: AUTH */}
          <section id="api-auth" className="docs-section-anchor">
            <h2>🔑 API: Authentication</h2>
            <table className="docs-table">
              <thead><tr><th>Method</th><th>Endpoint</th><th>Description</th><th>Auth</th></tr></thead>
              <tbody>
                <tr><td>POST</td><td><code className="inline">/api/auth/login/</code></td><td>Obtain JWT access + refresh tokens</td><td>None</td></tr>
                <tr><td>POST</td><td><code className="inline">/api/auth/refresh/</code></td><td>Refresh access token</td><td>Refresh token</td></tr>
                <tr><td>POST</td><td><code className="inline">/api/auth/register/</code></td><td>Register new user (pending admin approval)</td><td>None</td></tr>
                <tr><td>GET</td><td><code className="inline">/api/auth/me/</code></td><td>Get current authenticated user profile</td><td>Bearer JWT</td></tr>
                <tr><td>POST</td><td><code className="inline">/api/auth/approve/{'{userId}/'}</code></td><td>Admin approves registration</td><td>Admin JWT</td></tr>
              </tbody>
            </table>

            <h3>Token Structure</h3>
            <pre className="docs-code">{`// POST /api/auth/login/
// Request Body:
{ "username": "officer_jane", "password": "••••••••" }

// Response 200:
{
  "access":  "eyJhbGciOiJIUzI1NiIsInR5...",
  "refresh": "eyJhbGciOiJIUzI1NiIsInR5...",
  "user": {
    "id": 12, "username": "officer_jane",
    "role": "police_officer", "is_verified": true
  }
}`}</pre>
          </section>

          <hr className="docs-divider" />

          {/* API: CASES */}
          <section id="api-cases" className="docs-section-anchor">
            <h2>📋 API: Missing Persons</h2>
            <p>Base path: <code className="inline">/api/facial-recognition/missing-persons/</code></p>
            <table className="docs-table">
              <thead><tr><th>Method</th><th>Endpoint</th><th>Description</th></tr></thead>
              <tbody>
                <tr><td>GET</td><td><code className="inline">/</code></td><td>List all cases (paginated). Supports filter by status.</td></tr>
                <tr><td>POST</td><td><code className="inline">/</code></td><td>Create new missing person report</td></tr>
                <tr><td>GET</td><td><code className="inline">/{'{id}/'}</code></td><td>Retrieve case details</td></tr>
                <tr><td>PATCH</td><td><code className="inline">/{'{id}/'}</code></td><td>Update case fields</td></tr>
                <tr><td>POST</td><td><code className="inline">/{'{id}'}/upload_image/</code></td><td>Upload facial photo for a case</td></tr>
                <tr><td>POST</td><td><code className="inline">/{'{id}'}/run_ai_search/</code></td><td>Trigger AI facial recognition search</td></tr>
                <tr><td>POST</td><td><code className="inline">/{'{id}'}/escalate/</code></td><td>Escalate case to Government</td></tr>
                <tr><td>POST</td><td><code className="inline">/{'{id}'}/submit_government_report/</code></td><td>Government official submits review</td></tr>
                <tr><td>POST</td><td><code className="inline">/{'{id}'}/request_closure/</code></td><td>Police requests case closure</td></tr>
                <tr><td>POST</td><td><code className="inline">/{'{id}'}/approve_closure/</code></td><td>Family member approves closure (dual-signature)</td></tr>
              </tbody>
            </table>

            <h3>Case Lifecycle Status Values</h3>
            <table className="docs-table">
              <thead><tr><th>Status</th><th>Meaning</th><th>Actor</th></tr></thead>
              <tbody>
                <tr><td><code className="inline">REPORTED</code></td><td>Initial report submitted</td><td>Family Member</td></tr>
                <tr><td><code className="inline">RAISED</code></td><td>Case raised for investigation</td><td>System / Police</td></tr>
                <tr><td><code className="inline">ESCALATED</code></td><td>Escalated to Government</td><td>Police Officer</td></tr>
                <tr><td><code className="inline">GOVERNMENT_REVIEW</code></td><td>Under government review</td><td>Government Official</td></tr>
                <tr><td><code className="inline">PENDING_CLOSURE</code></td><td>Closure requested by police</td><td>Police Officer</td></tr>
                <tr><td><code className="inline">CLOSED</code></td><td>Closed after dual signature</td><td>Family Member + Police</td></tr>
              </tbody>
            </table>
          </section>

          <hr className="docs-divider" />

          {/* API: FACIAL */}
          <section id="api-facial" className="docs-section-anchor">
            <h2>🧠 API: Facial Recognition</h2>
            <h3>Run AI Search</h3>
            <pre className="docs-code">{`// POST /api/facial-recognition/missing-persons/{id}/run_ai_search/
// Headers: Authorization: Bearer <token>

// Response 200 (match found):
{
  "status": "success",
  "match_found": true,
  "confidence": 0.87,
  "matched_database": "POLICE",
  "matched_record_id": "REC-4421",
  "search_id": "sr-abc-1234",
  "blockchain_tx": "0x9f3e..."
}`}</pre>

            <div className="docs-info-box">
              <strong>Dev Mode Note:</strong> When DeepFace/NumPy is unavailable (Python 3.14, Windows), the system uses a deterministic dummy embedding that generates consistent results for the same image without AI processing.
            </div>
          </section>

          <hr className="docs-divider" />

          {/* BLOCKCHAIN */}
          <section id="blockchain" className="docs-section-anchor">
            <h2>⛓️ Blockchain Audit API</h2>
            <p>The <code className="inline">BlockchainAuditor</code> class in <code className="inline">blockchain_audit/auditor.py</code> provides the interface.</p>
            <table className="docs-table">
              <thead><tr><th>Method</th><th>Description</th></tr></thead>
              <tbody>
                <tr><td><code className="inline">log_search(...)</code></td><td>Triggers async on-chain write for a search event</td></tr>
                <tr><td><code className="inline">verify_audit_trail(search_id)</code></td><td>Returns existence and integrity status</td></tr>
                <tr><td><code className="inline">purge_expired_data()</code></td><td>Removes expired off-chain encrypted records (GDPR)</td></tr>
              </tbody>
            </table>

            <h3>Smart Contract Functions (AuditContract.sol)</h3>
            <table className="docs-table">
              <thead><tr><th>Function</th><th>Access</th><th>Description</th></tr></thead>
              <tbody>
                <tr><td><code className="inline">logAudit(...)</code></td><td>Authorised</td><td>Write immutable audit record</td></tr>
                <tr><td><code className="inline">getAudit(search_id)</code></td><td>Authorised</td><td>Retrieve full audit record</td></tr>
                <tr><td><code className="inline">verifyAudit(search_id)</code></td><td>Authorised</td><td>Lightweight integrity check</td></tr>
                <tr><td><code className="inline">authoriseAuditor(address)</code></td><td>Owner only</td><td>Grant write access to an address</td></tr>
                <tr><td><code className="inline">getAuditCount()</code></td><td>Authorised</td><td>Total number of audit records</td></tr>
              </tbody>
            </table>
          </section>

          <hr className="docs-divider" />

          {/* MODELS */}
          <section id="models" className="docs-section-anchor">
            <h2>🗄️ Database Models</h2>
            <h3>MissingPerson</h3>
            <table className="docs-table">
              <thead><tr><th>Field</th><th>Type</th><th>Notes</th></tr></thead>
              <tbody>
                <tr><td>id</td><td>UUID</td><td>Primary Key, auto-generated</td></tr>
                <tr><td>full_name</td><td>CharField</td><td>—</td></tr>
                <tr><td>age</td><td>IntegerField</td><td>Nullable</td></tr>
                <tr><td>gender</td><td>CharField</td><td>MALE/FEMALE/OTHER</td></tr>
                <tr><td>last_seen_location</td><td>CharField</td><td>Format: "Subcounty, County"</td></tr>
                <tr><td>last_seen_date</td><td>DateTimeField</td><td>Nullable</td></tr>
                <tr><td>status</td><td>CharField</td><td>See lifecycle statuses above</td></tr>
                <tr><td>reported_by</td><td>ForeignKey(User)</td><td>Family Member</td></tr>
                <tr><td>face_embedding</td><td>JSONField</td><td>AI face vector, encrypted at rest</td></tr>
                <tr><td>photo</td><td>ImageField</td><td>Stored in /media/</td></tr>
                <tr><td>created_at</td><td>DateTimeField</td><td>Auto</td></tr>
              </tbody>
            </table>
          </section>

          <hr className="docs-divider" />

          {/* ENV VARS */}
          <section id="env" className="docs-section-anchor">
            <h2>🔧 Environment Variables</h2>
            <pre className="docs-code">{`# Django Backend (.env or system env)
DJANGO_SECRET_KEY=your-secret-key-here
DATABASE_URL=postgresql://user:pass@localhost:5432/surasmart
ALLOWED_HOSTS=localhost,127.0.0.1

# Blockchain
BLOCKCHAIN_ENDPOINT=http://localhost:8545
AUDIT_SALT=change_this_in_production
ENCRYPTION_KEY=                       # Fernet key (auto-generated if empty)

# Data Retention
DATA_RETENTION_DAYS=90

# Celery
CELERY_BROKER_URL=redis://localhost:6379/0
CELERY_RESULT_BACKEND=redis://localhost:6379/0

# Email
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_HOST_USER=no-reply@surasmart.go.ke
EMAIL_HOST_PASSWORD=••••••••`}</pre>
          </section>
        </main>
      </div>
    </div>
  );
};

export default TechnicalDoc;
