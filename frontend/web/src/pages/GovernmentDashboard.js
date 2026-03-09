import React, { useState, useEffect, useCallback } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import api from '../services/api';
import '../styles/ChaseUI.css';

const GovernmentDashboard = () => {
  const { user, logout } = useAuth();
  const navigate = useNavigate();
  const [cases, setCases] = useState([]);
  const [users, setUsers] = useState([]);
  const [loading, setLoading] = useState(true);
  const [stats, setStats] = useState({
    totalCases: 0,
    activeCases: 0,
    resolvedCases: 0,
    escalatedCases: 0
  });

  const fetchData = useCallback(async () => {
    try {
      const [casesResponse, usersResponse] = await Promise.all([
        api.getMissingPersons(),
        api.getUsers()
      ]);

      const casesData = Array.isArray(casesResponse.data) ? casesResponse.data : casesResponse.data.results || [];
      const usersData = Array.isArray(usersResponse.data) ? usersResponse.data : [];

      setCases(casesData);
      setUsers(usersData);

      setStats({
        totalCases: casesData.length,
        activeCases: casesData.filter(c => !['CLOSED'].includes(c.status)).length,
        resolvedCases: casesData.filter(c => c.status === 'CLOSED').length,
        escalatedCases: casesData.filter(c => c.status === 'ESCALATED').length
      });
    } catch (error) {
      console.error('Error fetching data:', error);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    if (user === null) return;
    if (user && user.role !== 'government_official') {
      navigate('/login');
      return;
    }
    if (user) fetchData();
  }, [user, navigate, fetchData]);

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  const handleReviewCase = async (caseId) => {
    const review = prompt("Enter official review and recommended action for Police:");
    if (!review) return;
    try {
      await api.submitReview(caseId, review);
      await api.updateCaseStatus(caseId, 'GOVERNMENT_REVIEW'); // Or back to UNDER_INVESTIGATION
      alert('Review sent to Police Officer.');
      fetchData();
    } catch (error) {
      console.error('Error submitting review:', error);
      alert('Failed to submit review.');
    }
  };

  if (user === null || loading) {
    return <div className="chase-body"><div className="chase-container">Loading government dashboard...</div></div>;
  }

  // Filter specifically for Escalated Cases for the main action area
  const escalatedCases = cases.filter(c => c.status === 'ESCALATED');

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
        <h1 className="chase-title">Government Official Portal</h1>

        <div className="chase-grid">
          <div className="chase-card">
            <div className="chase-stat-label">Total Cases</div>
            <div className="chase-stat-value">{stats.totalCases}</div>
          </div>
          <div className="chase-card">
            <div className="chase-stat-label">Active Cases</div>
            <div className="chase-stat-value">{stats.activeCases}</div>
          </div>
          <div className="chase-card">
            <div className="chase-stat-label">Resolved Cases</div>
            <div className="chase-stat-value">{stats.resolvedCases}</div>
          </div>
          <div className="chase-card" style={{ borderTop: '4px solid #d97706' }}>
            <div className="chase-stat-label">Escalated Cases</div>
            <div className="chase-stat-value" style={{ color: '#d97706' }}>{stats.escalatedCases}</div>
          </div>
        </div>

        <div className="chase-grid" style={{ gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))', marginBottom: '40px' }}>
          <Link to="/analytics" className="chase-card" style={{ textDecoration: 'none', borderTop: '4px solid var(--chase-blue)' }}>
            <h3 style={{ color: 'var(--chase-blue-dark)', marginBottom: '10px' }}>Analytics Dashboard</h3>
            <p style={{ color: 'var(--chase-gray-500)' }}>View system analytics and statistics</p>
          </Link>
          <Link to="/system-reports" className="chase-card" style={{ textDecoration: 'none', borderTop: '4px solid var(--chase-blue)' }}>
            <h3 style={{ color: 'var(--chase-blue-dark)', marginBottom: '10px' }}>System Reports</h3>
            <p style={{ color: 'var(--chase-gray-500)' }}>Generate comprehensive system reports</p>
          </Link>
        </div>

        <div className="chase-section">
          <h2 style={{ marginBottom: '24px', color: 'var(--chase-blue-dark)' }}>Escalated Cases (Requires Review)</h2>
          {escalatedCases.length === 0 ? (
            <div className="chase-card" style={{ textAlign: 'center', padding: '60px' }}>
              <p style={{ color: 'var(--chase-gray-500)' }}>No cases currently escalated for government review.</p>
            </div>
          ) : (
            <div className="chase-card" style={{ padding: 0 }}>
              <div style={{ padding: '0 24px' }}>
                {escalatedCases.map(caseItem => (
                  <div key={caseItem.id} className="chase-list-item" style={{ flexDirection: 'column', alignItems: 'flex-start', gap: '15px', padding: '20px 0' }}>
                    <div style={{ width: '100%', display: 'flex', justifyContent: 'space-between' }}>
                      <div>
                        <h3 style={{ margin: '0 0 5px 0', color: 'var(--chase-blue-dark)' }}>{caseItem.full_name}</h3>
                        <p style={{ margin: '0', fontSize: '0.9rem', color: 'var(--chase-gray-500)' }}>
                          Escalated: {new Date(caseItem.date_escalated || caseItem.date_reported).toLocaleDateString()}
                        </p>
                        <p style={{ margin: '5px 0 0 0', fontSize: '0.85rem', color: '#d97706', fontWeight: '600' }}>
                          ⚠️ National Security Interest
                        </p>
                      </div>
                      <span className="chase-status-pill" style={{ background: '#fef3c7', color: '#92400e' }}>
                        ESCALATED
                      </span>
                    </div>

                    <div style={{ width: '100%', display: 'flex', gap: '10px', borderTop: '1px solid var(--chase-gray-100)', paddingTop: '15px' }}>
                      <button onClick={() => handleReviewCase(caseItem.id)} className="chase-button" style={{ fontSize: '0.85rem', background: 'var(--chase-blue-dark)' }}>
                        Submit Review to Police
                      </button>
                      <Link to={`/results/${caseItem.id}`} className="chase-button-outline" style={{ fontSize: '0.85rem' }}>
                        View Details
                      </Link>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>

        <div className="chase-section" style={{ marginTop: '40px' }}>
          <h2 style={{ marginBottom: '24px', color: 'var(--chase-blue-dark)' }}>All Cases Overview</h2>
          <div className="chase-card" style={{ padding: 0 }}>
            <div style={{ padding: '0 24px' }}>
              {cases.slice(0, 5).map(caseItem => (
                <div key={caseItem.id} className="chase-list-item">
                  <div>
                    <div style={{ fontWeight: '600', fontSize: '1.1rem', marginBottom: '4px' }}>{caseItem.full_name}</div>
                    <div style={{ fontSize: '0.85rem', color: 'var(--chase-gray-500)' }}>
                      Status: <span style={{ fontWeight: '600', color: 'var(--chase-blue)' }}>{caseItem.status}</span>
                    </div>
                  </div>
                  <Link to={`/results/${caseItem.id}`} className="chase-button-outline" style={{ padding: '6px 12px', fontSize: '0.85rem' }}>
                    View Details
                  </Link>
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default GovernmentDashboard;