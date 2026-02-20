import React, { useState, useEffect, useCallback } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import api from '../services/api';
import '../styles/Dashboard.css';

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
      setCases(response.data);

      setStats({
        totalCases: response.data.length,
        activeCases: response.data.filter(c => c.status === 'searching').length,
        resolvedCases: response.data.filter(c => c.status === 'found').length,
        pendingVerification: response.data.filter(c => c.status === 'pending_verification').length
      });
    } catch (error) {
      console.error('Error fetching cases:', error);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    if (user === null) {
      // User not loaded yet, wait
      return;
    }
    if (user && user.role !== 'police_officer') {
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

  const updateCaseStatus = async (caseId, newStatus) => {
    try {
      await api.updateCaseStatus(caseId, newStatus);
      fetchCases(); // Refresh the cases
    } catch (error) {
      console.error('Error updating case status:', error);
    }
  };

  if (user === null) {
    return <div className="loading">Loading police dashboard...</div>;
  }

  if (loading) {
    return <div className="loading">Loading police dashboard...</div>;
  }

  return (
    <div className="dashboard-container">
      <header className="dashboard-header">
        <div className="header-content">
          <h1>SuraSmart - Police Officer Portal</h1>
          <div className="user-info">
            <span>Welcome, Officer {user?.first_name} {user?.last_name}</span>
            <span className="user-role">Police Officer - {user?.police_rank}</span>
            <button onClick={handleLogout} className="btn-secondary">Logout</button>
          </div>
        </div>
      </header>

      <div className="dashboard-content">
        <div className="stats-grid">
          <div className="stat-card">
            <h3>Total Cases</h3>
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
          <div className="stat-card">
            <h3>Pending Verification</h3>
            <div className="stat-number">{stats.pendingVerification}</div>
          </div>
        </div>

        <div className="dashboard-actions">
          <Link to="/facial-search" className="action-card">
            <h3>Facial Recognition Search</h3>
            <p>Search the database using facial recognition</p>
          </Link>

          <Link to="/bulk-upload" className="action-card">
            <h3>Bulk Image Upload</h3>
            <p>Upload multiple images for processing</p>
          </Link>

          <Link to="/reports" className="action-card">
            <h3>Generate Reports</h3>
            <p>View and generate case reports</p>
          </Link>
        </div>

        <div className="recent-cases">
          <h2>All Missing Persons Cases</h2>
          {cases.length === 0 ? (
            <div className="no-cases">
              <p>No cases reported yet.</p>
            </div>
          ) : (
            <div className="cases-grid">
              {(Array.isArray(cases) ? cases : []).map(caseItem => (
                <div key={caseItem.id} className="case-card">
                  <h3>{caseItem.full_name}</h3>
                  <p><strong>Status:</strong>
                    <select
                      value={caseItem.status}
                      onChange={(e) => updateCaseStatus(caseItem.id, e.target.value)}
                      className="status-select"
                    >
                      <option value="searching">Searching</option>
                      <option value="pending_verification">Pending Verification</option>
                      <option value="found">Found</option>
                      <option value="closed">Closed</option>
                    </select>
                  </p>
                  <p><strong>Reported:</strong> {new Date(caseItem.date_reported).toLocaleDateString()}</p>
                  <p><strong>Last Seen:</strong> {caseItem.last_seen_location || 'Unknown'}</p>
                  <p><strong>Reported by:</strong> {caseItem.reporter_name || 'Unknown'}</p>
                  <div className="case-actions">
                    <Link to={`/results/${caseItem.id}`} className="btn-secondary">
                      View Details
                    </Link>
                    <Link to={`/facial-search/${caseItem.id}`} className="btn-primary">
                      Search Matches
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

export default PoliceDashboard;