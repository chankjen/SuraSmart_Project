import React from 'react';
import { useNavigate } from 'react-router-dom';
import '../../styles/Documentation.css';
import '../../styles/ChaseUI.css';


const docSections = [
  {
    id: 'requirements',
    path: '/docs/requirements',
    icon: '📋',
    title: 'Requirements Documentation',
    desc: 'System requirements, functional and non-functional specifications, user stories, and compliance mandates for the SuraSmart platform.',
  },
  {
    id: 'architecture',
    path: '/docs/architecture',
    icon: '🏗️',
    title: 'Architectural Documentation',
    desc: 'High-level system design, component diagrams, data flows, technology stack, and security architecture decisions.',
  },
  {
    id: 'technical',
    path: '/docs/technical',
    icon: '⚙️',
    title: 'Technical Documentation',
    desc: 'API reference, backend logic, blockchain audit trail, facial recognition integration, and developer setup guides.',
  },
  {
    id: 'enduser',
    path: '/docs/end-user',
    icon: '👤',
    title: 'End-User Documentation',
    desc: 'Step-by-step guides for Family Members, Police Officers, and Government Officials using the SuraSmart portal.',
  },
];

const DocHub = () => {
  const navigate = useNavigate();

  return (
    <div className="docs-page">
      <header className="chase-header" style={{ marginBottom: 0 }}>
        <div className="chase-logo">Sura<span>Smart</span> &nbsp;|&nbsp; <span style={{ fontWeight: 400, fontSize: '1rem', opacity: 0.85 }}>Documentation</span></div>
        <div style={{ display: 'flex', gap: 12 }}>
          <button className="chase-button-outline" style={{ color: 'white', borderColor: 'white', background: 'transparent', padding: '6px 18px', borderRadius: 8, cursor: 'pointer', fontSize: '0.9rem' }} onClick={() => navigate('/')}>Home</button>
          <button className="chase-button" style={{ padding: '6px 18px', fontSize: '0.9rem' }} onClick={() => navigate('/login')}>Login</button>
        </div>
      </header>

      <div className="chase-container" style={{ paddingTop: 48, paddingBottom: 64 }}>
        <div className="docs-version-badge">v1.0 • March 2026</div>
        <h1 style={{ fontSize: '2.4rem', color: 'var(--chase-blue-dark)', fontWeight: 700, margin: '0 0 12px' }}>SuraSmart Documentation</h1>
        <p className="docs-intro-lead">
          Welcome to the official SuraSmart documentation hub. Select a document category below to explore system requirements, architecture, technical references, or user guides.
        </p>

        <div className="doc-hub-grid">
          {docSections.map(doc => (
            <div key={doc.id} className="doc-hub-card" onClick={() => navigate(doc.path)}>
              <div className="doc-hub-icon">{doc.icon}</div>
              <h3>{doc.title}</h3>
              <p>{doc.desc}</p>
              <div className="doc-hub-arrow">Read documentation →</div>
            </div>
          ))}
        </div>

        <hr className="docs-divider" style={{ marginTop: 56 }} />

        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr 1fr', gap: 20, marginTop: 0 }}>
          <div className="docs-info-box">
            <strong>ℹ️ Platform Version:</strong> SuraSmart v1.0<br />
            Built on Django REST + React.
          </div>
          <div className="docs-tip-box">
            <strong>✓ Compliance:</strong> GDPR, BIPA, PDPPA Kenya 2023,<br />Blockchain Audit TRD 5.1.2.
          </div>
          <div className="docs-warn-box">
            <strong>⚠️ Restricted:</strong> Technical docs contain sensitive system details. For authorised personnel.
          </div>
        </div>
      </div>
    </div>
  );
};

export default DocHub;
