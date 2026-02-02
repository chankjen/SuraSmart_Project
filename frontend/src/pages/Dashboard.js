import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import api from '../services/api';
import '../styles/Dashboard.css';

const Dashboard = () => {
  const navigate = useNavigate();
  const { user, logout } = useAuth();
  const [missingPersons, setMissingPersons] = useState([]);
  const [notifications, setNotifications] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [filter, setFilter] = useState('all');

  useEffect(() => {
    fetchData();
  }, []);

  const fetchData = async () => {
    try {
      const params = filter !== 'all' ? { status: filter } : {};
      const [personsRes, notificationsRes] = await Promise.all([
        api.getMissingPersons(params),
        api.getNotifications({ limit: 5 }),
      ]);

      setMissingPersons(personsRes.data.results || []);
      setNotifications(notificationsRes.data.results || []);
      setError(null);
    } catch (err) {
      setError('Failed to load dashboard');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  const handleViewResults = (personId) => {
    navigate(`/results/${personId}`);
  };

  if (loading) {
    return (
      <div className="dashboard-container">
        <div className="loading">Loading dashboard...</div>
      </div>
    );
  }

  return (
    <div className="dashboard-container">
      <header className="dashboard-header">
        <div className="header-content">
          <h1>SuraSmart Dashboard</h1>
          <div className="header-actions">
            <span className="user-info">
              Welcome, {user?.first_name || user?.username}!
            </span>
            <button onClick={handleLogout} className="btn-secondary">
              Logout
            </button>
          </div>
        </div>
      </header>

      <div className="dashboard-content">
        <div className="action-buttons">
          <button
            onClick={() => navigate('/report')}
            className="btn-primary btn-large"
          >
            + Report Missing Person
          </button>
          <button
            onClick={() => navigate('/search')}
            className="btn-primary btn-large"
          >
            🔍 Search
          </button>
        </div>

        {error && <div className="error-message">{error}</div>}

        {notifications.length > 0 && (
          <div className="section notifications-section">
            <h2>Recent Notifications</h2>
            <div className="notifications-list">
              {notifications.map((notif) => (
                <div key={notif.id} className="notification-item">
                  <h4>{notif.title}</h4>
                  <p>{notif.message}</p>
                  <span className="notification-time">
                    {new Date(notif.created_at).toLocaleString()}
                  </span>
                </div>
              ))}
            </div>
          </div>
        )}

        <div className="section">
          <div className="section-header">
            <h2>Missing Persons</h2>
            <div className="filter-buttons">
              {['all', 'reported', 'searching', 'found'].map((status) => (
                <button
                  key={status}
                  onClick={() => {
                    setFilter(status);
                    setLoading(true);
                  }}
                  className={`filter-btn ${filter === status ? 'active' : ''}`}
                >
                  {status.charAt(0).toUpperCase() + status.slice(1)}
                </button>
              ))}
            </div>
          </div>

          {missingPersons.length === 0 ? (
            <div className="no-results">
              <p>No missing persons found. Start by reporting one.</p>
            </div>
          ) : (
            <div className="persons-grid">
              {missingPersons.map((person) => (
                <div key={person.id} className="person-card">
                  <div className="person-header">
                    <h3>{person.full_name}</h3>
                    <span className={`status-badge status-${person.status}`}>
                      {person.status.toUpperCase()}
                    </span>
                  </div>

                  <div className="person-details">
                    {person.age && <p><strong>Age:</strong> {person.age}</p>}
                    {person.gender && <p><strong>Gender:</strong> {person.gender}</p>}
                    {person.last_seen_location && (
                      <p><strong>Last Seen:</strong> {person.last_seen_location}</p>
                    )}
                  </div>

                  <div className="person-description">
                    {person.description && <p>{person.description}</p>}
                  </div>

                  <div className="person-stats">
                    <span>{person.match_count || 0} matches</span>
                    <span>Reported: {new Date(person.date_reported).toLocaleDateString()}</span>
                  </div>

                  <div className="person-actions">
                    <button
                      onClick={() => handleViewResults(person.id)}
                      className="btn-primary btn-small"
                    >
                      View Results
                    </button>
                    <button
                      onClick={() => navigate(`/missing-person/${person.id}/upload`)}
                      className="btn-secondary btn-small"
                    >
                      Upload Image
                    </button>
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

export default Dashboard;
