import React, { useState, useEffect, useCallback } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import api from '../services/api';
import '../styles/Dashboard.css';

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
    totalUsers: 0,
    verifiedUsers: 0,
    unverifiedUsers: 0
  });

  const fetchData = useCallback(async () => {
    try {
      const [casesResponse, usersResponse] = await Promise.all([
        api.getMissingPersons(),
        api.getUsers()
      ]);

      setCases(Array.isArray(casesResponse.data) ? casesResponse.data : []);
      setUsers(Array.isArray(usersResponse.data) ? usersResponse.data : []);

      const casesData = Array.isArray(casesResponse.data) ? casesResponse.data : [];
      const usersData = Array.isArray(usersResponse.data) ? usersResponse.data : [];

      setStats({
        totalCases: casesData.length,
        activeCases: casesData.filter(c => c.status === 'searching').length,
        resolvedCases: casesData.filter(c => c.status === 'found').length,
        totalUsers: usersData.length,
        verifiedUsers: usersData.filter(u => u.is_verified).length,
        unverifiedUsers: usersData.filter(u => !u.is_verified).length
      });
    } catch (error) {
      console.error('Error fetching data:', error);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    if (user === null) {
      // User not loaded yet, wait
      return;
    }
    if (user && user.role !== 'government_official') {
      navigate('/login');
      return;
    }
    if (user) {
      fetchData();
    }
  }, [user, navigate, fetchData]);

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  const verifyUser = async (userId) => {
    try {
      await api.verifyUser(userId);
      fetchData(); // Refresh the data
    } catch (error) {
      console.error('Error verifying user:', error);
    }
  };

  const updateCaseStatus = async (caseId, newStatus) => {
    try {
      await api.updateCaseStatus(caseId, newStatus);
      fetchData(); // Refresh the data
    } catch (error) {
      console.error('Error updating case status:', error);
    }
  };

  if (user === null) {
    return <div className="loading">Loading government dashboard...</div>;
  }

  if (loading) {
    return <div className="loading">Loading government dashboard...</div>;
  }

  return (
    <div className="dashboard-container">
      <header className="dashboard-header">
        <div className="header-content">
          <h1>SuraSmart - Government Official Portal</h1>
          <div className="user-info">
            <span>Welcome, {user?.first_name} {user?.last_name}</span>
            <span className="user-role">Government Official - {user?.government_position}</span>
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
            <h3>Active Cases</h3>
            <div className="stat-number">{stats.activeCases}</div>
          </div>
          <div className="stat-card">
            <h3>Resolved Cases</h3>
            <div className="stat-number">{stats.resolvedCases}</div>
          </div>
          <div className="stat-card">
            <h3>Total Users</h3>
            <div className="stat-number">{stats.totalUsers}</div>
          </div>
          <div className="stat-card">
            <h3>Verified Users</h3>
            <div className="stat-number">{stats.verifiedUsers}</div>
          </div>
          <div className="stat-card">
            <h3>Unverified Users</h3>
            <div className="stat-number">{stats.unverifiedUsers}</div>
          </div>
        </div>

        <div className="dashboard-actions">
          <Link to="/facial-search" className="action-card">
            <h3>Advanced Facial Search</h3>
            <p>Access full facial recognition database</p>
          </Link>

          <Link to="/user-management" className="action-card">
            <h3>User Management</h3>
            <p>Manage user accounts and permissions</p>
          </Link>

          <Link to="/system-reports" className="action-card">
            <h3>System Reports</h3>
            <p>Generate comprehensive system reports</p>
          </Link>

          <Link to="/analytics" className="action-card">
            <h3>Analytics Dashboard</h3>
            <p>View system analytics and statistics</p>
          </Link>
        </div>

        <div className="admin-sections">
          <div className="section">
            <h2>Recent Cases</h2>
            <div className="cases-grid">
              {(Array.isArray(cases) ? cases.slice(0, 5) : []).map(caseItem => (
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
                  <div className="case-actions">
                    <Link to={`/results/${caseItem.id}`} className="btn-secondary">
                      View Details
                    </Link>
                  </div>
                </div>
              ))}
            </div>
          </div>

          <div className="section">
            <h2>Unverified Users</h2>
            <div className="users-grid">
              {users.filter(u => !u.is_verified).slice(0, 5).map(userItem => (
                <div key={userItem.id} className="user-card">
                  <h3>{userItem.first_name} {userItem.last_name}</h3>
                  <p><strong>Email:</strong> {userItem.email}</p>
                  <p><strong>Role:</strong> {userItem.role}</p>
                  <p><strong>Registered:</strong> {new Date(userItem.date_joined).toLocaleDateString()}</p>
                  <div className="user-actions">
                    <button
                      onClick={() => verifyUser(userItem.id)}
                      className="btn-primary"
                    >
                      Verify User
                    </button>
                  </div>
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