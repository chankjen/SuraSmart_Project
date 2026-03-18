import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import '../../styles/Documentation.css';
import '../../styles/ChaseUI.css';

const sections = [
  { id: 'overview', label: 'Overview' },
  { id: 'system-arch', label: 'System Architecture' },
  { id: 'components', label: 'Components' },
  { id: 'data-flow', label: 'Data Flows' },
  { id: 'tech-stack', label: 'Technology Stack' },
  { id: 'security', label: 'Security Architecture' },
  { id: 'deployment', label: 'Deployment' },
];

const ArchitectureDoc = () => {
  const navigate = useNavigate();
  const [activeSection, setActiveSection] = useState('overview');

  const scrollTo = (id) => {
    setActiveSection(id);
    document.getElementById(id)?.scrollIntoView({ behavior: 'smooth' });
  };

  return (
    <div className="docs-page">
      <header className="chase-header">
        <div className="chase-logo">Sura<span>Smart</span> &nbsp;|&nbsp; <span style={{ fontWeight: 400, fontSize: '1rem', opacity: 0.85 }}>Architectural Documentation</span></div>
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
          <button className="docs-sidebar-link" onClick={() => navigate('/docs/technical')}>Technical Doc →</button>
          <button className="docs-sidebar-link" onClick={() => navigate('/docs/end-user')}>End-User Guide →</button>
        </aside>

        <main className="docs-content">
          <div className="docs-version-badge">v1.0 • March 2026</div>
          <h1>Architectural Documentation</h1>
          <p className="docs-intro-lead">
            This document describes the high-level system design, component architecture, data flows, technology choices, and security architecture of the SuraSmart platform.
          </p>

          {/* OVERVIEW */}
          <section id="overview" className="docs-section-anchor">
            <h2>📐 Overview</h2>
            <p>SuraSmart follows a three-tier client-server architecture: a React.js Single Page Application (SPA) as the presentation layer, a Django REST Framework (DRF) backend as the business logic layer, and PostgreSQL as the data persistence layer. A supplementary blockchain audit module provides immutable logging of all search events.</p>
            <div className="docs-info-box">
              <strong>Design Principles:</strong> Separation of Concerns · Role-Based Access Control · API-First Design · Fail-Open Audit Architecture · Privacy by Design
            </div>
          </section>

          <hr className="docs-divider" />

          {/* SYSTEM ARCHITECTURE */}
          <section id="system-arch" className="docs-section-anchor">
            <h2>🏗️ System Architecture</h2>
            <p>The platform uses a layered architecture where each tier communicates via well-defined interfaces:</p>

            <div className="docs-arch-diagram">
              <div className="docs-arch-layers">
                <div className="docs-arch-layer layer-presentation">🖥️ Presentation Layer — React.js SPA (Port 3000)</div>
                <div className="arch-arrow">⬇ REST API calls (JSON / JWT Auth)</div>
                <div className="docs-arch-layer layer-api">🔌 API Gateway — Django REST Framework (Port 8000)</div>
                <div className="arch-arrow">⬇ ORM / Service calls</div>
                <div className="docs-arch-layer layer-service">⚙️ Business Logic — AI Models · Facial Recognition · Notifications · Chat</div>
                <div className="arch-arrow">⬇ Database access</div>
                <div className="docs-arch-layer layer-data">🗄️ Data Layer — PostgreSQL · Media Storage</div>
                <div className="arch-arrow">⬇ Async audit write</div>
                <div className="docs-arch-layer layer-blockchain">⛓️ Blockchain Audit — AuditContract.sol (Ethereum / Hyperledger)</div>
              </div>
            </div>
          </section>

          <hr className="docs-divider" />

          {/* COMPONENTS */}
          <section id="components" className="docs-section-anchor">
            <h2>🧩 Components</h2>
            <table className="docs-table">
              <thead><tr><th>Component</th><th>Technology</th><th>Responsibility</th></tr></thead>
              <tbody>
                <tr><td>Frontend SPA</td><td>React.js 18, React Router v6</td><td>User interface for all portals (Family, Police, Government, Admin)</td></tr>
                <tr><td>Authentication</td><td>Django JWT (SimpleJWT)</td><td>Token issuance, refresh, and role-based access control</td></tr>
                <tr><td>Missing Persons API</td><td>DRF ViewSets</td><td>CRUD operations for missing person cases and case lifecycle</td></tr>
                <tr><td>AI Facial Recognition</td><td>DeepFace (prod) / MockNumpy (dev)</td><td>Face embedding, comparison, and database matching</td></tr>
                <tr><td>Notifications</td><td>Django Signals + celery-beat</td><td>Email/in-app notifications for case updates</td></tr>
                <tr><td>Blockchain Audit</td><td>Web3.py + AuditContract.sol</td><td>Immutable audit trail for all search operations</td></tr>
                <tr><td>Analytics Engine</td><td>Frontend aggregation (React)</td><td>Gender, county, status distribution analytics</td></tr>
                <tr><td>Admin Panel</td><td>Custom DRF + React Admin pages</td><td>User management, registration approval, system health</td></tr>
              </tbody>
            </table>

            <h3>Backend Django Apps</h3>
            <ul>
              <li><code className="inline">ai_models.facial_recognition</code> — Core AI search endpoint, case management ViewSets</li>
              <li><code className="inline">notifications</code> — Case event signals and notification records</li>
              <li><code className="inline">chat</code> — Real-time messaging between stakeholders</li>
              <li><code className="inline">shared</code> — Blockchain integration, shared utilities</li>
              <li><code className="inline">blockchain_audit</code> — BlockchainAuditor class, AuditContract interface</li>
            </ul>
          </section>

          <hr className="docs-divider" />

          {/* DATA FLOW */}
          <section id="data-flow" className="docs-section-anchor">
            <h2>🔄 Data Flows</h2>
            <h3>Missing Person Report Flow</h3>
            <ol>
              <li>Family Member submits form → <code className="inline">POST /api/facial-recognition/missing-persons/</code></li>
              <li>Backend validates and creates MissingPerson record (status: REPORTED)</li>
              <li>Case notification sent to relevant Police Officers</li>
              <li>Family Member uploads photo → <code className="inline">POST /api/facial-recognition/missing-persons/{"{id}"}/upload_image/</code></li>
              <li>AI generates face embedding, stored in database</li>
            </ol>

            <h3>AI Search Flow</h3>
            <ol>
              <li>Police Officer triggers search → <code className="inline">POST /api/facial-recognition/missing-persons/{"{id}"}/run_ai_search/</code></li>
              <li>Backend retrieves face embedding, compares against database</li>
              <li>Results returned with confidence scores</li>
              <li>Blockchain audit record written asynchronously (non-blocking)</li>
              <li>Results displayed to Officer with match details</li>
            </ol>

            <h3>Case Closure Flow</h3>
            <ol>
              <li>Police Officer approves closure → <code className="inline">POST .../request_closure/</code></li>
              <li>Family Member provides closure signature → <code className="inline">POST .../approve_closure/</code></li>
              <li>Status transitions to CLOSED; dashboard statistics update</li>
            </ol>
          </section>

          <hr className="docs-divider" />

          {/* TECH STACK */}
          <section id="tech-stack" className="docs-section-anchor">
            <h2>🛠️ Technology Stack</h2>
            <table className="docs-table">
              <thead><tr><th>Layer</th><th>Technology</th><th>Version</th></tr></thead>
              <tbody>
                <tr><td>Frontend Framework</td><td>React.js</td><td>18.x</td></tr>
                <tr><td>Frontend Routing</td><td>React Router DOM</td><td>6.x</td></tr>
                <tr><td>Backend Framework</td><td>Django</td><td>4.x</td></tr>
                <tr><td>REST API</td><td>Django REST Framework</td><td>3.x</td></tr>
                <tr><td>Authentication</td><td>djangorestframework-simplejwt</td><td>5.x</td></tr>
                <tr><td>Database</td><td>PostgreSQL</td><td>15.x</td></tr>
                <tr><td>AI Library</td><td>DeepFace / NumPy</td><td>Latest</td></tr>
                <tr><td>Blockchain Runtime</td><td>Solidity 0.8.19 / Web3.py</td><td>0.8.19 / 6.x</td></tr>
                <tr><td>Async Processing</td><td>Celery + Redis</td><td>5.x / 7.x</td></tr>
                <tr><td>Encryption</td><td>cryptography (Fernet)</td><td>Latest</td></tr>
              </tbody>
            </table>
          </section>

          <hr className="docs-divider" />

          {/* SECURITY */}
          <section id="security" className="docs-section-anchor">
            <h2>🔐 Security Architecture</h2>
            <div className="docs-warn-box"><strong>⚠️ Security Notice:</strong> This section contains sensitive architecture details. Restrict access to authorised personnel only.</div>
            <h3>Authentication & Authorisation</h3>
            <ul>
              <li>JWT tokens issued on login, short expiry (15 min access / 7 day refresh).</li>
              <li>Every API endpoint guarded by <code className="inline">IsAuthenticated</code> + custom role permission classes.</li>
              <li>Registration requires administrator approval before access is granted.</li>
            </ul>
            <h3>Data Protection</h3>
            <ul>
              <li>All PII encrypted using Fernet symmetric encryption before off-chain storage.</li>
              <li>SHA-256 salted hashes used for on-chain records (never plaintext).</li>
              <li>Production: TLS 1.3 for all data in transit.</li>
              <li>Database: Column-level encryption for biometric embeddings.</li>
            </ul>
            <h3>Audit & Non-Repudiation</h3>
            <ul>
              <li>Every search operation logged to the <code className="inline">AuditContract</code> smart contract.</li>
              <li>Records include: hashed user ID, role, query type, timestamp, match result.</li>
              <li>Records are immutable once written to the blockchain.</li>
            </ul>
          </section>

          <hr className="docs-divider" />

          {/* DEPLOYMENT */}
          <section id="deployment" className="docs-section-anchor">
            <h2>🚀 Deployment</h2>
            <table className="docs-table">
              <thead><tr><th>Environment</th><th>Frontend</th><th>Backend</th><th>Database</th></tr></thead>
              <tbody>
                <tr><td>Development</td><td>npm start (port 3000)</td><td>manage.py runserver (port 8000)</td><td>SQLite / PostgreSQL local</td></tr>
                <tr><td>Staging</td><td>Nginx reverse proxy</td><td>Gunicorn + Nginx</td><td>PostgreSQL (managed)</td></tr>
                <tr><td>Production</td><td>CDN (Cloudfront/Akamai)</td><td>Gunicorn + Nginx (SSL)</td><td>PostgreSQL (RDS)</td></tr>
              </tbody>
            </table>
          </section>
        </main>
      </div>
    </div>
  );
};

export default ArchitectureDoc;
