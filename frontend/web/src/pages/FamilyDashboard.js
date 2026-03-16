import React, { useState, useEffect, useCallback } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import api from '../services/api';
import '../styles/ChaseUI.css';

const FamilyDashboard = () => {
  const { user, logout } = useAuth();
  const navigate = useNavigate();
  const [cases, setCases] = useState([]);
  const [loading, setLoading] = useState(true);
  const [stats, setStats] = useState({
    totalCases: 0,
    activeCases: 0,
    resolvedCases: 0
  });

  const fetchCases = useCallback(async () => {
    try {
      const response = await api.getMissingPersons();
      const allCases = Array.isArray(response.data) ? response.data : response.data.results;
      const userCases = allCases.filter(caseItem => caseItem.reported_by === user.id);
      setCases(userCases);

      setStats({
        totalCases: userCases.length,
        activeCases: userCases.filter(c => !['CLOSED'].includes(c.status)).length,
        resolvedCases: userCases.filter(c => c.status === 'CLOSED').length
      });
    } catch (error) {
      console.error('Error fetching cases:', error);
    } finally {
      setLoading(false);
    }
  }, [user]);

  useEffect(() => {
    if (user && user.role === 'family_member') {
      fetchCases();
    } else if (user) {
      navigate('/login');
    }
  }, [user, navigate, fetchCases]);

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  const handleRaiseCase = async (id) => {
    if (!window.confirm('Are you sure you want to raise this case to the police?')) return;
    try {
      await api.raiseCase(id);
      alert('Case successfully raised to the police.');
      fetchCases();
    } catch (error) {
      console.error('Error raising case:', error);
      alert('Failed to raise case.');
    }
  };

  const handleApproveClosure = async (id) => {
    if (!window.confirm('Are you sure you want to approve this match and close the case? (Dual Signature)')) return;
    try {
      await api.updateCaseStatus(id, 'CLOSED');
      alert('Case closed successfully. Data will be purged in 30 days.');
      fetchCases();
    } catch (error) {
      console.error('Error closing case:', error);
      alert('Failed to close case.');
    }
  };

  if (loading) return <div className="chase-body"><div className="chase-container">Loading your dashboard...</div></div>;

  return (
    <div className="chase-body">
      <div className="chase-header">
        <div className="chase-logo">Sura <span>Smart</span></div>
        <div style={{ display: 'flex', alignItems: 'center', gap: '20px' }}>
          <span style={{ color: 'white' }}>{user?.first_name} {user?.last_name}</span>
          <button onClick={handleLogout} className="chase-button-outline" style={{ color: 'white', borderColor: 'white', padding: '0.5rem 1rem' }}>Logout</button>
        </div>
      </div>

      <div className="chase-container">
        <h1 className="chase-title">Family Member Portal</h1>

        <div className="chase-grid">
          <Link to="/reported-cases" className="chase-card" style={{ textDecoration: 'none' }}>
            <div className="chase-stat-label">Total Cases Reported</div>
            <div className="chase-stat-value">{stats.totalCases}</div>
            <div className="chase-stat-action">View Reported Cases</div>
          </Link>

          <Link to="/active-searches" className="chase-card" style={{ textDecoration: 'none' }}>
            <div className="chase-stat-label">Active Searches</div>
            <div className="chase-stat-value">{stats.activeCases}</div>
            <div className="chase-stat-action">Manage Active Searches</div>
          </Link>

          <Link to="/resolved-cases" className="chase-card" style={{ textDecoration: 'none' }}>
            <div className="chase-stat-label">Cases Resolved</div>
            <div className="chase-stat-value">{stats.resolvedCases}</div>
            <div className="chase-stat-action">View Resolved Cases</div>
          </Link>
        </div>

        <div style={{ marginBottom: '40px' }}>
          <Link to="/report" className="chase-button" style={{ padding: '1rem 2rem', fontSize: '1.1rem' }}>
            + Report Missing Person
          </Link>
        </div>

        <div className="chase-section">
          <h2 style={{ marginBottom: '24px', color: 'var(--chase-blue-dark)' }}>Recent Cases</h2>
          {cases.length === 0 ? (
            <div className="chase-card" style={{ textAlign: 'center', padding: '60px' }}>
              <p style={{ color: 'var(--chase-gray-500)', marginBottom: '24px' }}>You haven't reported any missing persons yet.</p>
              <Link to="/report" className="chase-button">Start First Report</Link>
            </div>
          ) : (
            <div className="chase-card" style={{ padding: 0 }}>
              <div style={{ padding: '0 24px' }}>
                {cases.slice(0, 5).map(caseItem => (
                  <div key={caseItem.id} className="chase-list-item" style={{ flexDirection: 'column', alignItems: 'flex-start', gap: '10px' }}>
                    <div style={{ width: '100%', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                      <div>
                        <div style={{ fontWeight: '600', fontSize: '1.1rem', marginBottom: '4px' }}>{caseItem.full_name}</div>
                        <div style={{ fontSize: '0.85rem', color: 'var(--chase-gray-500)' }}>
                          Status: <span style={{ fontWeight: '600', color: 'var(--chase-blue)' }}>{caseItem.status}</span>
                        </div>
                        {/* Workflow Specific Messages */}
                        {caseItem.status === 'ESCALATED' && (
                          <div style={{ fontSize: '0.8rem', color: '#d97706', marginTop: '4px', fontWeight: '600' }}>
                            ⚠️ Status Report: Your Case has been escalated for further investigations.
                          </div>
                        )}
                        {caseItem.report_details && (
                          <div style={{ fontSize: '0.8rem', color: 'var(--chase-blue-dark)', marginTop: '4px', background: '#f0f9ff', padding: '4px 8px', borderRadius: '4px' }}>
                            📄 Case Findings: {caseItem.report_details}
                          </div>
                        )}
                      </div>
                      <div style={{ display: 'flex', gap: '12px' }}>
                        {caseItem.status === 'REPORTED' && (
                          <button onClick={() => handleRaiseCase(caseItem.id)} className="chase-button" style={{ padding: '6px 12px', fontSize: '0.85rem' }}>
                            Raise to Police
                          </button>
                        )}
                        {caseItem.status === 'PENDING_CLOSURE' && (
                          <button onClick={() => handleApproveClosure(caseItem.id)} className="chase-button" style={{ padding: '6px 12px', fontSize: '0.85rem', background: 'var(--chase-green)' }}>
                            Approve Closure
                          </button>
                        )}
                        <Link to={`/missing-person/${caseItem.id}`} className="chase-button-outline" style={{ padding: '6px 12px', fontSize: '0.85rem' }}>
                          Details
                        </Link>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
              {cases.length > 5 && (
                <div style={{ padding: '16px', textAlign: 'center', borderTop: '1px solid var(--chase-gray-100)' }}>
                  <Link to="/reported-cases" style={{ color: 'var(--chase-blue)', textDecoration: 'none', fontWeight: '600' }}>See all cases</Link>
                </div>
              )}
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default FamilyDashboard;