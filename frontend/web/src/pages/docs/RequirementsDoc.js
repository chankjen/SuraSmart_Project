import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import '../../styles/Documentation.css';
import '../../styles/ChaseUI.css';

const sections = [
  { id: 'overview', label: 'Overview' },
  { id: 'stakeholders', label: 'Stakeholders' },
  { id: 'functional', label: 'Functional Requirements' },
  { id: 'nonfunctional', label: 'Non-Functional Requirements' },
  { id: 'user-stories', label: 'User Stories' },
  { id: 'compliance', label: 'Compliance & Legal' },
  { id: 'constraints', label: 'Constraints' },
];

const RequirementsDoc = () => {
  const navigate = useNavigate();
  const [activeSection, setActiveSection] = useState('overview');

  const scrollTo = (id) => {
    setActiveSection(id);
    document.getElementById(id)?.scrollIntoView({ behavior: 'smooth' });
  };

  return (
    <div className="docs-page">
      <header className="chase-header">
        <div className="chase-logo">Sura<span>Smart</span> &nbsp;|&nbsp; <span style={{ fontWeight: 400, fontSize: '1rem', opacity: 0.85 }}>Requirements Documentation</span></div>
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
          <button className="docs-sidebar-link" onClick={() => navigate('/docs/architecture')}>Architecture Doc →</button>
          <button className="docs-sidebar-link" onClick={() => navigate('/docs/technical')}>Technical Doc →</button>
          <button className="docs-sidebar-link" onClick={() => navigate('/docs/end-user')}>End-User Guide →</button>
        </aside>

        <main className="docs-content">
          <div className="docs-version-badge">v1.0 • March 2026</div>
          <h1>Requirements Documentation</h1>
          <p className="docs-intro-lead">
            This document defines the functional and non-functional requirements, stakeholders, user stories, and compliance mandates for the SuraSmart Missing Persons Registry Platform.
          </p>

          {/* OVERVIEW */}
          <section id="overview" className="docs-section-anchor">
            <h2>📌 Overview</h2>
            <p>SuraSmart is a national AI-powered Missing Persons Registry System designed for Kenya. The platform enables families, police officers, and government officials to collaboratively report, track, investigate, and resolve missing person cases using facial recognition, blockchain-backed audit trails, and role-based workflows.</p>
            <table className="docs-table">
              <thead><tr><th>Attribute</th><th>Value</th></tr></thead>
              <tbody>
                <tr><td>Project Name</td><td>SuraSmart – Missing Persons Registry</td></tr>
                <tr><td>Version</td><td>1.0.0</td></tr>
                <tr><td>Date</td><td>March 2026</td></tr>
                <tr><td>Classification</td><td>Government / Law Enforcement</td></tr>
                <tr><td>Applicable Region</td><td>Republic of Kenya</td></tr>
              </tbody>
            </table>
          </section>

          <hr className="docs-divider" />

          {/* STAKEHOLDERS */}
          <section id="stakeholders" className="docs-section-anchor">
            <h2>👥 Stakeholders</h2>
            <table className="docs-table">
              <thead><tr><th>Stakeholder</th><th>Role</th><th>Interest</th></tr></thead>
              <tbody>
                <tr><td>Family Members</td><td>Reporters</td><td>Report, track, and receive updates on missing persons.</td></tr>
                <tr><td>Police Officers</td><td>Investigators</td><td>Search databases, run AI facial scans, update case status, and escalate.</td></tr>
                <tr><td>Government Officials</td><td>Reviewers / Overseers</td><td>Review escalated cases, provide oversight, access analytics.</td></tr>
                <tr><td>System Administrators</td><td>Platform Managers</td><td>Manage users, roles, approvals, and system health.</td></tr>
                <tr><td>Regulatory Bodies</td><td>Compliance Auditors</td><td>Ensure GDPR, BIPA, and PDPPA compliance via blockchain audit trails.</td></tr>
              </tbody>
            </table>
          </section>

          <hr className="docs-divider" />

          {/* FUNCTIONAL */}
          <section id="functional" className="docs-section-anchor">
            <h2>✅ Functional Requirements</h2>

            <h3>FR-01: User Registration & Authentication</h3>
            <ul>
              <li>Users register with personal details, role, and organisation.</li>
              <li>Administrators approve or reject registrations with reason.</li>
              <li>JWT-based authentication with role-based access control (RBAC).</li>
              <li>Email notifications sent on registration approval/rejection.</li>
            </ul>

            <h3>FR-02: Missing Person Reporting</h3>
            <ul>
              <li>Family Members submit reports with name, age, gender, identifying marks, last seen date, and County/Subcounty location (cascading dropdowns from Kenya's 47 counties).</li>
              <li>Case ID is generated upon submission.</li>
              <li>Case status begins at <code className="inline">REPORTED</code>.</li>
              <li>Case progresses through: REPORTED → RAISED → ESCALATED → GOVERNMENT_REVIEW → CLOSED.</li>
            </ul>

            <h3>FR-03: Facial Image Upload & AI Search</h3>
            <ul>
              <li>Family Members upload photos linked to a case.</li>
              <li>Police Officers trigger AI facial recognition searches across multiple databases (morgue, jail, police).</li>
              <li>System returns match results with confidence scores.</li>
              <li>Blockchain audit record created for every search (TRD 5.1.2).</li>
            </ul>

            <h3>FR-04: Case Escalation Workflow</h3>
            <ul>
              <li>Police Officers escalate unresolved cases to Government Officials.</li>
              <li>Government Officials submit formal reviews.</li>
              <li>Case closure requires dual-signature from Family Member and Police Officer.</li>
            </ul>

            <h3>FR-05: Analytics Dashboard</h3>
            <ul>
              <li>Government Officials access a real-time System Analytics Dashboard.</li>
              <li>Displays: Gender Distribution, Top 5 Counties, Case Status Breakdown, Resolution Rate, Unattended Cases.</li>
              <li>Regional Oversight: Interactive county drill-down showing subcounty case dispersion.</li>
            </ul>

            <h3>FR-06: Blockchain Audit Trail</h3>
            <ul>
              <li>All search operations logged immutably via <code className="inline">AuditContract.sol</code>.</li>
              <li>Only hashed PII stored on-chain; encryption key stored off-chain.</li>
              <li>Records expire after configurable retention period (default: 90 days).</li>
            </ul>
          </section>

          <hr className="docs-divider" />

          {/* NON-FUNCTIONAL */}
          <section id="nonfunctional" className="docs-section-anchor">
            <h2>⚡ Non-Functional Requirements</h2>
            <table className="docs-table">
              <thead><tr><th>Category</th><th>Requirement</th><th>Target</th></tr></thead>
              <tbody>
                <tr><td>Performance</td><td>Search response time</td><td>&lt;30 seconds (TRD 6.1.1)</td></tr>
                <tr><td>Availability</td><td>Platform uptime</td><td>99.9% SLA</td></tr>
                <tr><td>Security</td><td>Data encryption (at rest / in transit)</td><td>AES-256 / TLS 1.3</td></tr>
                <tr><td>Scalability</td><td>Concurrent users</td><td>&gt;500 simultaneous users</td></tr>
                <tr><td>Accessibility</td><td>WCAG 2.1 AA compliance</td><td>All public pages</td></tr>
                <tr><td>Maintainability</td><td>Codebase documentation</td><td>100% critical-path coverage</td></tr>
                <tr><td>Portability</td><td>Browser support</td><td>Chrome/Firefox/Safari/Edge</td></tr>
              </tbody>
            </table>
          </section>

          <hr className="docs-divider" />

          {/* USER STORIES */}
          <section id="user-stories" className="docs-section-anchor">
            <h2>📖 User Stories</h2>
            <table className="docs-table">
              <thead><tr><th>ID</th><th>As a…</th><th>I want to…</th><th>So that…</th></tr></thead>
              <tbody>
                <tr><td>US-01</td><td>Family Member</td><td>Report a missing person with a photo</td><td>Police can begin searching immediately</td></tr>
                <tr><td>US-02</td><td>Family Member</td><td>Track the status of my case</td><td>I know what is being done</td></tr>
                <tr><td>US-03</td><td>Police Officer</td><td>Run an AI facial recognition search</td><td>I can identify the person across multiple databases</td></tr>
                <tr><td>US-04</td><td>Police Officer</td><td>Escalate a case to government</td><td>High-priority or complex cases get senior attention</td></tr>
                <tr><td>US-05</td><td>Government Official</td><td>Review escalated cases</td><td>I can ensure proper resolution or provide policy guidance</td></tr>
                <tr><td>US-06</td><td>Government Official</td><td>View analytics by county and subcounty</td><td>I can identify regional hotspots and deploy resources</td></tr>
                <tr><td>US-07</td><td>Admin</td><td>Approve or reject user registrations</td><td>Only verified personnel access the system</td></tr>
                <tr><td>US-08</td><td>Auditor</td><td>Query the blockchain audit trail</td><td>I can verify all search operations were compliant</td></tr>
              </tbody>
            </table>
          </section>

          <hr className="docs-divider" />

          {/* COMPLIANCE */}
          <section id="compliance" className="docs-section-anchor">
            <h2>⚖️ Compliance & Legal</h2>
            <div className="docs-warn-box"><strong>⚠️ Note:</strong> This system processes sensitive biometric data. All operations must comply with the frameworks listed below.</div>
            <ul>
              <li><strong>Kenya Data Protection Act (PDPPA 2019):</strong> Governs collection, storage, and processing of personal data.</li>
              <li><strong>GDPR (Article 9):</strong> Biometric data classified as special category requiring explicit consent.</li>
              <li><strong>BIPA (Illinois, USA) – adopted as international standard:</strong> Biometric data must not be sold, leased, or disclosed without consent.</li>
              <li><strong>TRD Section 8:</strong> Internal Technical Reference Document governing system-level data handling policies.</li>
              <li><strong>National Police Service Act (Kenya):</strong> Mandates chain of evidence and audit requirements in investigations.</li>
            </ul>
          </section>

          <hr className="docs-divider" />

          {/* CONSTRAINTS */}
          <section id="constraints" className="docs-section-anchor">
            <h2>🔒 Constraints</h2>
            <ul>
              <li>Platform limited to Kenya's 47 counties and their official subcounties.</li>
              <li>AI facial recognition must fall back gracefully when Python libraries (e.g., numpy/DeepFace) are unavailable (local dev).</li>
              <li>Blockchain writes are asynchronous and must not block the user-facing search experience.</li>
              <li>PII must never be stored in plaintext on-chain; only SHA-256 hashes are permitted.</li>
              <li>Case closure is a multi-party agreement and cannot be finalised by a single user unilaterally.</li>
            </ul>
          </section>
        </main>
      </div>
    </div>
  );
};

export default RequirementsDoc;
