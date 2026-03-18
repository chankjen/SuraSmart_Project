import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import '../../styles/Documentation.css';
import '../../styles/ChaseUI.css';

const sections = [
  { id: 'getting-started', label: 'Getting Started' },
  { id: 'family-guide', label: 'Family Member Guide' },
  { id: 'police-guide', label: 'Police Officer Guide' },
  { id: 'government-guide', label: 'Government Official Guide' },
  { id: 'admin-guide', label: 'Admin Guide' },
  { id: 'faq', label: 'FAQ' },
  { id: 'support', label: 'Support' },
];

const EndUserDoc = () => {
  const navigate = useNavigate();
  const [activeSection, setActiveSection] = useState('getting-started');

  const scrollTo = (id) => {
    setActiveSection(id);
    document.getElementById(id)?.scrollIntoView({ behavior: 'smooth' });
  };

  return (
    <div className="docs-page">
      <header className="chase-header">
        <div className="chase-logo">Sura<span>Smart</span> &nbsp;|&nbsp; <span style={{ fontWeight: 400, fontSize: '1rem', opacity: 0.85 }}>End-User Guide</span></div>
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
          <button className="docs-sidebar-link" onClick={() => navigate('/docs/technical')}>Technical Doc →</button>
        </aside>

        <main className="docs-content">
          <div className="docs-version-badge">v1.0 • March 2026</div>
          <h1>End-User Documentation</h1>
          <p className="docs-intro-lead">
            This guide explains how to use SuraSmart for each user role: Family Members reporting missing loved ones, Police Officers investigating cases, Government Officials overseeing the registry, and Administrators managing the platform.
          </p>

          {/* GETTING STARTED */}
          <section id="getting-started" className="docs-section-anchor">
            <h2>🚀 Getting Started</h2>
            <h3>Step 1: Access the Platform</h3>
            <p>Open your web browser and navigate to <strong>http://surasmart.go.ke</strong> (or <strong>http://localhost:3000</strong> in development).</p>

            <h3>Step 2: Register Your Account</h3>
            <ol>
              <li>Click <strong>Register</strong> on the navigation bar.</li>
              <li>Fill in your personal details: Full Name, Email, Phone Number.</li>
              <li>Select your <strong>Role</strong>: Family Member, Police Officer, or Government Official.</li>
              <li>Police Officers and Government Officials must provide their <strong>Badge Number</strong> or <strong>Department</strong>.</li>
              <li>Submit the form and wait for Administrator approval.</li>
            </ol>
            <div className="docs-info-box">
              <strong>ℹ️ Approval Notice:</strong> Your account is reviewed by an administrator before activation. You will receive an email notification once approved or rejected with a reason.
            </div>

            <h3>Step 3: Log In</h3>
            <ol>
              <li>Click <strong>Login</strong> on the navigation bar.</li>
              <li>Enter your username/email and password.</li>
              <li>You are automatically redirected to your role-specific dashboard.</li>
            </ol>
          </section>

          <hr className="docs-divider" />

          {/* FAMILY MEMBER */}
          <section id="family-guide" className="docs-section-anchor">
            <h2>👨‍👩‍👧 Family Member Guide</h2>
            <p>As a Family Member, you are the primary reporter of missing persons. Your portal allows you to file reports, upload photos, and monitor case progress.</p>

            <h3>Reporting a Missing Person</h3>
            <ol>
              <li>On your <strong>Family Dashboard</strong>, click <strong>Report Missing Person</strong>.</li>
              <li>Fill in the report form:
                <ul>
                  <li><strong>Full Name</strong> — The missing person's complete name.</li>
                  <li><strong>Age</strong> — Approximate age.</li>
                  <li><strong>Gender</strong> — Select from the dropdown.</li>
                  <li><strong>Description</strong> — Physical description, clothing, circumstances.</li>
                  <li><strong>Last Seen Date</strong> — Approximate date/time.</li>
                  <li><strong>County</strong> — Select from Kenya's 47 counties.</li>
                  <li><strong>Subcounty</strong> — Automatically populated based on county selection.</li>
                  <li><strong>Identifying Marks</strong> — Scars, tattoos, or other identifiers (optional).</li>
                </ul>
              </li>
              <li>Click <strong>Report Missing Person</strong> to submit.</li>
              <li>You will be redirected to your dashboard where you can track the case status.</li>
            </ol>

            <h3>Uploading a Photo</h3>
            <ol>
              <li>From your dashboard, select a reported case.</li>
              <li>Click <strong>Upload Photo</strong> or <strong>Raise Case</strong>.</li>
              <li>Select a clear, front-facing photograph of the missing person.</li>
              <li>Click <strong>Upload</strong>. The AI will process the image for matching.</li>
            </ol>
            <div className="docs-tip-box"><strong>✓ Photo Tips:</strong> Use a clear, recent, front-facing photo with good lighting. Avoid sunglasses or hats. Higher resolution improves AI matching accuracy.</div>

            <h3>Approving Case Closure</h3>
            <p>When a Police Officer requests case closure, you will see a notification on your dashboard. Review the details and click <strong>Approve Closure</strong> to finalise. The case status will change to <strong>Closed</strong>.</p>
          </section>

          <hr className="docs-divider" />

          {/* POLICE OFFICER */}
          <section id="police-guide" className="docs-section-anchor">
            <h2>🚔 Police Officer Guide</h2>
            <p>As a Police Officer, you investigate cases, run AI facial recognition searches, update case status, and escalate complex cases to government officials.</p>

            <h3>Viewing Assigned Cases</h3>
            <ol>
              <li>Log in and access your <strong>Police Dashboard</strong>.</li>
              <li>The dashboard displays: Total Cases, Pending Cases, Resolved Cases, and Escalated Cases.</li>
              <li>Click on any case card to view full details.</li>
            </ol>

            <h3>Running an AI Facial Recognition Search</h3>
            <ol>
              <li>Open a case from your dashboard.</li>
              <li>Navigate to the <strong>Facial Recognition Search</strong> tab.</li>
              <li>Review the uploaded photo, then click <strong>Analyse Case Photo Now</strong>.</li>
              <li>The system searches across morgue, jail, and police databases.</li>
              <li>Results are displayed with confidence scores. If a match is found, review the matched record details.</li>
              <li>A blockchain audit trail is automatically created for this search.</li>
            </ol>
            <div className="docs-info-box"><strong>ℹ️ Audit Trail:</strong> Every search you perform is permanently recorded on the blockchain for compliance and accountability purposes.</div>

            <h3>Escalating a Case</h3>
            <ol>
              <li>Open the case and click <strong>Escalate Case</strong>.</li>
              <li>Provide an escalation reason/summary.</li>
              <li>The case status changes to <strong>ESCALATED</strong> and a Government Official is notified.</li>
            </ol>

            <h3>Requesting Case Closure</h3>
            <ol>
              <li>Once the person is found and the case is resolved, click <strong>Request Closure</strong>.</li>
              <li>The family member must approve the closure for it to be finalised.</li>
            </ol>
          </section>

          <hr className="docs-divider" />

          {/* GOVERNMENT OFFICIAL */}
          <section id="government-guide" className="docs-section-anchor">
            <h2>🏛️ Government Official Guide</h2>
            <p>As a Government Official, you review escalated cases and monitor the national missing persons registry through analytics tools.</p>

            <h3>Reviewing Escalated Cases</h3>
            <ol>
              <li>Access your <strong>Government Dashboard</strong>.</li>
              <li>The <strong>Escalated Cases</strong> panel shows all cases pending your review.</li>
              <li>Click a case to view full details, investigation history, and AI search results.</li>
              <li>Click <strong>Submit Review</strong>, provide your written assessment, and click <strong>OK</strong>.</li>
              <li>The case status updates to <strong>GOVERNMENT_REVIEW</strong>.</li>
            </ol>

            <h3>Accessing the Analytics Dashboard</h3>
            <ol>
              <li>Click <strong>View Analytics</strong> on your dashboard.</li>
              <li>The System Analytics Dashboard displays:
                <ul>
                  <li><strong>Gender Distribution</strong> – Case reporting by gender.</li>
                  <li><strong>Top 5 Reporting Counties</strong> – Hotspot alert.</li>
                  <li><strong>Status Breakdown</strong> – Cases by current status.</li>
                  <li><strong>Unattended Cases</strong> – Reports needing immediate police attention.</li>
                </ul>
              </li>
              <li>Use the <strong>Regional Oversight</strong> panel: select a county from the dropdown to view case dispersion across subcounties.</li>
            </ol>
          </section>

          <hr className="docs-divider" />

          {/* ADMIN */}
          <section id="admin-guide" className="docs-section-anchor">
            <h2>⚙️ Administrator Guide</h2>
            <p>Administrators manage user accounts, registrations, and platform health.</p>

            <h3>Approving / Rejecting Registrations</h3>
            <ol>
              <li>Access the <strong>Admin Dashboard</strong> via the <em>Admin Login</em> button on the home page.</li>
              <li>The <strong>Pending Registrations</strong> panel lists all accounts awaiting approval.</li>
              <li>Click <strong>Review</strong> on any registration to view the submitted details.</li>
              <li>Click <strong>Approve</strong> or <strong>Reject</strong>.</li>
              <li>If rejecting, provide a reason — this is sent to the user via email.</li>
            </ol>

            <h3>Managing Users</h3>
            <p>The Admin Dashboard allows you to: view all registered users, see their role and verification status, approve pending accounts, and view user details and case history.</p>
          </section>

          <hr className="docs-divider" />

          {/* FAQ */}
          <section id="faq" className="docs-section-anchor">
            <h2>❓ Frequently Asked Questions</h2>
            <h3>Why is my account pending?</h3>
            <p>All accounts require administrator verification before activation. This ensures only authorised personnel access the system. Typical approval time is 1–2 business days.</p>

            <h3>What happens to my data after a case is closed?</h3>
            <p>Case data is retained for the legal retention period (90 days by default). Biometric data (face embeddings) is purged automatically after this period in compliance with GDPR and the Kenya Data Protection Act.</p>

            <h3>What if the AI search doesn't find a match?</h3>
            <p>No match does not mean the person isn't found — it means no match exists in the currently indexed databases. Police Officers can re-run searches as databases are updated, or escalate the case for broader investigation.</p>

            <h3>Is my data secure?</h3>
            <p>Yes. All sensitive data is encrypted at rest and in transit. Biometric data is never stored in plaintext. Every search is audited via an immutable blockchain record. Access is strictly role-based.</p>
          </section>

          <hr className="docs-divider" />

          {/* SUPPORT */}
          <section id="support" className="docs-section-anchor">
            <h2>📞 Support</h2>
            <table className="docs-table">
              <thead><tr><th>Channel</th><th>Details</th></tr></thead>
              <tbody>
                <tr><td>Email Support</td><td>support@surasmart.go.ke</td></tr>
                <tr><td>Emergency Helpline</td><td>+254 800 000 000 (24/7)</td></tr>
                <tr><td>Admin Contact</td><td>admin@surasmart.go.ke</td></tr>
                <tr><td>GitHub Issues</td><td>github.com/chankjen/SuraSmart_Project/issues</td></tr>
              </tbody>
            </table>
            <div className="docs-tip-box"><strong>✓ Include in Support Requests:</strong> Your username, the case ID (if applicable), a description of the issue, and any error messages you see.</div>
          </section>
        </main>
      </div>
    </div>
  );
};

export default EndUserDoc;
