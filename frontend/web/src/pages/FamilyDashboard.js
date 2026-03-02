import React, { useState, useEffect, useCallback } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import api from '../services/api';
import '../styles/Dashboard.css';

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
      const userCases = response.data.filter(caseItem => caseItem.reported_by === user.id);
      setCases(userCases);

      setStats({
        totalCases: userCases.length,
        activeCases: userCases.filter(c => c.status === 'searching').length,
        resolvedCases: userCases.filter(c => c.status === 'found').length
      });
    } catch (error) {
      console.error('Error fetching cases:', error);
    } finally {
      setLoading(false);
    }
  }, [user]);

  useEffect(() => {
    if (user === null) {
      // User not loaded yet, wait
      return;
    }
    if (user && user.role !== 'family_member') {
      navigate('/login');
      return;
    }
    if (user) {
      fetchCases();
    }
  }, [user, navigate, fetchCases]);

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  if (user === null) {
    return <div className="loading">Loading your dashboard...</div>;
  }

  if (loading) {
    return <div className="loading">Loading your dashboard...</div>;
  }

  return (
    <div className="dashboard-container">
      <header className="dashboard-header">
        <div className="header-content">
          <h1><span className="logo-glitter-text">SuraSmart</span> - Family Member Portal</h1>
          <div className="user-info">
            <span>Welcome, {user?.first_name} {user?.last_name}</span>
            <span className="user-role">Family Member</span>
            <button onClick={handleLogout} className="btn-secondary">Logout</button>
          </div>
        </div>
      </header>

      <div className="dashboard-content">
        <div className="stats-grid">
          <div className="stat-card">
            <h3>Total Cases Reported</h3>
            <div className="stat-number">{stats.totalCases}</div>
          </div>
          <div className="stat-card">
            <h3>Active Searches</h3>
            <div className="stat-number">{stats.activeCases}</div>
          </div>
          <div className="stat-card">
            <h3>Cases Resolved</h3>
            <div className="stat-number">{stats.resolvedCases}</div>
          </div>
        </div>

        <div className="dashboard-actions">
          <Link to="/report" className="action-card">
            <h3>Report Missing Person</h3>
            <p>Submit a new missing person report</p>
          </Link>

          <Link to="/facial-search" className="action-card">
            <h3>Search Database</h3>
            <p>Search for matches in the facial recognition database</p>
          </Link>
        </div>

        <div className="recent-cases">
          <h2>Your Reported Cases</h2>
          {cases.length === 0 ? (
            <div className="no-cases">
              <p>You haven't reported any missing persons yet.</p>
              <Link to="/report" className="btn-primary">Report Your First Case</Link>
            </div>
          ) : (
            <div className="cases-grid">
              {(Array.isArray(cases) ? cases : []).map(caseItem => (
                <div key={caseItem.id} className="case-card">
                  <h3>{caseItem.full_name}</h3>
                  <p><strong>Status:</strong> {caseItem.status}</p>
                  <p><strong>Reported:</strong> {new Date(caseItem.date_reported).toLocaleDateString()}</p>
                  <p><strong>Last Seen:</strong> {caseItem.last_seen_location || 'Unknown'}</p>
                  <div className="case-actions">
                    <Link to={`/results/${caseItem.id}`} className="btn-secondary">
                      View Details
                    </Link>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default FamilyDashboard;