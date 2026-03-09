import React, { useState, useEffect, useCallback } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import api from '../services/api';
import '../styles/ChaseUI.css';

const PoliceDashboard = () => {
  const { user, logout } = useAuth();
  const navigate = useNavigate();
  const [cases, setCases] = useState([]);
  const [loading, setLoading] = useState(true);
  const [stats, setStats] = useState({
    totalCases: 0,
    activeCases: 0,
    resolvedCases: 0,
    pendingVerification: 0
  });

  const fetchCases = useCallback(async () => {
    try {
      const response = await api.getMissingPersons();
      const results = response.data.results || response.data || [];
      setCases(results);

      setStats({
        totalCases: results.length,
        activeCases: results.filter(c => ['REPORTED', 'RAISED', 'UNDER_INVESTIGATION', 'ANALYZED'].includes(c.status)).length,
        resolvedCases: results.filter(c => c.status === 'CLOSED').length,
        pendingVerification: results.filter(c => ['MATCH_FOUND', 'PENDING_CLOSURE', 'ESCALATED', 'GOVERNMENT_REVIEW'].includes(c.status)).length
      });
    } catch (error) {
      console.error('Error fetching cases:', error);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    if (user === null) return;
    if (user && user.role !== 'police_officer') {
      navigate('/login');
      return;
    }
    if (user) fetchCases();
  }, [user, navigate, fetchCases]);

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  const handleTakeCase = async (caseId) => {
    try {
      await api.updateCaseStatus(caseId, 'UNDER_INVESTIGATION');
      alert('Case taken. You can now download images and run searches.');
      fetchCases();
    } catch (error) {
      console.error('Error taking case:', error);
    }
  };

  const handleDownloadImage = async (caseId, imageUrl) => {
    // Security: Backend should verify case is assigned to this officer before serving image
    try {
      const blob = await api.downloadImage(imageUrl);
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `case_${caseId}_evidence.jpg`;
      a.click();
    } catch (error) {
      alert('Failed to download image. Ensure you have taken the case.');
    }
  };

  const handleRunAiSearch = async (caseId) => {
    try {
      const result = await api.runAiSearch(caseId);
      alert(`Search Complete. Match Confidence: ${result.confidence}%`);
      // In real app, this would open the match verification modal
      navigate(`/facial-search/${caseId}`);
    } catch (error) {
      alert('AI Search failed.');
    }
  };

  const handleEscalate = async (caseId) => {
    if (!window.confirm('Escalate this case to Government Official for national security review?')) return;
    try {
      await api.escalateCase(caseId);
      alert('Case escalated. Family member notified.');
      fetchCases();
    } catch (error) {
      console.error('Error escalating case:', error);
    }
  };

  const handleSubmitReport = async (caseId) => {
    const report = prompt("Enter match details and description statement:");
    if (!report) return;
    try {
      await api.submitReport(caseId, report);
      await api.updateCaseStatus(caseId, 'PENDING_CLOSURE');
      alert('Report sent to Family. Awaiting dual signature for closure.');
      fetchCases();
    } catch (error) {
      console.error('Error submitting report:', error);
    }
  };

  if (user === null || loading) {
    return <div className="chase-body"><div className="chase-container">Loading police dashboard...</div></div>;
  }

  return (
    <div className="chase-body">
      <div className="chase-header">
        <div className="chase-logo">Sura <span>Smart</span></div>
        <div style={{ display: 'flex', alignItems: 'center', gap: '20px' }}>
          <span style={{ color: 'white' }}>Officer {user?.first_name} {user?.last_name}</span>
          <button onClick={handleLogout} className="chase-button-outline" style={{ color: 'white', borderColor: 'white', padding: '0.5rem 1rem' }}>Logout</button>
        </div>
      </div>

      <div className="chase-container">
        <h1 className="chase-title">Police Officer Portal</h1>

        <div className="chase-grid">
          <div className="chase-card">
            <div className="chase-stat-label">Total Cases</div>
            <div className="chase-stat-value">{stats.totalCases}</div>
          </div>
          <div className="chase-card">
            <div className="chase-stat-label">Active Searches</div>
            <div className="chase-stat-value">{stats.activeCases}</div>
          </div>
          <div className="chase-card">
            <div className="chase-stat-label">Cases Resolved</div>
            <div className="chase-stat-value">{stats.resolvedCases}</div>
          </div>
          <div className="chase-card">
            <div className="chase-stat-label">Pending Verification</div>
            <div className="chase-stat-value">{stats.pendingVerification}</div>
          </div>
        </div>

        <div className="chase-grid" style={{ gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))', marginBottom: '40px' }}>
          <Link to="/facial-search" className="chase-card" style={{ textDecoration: 'none', borderTop: '4px solid var(--chase-blue)' }}>
            <h3 style={{ color: 'var(--chase-blue-dark)', marginBottom: '10px' }}>Facial Recognition Search</h3>
            <p style={{ color: 'var(--chase-gray-500)' }}>Search the database using facial recognition</p>
          </Link>
          <Link to="/reports" className="chase-card" style={{ textDecoration: 'none', borderTop: '4px solid var(--chase-blue)' }}>
            <h3 style={{ color: 'var(--chase-blue-dark)', marginBottom: '10px' }}>Generate Reports</h3>
            <p style={{ color: 'var(--chase-gray-500)' }}>View and generate case reports</p>
          </Link>
        </div>

        <div className="chase-section">
          <h2 style={{ marginBottom: '24px', color: 'var(--chase-blue-dark)' }}>All Missing Persons Cases</h2>
          {cases.length === 0 ? (
            <div className="chase-card" style={{ textAlign: 'center', padding: '60px' }}>
              <p style={{ color: 'var(--chase-gray-500)' }}>No cases reported yet.</p>
            </div>
          ) : (
            <div className="chase-card" style={{ padding: 0 }}>
              <div style={{ padding: '0 24px' }}>
                {cases.map(caseItem => (
                  <div key={caseItem.id} className="chase-list-item" style={{ flexDirection: 'column', alignItems: 'flex-start', gap: '15px', padding: '20px 0' }}>
                    <div style={{ width: '100%', display: 'flex', justifyContent: 'space-between' }}>
                      <div>
                        <h3 style={{ margin: '0 0 5px 0', color: 'var(--chase-blue-dark)' }}>{caseItem.full_name}</h3>
                        <p style={{ margin: '0', fontSize: '0.9rem', color: 'var(--chase-gray-500)' }}>
                          Reported: {new Date(caseItem.date_reported).toLocaleDateString()} | By: {caseItem.reporter_name}
                        </p>
                        {caseItem.gov_review_comment && (
                          <div style={{ marginTop: '5px', fontSize: '0.85rem', color: 'var(--chase-blue)', background: '#eff6ff', padding: '4px 8px', borderRadius: '4px', display: 'inline-block' }}>
                            🏛️ Reviewed Cases: {caseItem.gov_review_comment}
                          </div>
                        )}
                      </div>
                      <span className="chase-status-pill" style={{ 
                        background: caseItem.status === 'CLOSED' ? '#dcfce7' : '#e0f2fe', 
                        color: caseItem.status === 'CLOSED' ? '#15803d' : '#0369a1' 
                      }}>
                        {caseItem.status}
                      </span>
                    </div>

                    <div style={{ width: '100%', display: 'flex', gap: '10px', flexWrap: 'wrap', borderTop: '1px solid var(--chase-gray-100)', paddingTop: '15px' }}>
                      {/* Workflow Actions */}
                      {caseItem.status === 'RAISED' && (
                        <button onClick={() => handleTakeCase(caseItem.id)} className="chase-button" style={{ fontSize: '0.85rem' }}>Take Case</button>
                      )}
                      
                      {caseItem.status === 'UNDER_INVESTIGATION' && (
                        <>
                          <button onClick={() => handleDownloadImage(caseItem.id, caseItem.image_url)} className="chase-button-outline" style={{ fontSize: '0.85rem' }}>Download Image</button>
                          <button onClick={() => handleRunAiSearch(caseItem.id)} className="chase-button" style={{ fontSize: '0.85rem', background: 'var(--chase-blue-dark)' }}>Run AI Search</button>
                        </>
                      )}

                      {caseItem.status === 'ANALYZED' && (
                        <button onClick={() => handleSubmitReport(caseItem.id)} className="chase-button" style={{ fontSize: '0.85rem', background: 'var(--chase-green)' }}>Submit Report</button>
                      )}

                      {['UNDER_INVESTIGATION', 'ANALYZED', 'MATCH_FOUND'].includes(caseItem.status) && (
                        <button onClick={() => handleEscalate(caseItem.id)} className="chase-button-outline" style={{ fontSize: '0.85rem', borderColor: '#d97706', color: '#d97706' }}>Escalate</button>
                      )}

                      <Link to={`/results/${caseItem.id}`} className="chase-button-outline" style={{ fontSize: '0.85rem' }}>View Details</Link>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default PoliceDashboard;