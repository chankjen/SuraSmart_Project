import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import api from '../services/api';
import '../styles/DashboardNew.css';

const Dashboard = () => {
  const navigate = useNavigate();
  const { user, logout, isAuthenticated } = useAuth();
  const [stats, setStats] = useState({ cases: 0, matches: 0, notifications: 0 });
  const [loading, setLoading] = useState(true);
  const [menuOpen, setMenuOpen] = useState(false);

  useEffect(() => {
    if (!isAuthenticated) {
      navigate('/login');
      return;
    }

    const fetchStats = async () => {
      try {
        const casesRes = await api.getMissingPersons({ limit: 1 });
        const matchesRes = await api.getMatches({ limit: 1 });

        setStats({
          cases: casesRes.data.count || 0,
          matches: matchesRes.data.count || 0,
          notifications: 0,
        });
      } catch (err) {
        console.error('Failed to fetch stats:', err);
      } finally {
        setLoading(false);
      }
    };

    fetchStats();
  }, [isAuthenticated, navigate]);

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  const canVerifyMatches = user?.role === 'police_officer' || user?.role === 'government_official';
  const canAccessAllCases = user?.role === 'police_officer' || user?.role === 'government_official';
  const isFamilyMember = user?.role === 'family_member';

  const getRoleDisplay = (role) => {
    const roleMap = {
      'family_member': '👨‍👩‍👧‍👦 Family Member',
      'police_officer': '👮 Police Officer',
      'government_official': '🏛️ Government Official',
    };
    return roleMap[role] || role;
  };

  const getWelcomeMessage = () => {
    if (isFamilyMember) return 'Welcome back! You can report missing family members and track their status.';
    if (user?.role === 'police_officer') return 'Welcome back! You have access to all cases and can verify facial matches.';
    if (user?.role === 'government_official') return 'Welcome back! You have full administrative access to all cases and data.';
    return 'Welcome to SuraSmart!';
  };

  const getQuickActions = () => {
    const actions = [
      { label: 'Report Missing Person', icon: '📋', action: '/report', show: true },
      { label: 'Search Cases', icon: '🔍', action: '/search', show: true },
      { label: 'Upload Image', icon: '📷', action: '/upload', show: true },
    ];

    if (canVerifyMatches) actions.push({ label: 'Verify Matches', icon: '✓', action: '/matches', show: true });
    return actions.filter(a => a.show);
  };

  const getResources = () => {
    const baseResources = [
      { name: 'View My Cases', available: true, desc: 'Cases you reported' },
      { name: 'Upload Images', available: true, desc: 'Add facial images for matching' },
      { name: 'View Matches', available: true, desc: 'Potential matches found' },
    ];

    if (canAccessAllCases) {
      return [
        { name: 'All Cases', available: true, desc: 'Access to all missing person cases' },
        { name: 'Verify Matches', available: true, desc: 'Confirm facial recognition matches' },
        { name: 'View All Images', available: true, desc: 'Browse all uploaded images' },
        { name: 'Generate Reports', available: true, desc: 'Create statistics and reports' },
        { name: 'User Management', available: user?.is_staff, desc: 'Manage user accounts' },
      ];
    }

    return baseResources;
  };

  if (loading) return (
    <div className="dashboard-container">
      <div className="loading">Loading dashboard...</div>
    </div>
  );

  return (
    <div className="dashboard-container">
      <header className="dashboard-header">
        <div className="header-content">
          <div className="logo-section">
            <h1>SuraSmart</h1>
            <span className="logo-tagline">Facial Recognition System</span>
          </div>

          <div className="header-actions">
            <div className="user-info">
              <div className="user-name">{user?.first_name || user?.username}</div>
              <div className="user-role">{getRoleDisplay(user?.role)}</div>
            </div>

            <button className="menu-toggle" onClick={() => setMenuOpen(!menuOpen)}>☰</button>
            <button onClick={handleLogout} className="btn-secondary">Logout</button>
          </div>
        </div>
      </header>

      <div className="dashboard-content">
        <div className="welcome-section">
          <div className="welcome-card">
            <h2>👋 {getWelcomeMessage()}</h2>
            <p className="stats-summary">
              System Status: <span className="status-online">● Online</span>
              {isFamilyMember && ` | Your Cases: ${stats.cases}`}
              {canAccessAllCases && ` | Total Cases: ${stats.cases} | Potential Matches: ${stats.matches}`}
            </p>
          </div>
        </div>

        <div className="stats-grid">
          <div className="stat-card">
            <div className="stat-icon">📋</div>
            <div className="stat-content"><h3>Cases</h3><p className="stat-number">{stats.cases}</p></div>
          </div>

          <div className="stat-card">
            <div className="stat-icon">✓</div>
            <div className="stat-content"><h3>Potential Matches</h3><p className="stat-number">{stats.matches}</p></div>
          </div>

          <div className="stat-card">
            <div className="stat-icon">🔔</div>
            <div className="stat-content"><h3>Notifications</h3><p className="stat-number">{stats.notifications}</p></div>
          </div>
        </div>

        <div className="action-buttons">
          <button onClick={() => navigate('/report')} className="btn-primary btn-large">+ Report Missing Person</button>
          <button onClick={() => navigate('/search')} className="btn-primary btn-large">🔍 Search</button>
        </div>

        <div className="quick-actions-section">
          <h3>Quick Actions</h3>
          <div className="actions-grid">
            {getQuickActions().map((action, idx) => (
              <button key={idx} className="action-btn" onClick={() => navigate(action.action)}>
                <span className="action-icon">{action.icon}</span>
                <span className="action-label">{action.label}</span>
              </button>
            ))}
          </div>
        </div>

        <div className="resources-section">
          <h3>📦 Available Resources</h3>
          <div className="resources-grid">
            {getResources().map((resource, idx) => (
              <div key={idx} className={`resource-card ${resource.available ? 'available' : 'unavailable'}`}>
                <h4>{resource.name}</h4>
                <p>{resource.desc}</p>
                <span className="resource-status">{resource.available ? '✓ Available' : '🔒 Not Available'}</span>
              </div>
            ))}
          </div>
        </div>

        <div className="guide-section">
          <h3>📖 How to Use</h3>
          <div className="guide-content">
            {isFamilyMember && (
              <div className="guide-card">
                <h4>👨‍👩‍👧‍👦 Family Member Guide</h4>
                <ol>
                  <li><strong>Report Missing Person:</strong> Click "Report" to file a new missing person case with photos and details</li>
                  <li><strong>Upload Images:</strong> Add high-quality facial photos for better matching accuracy</li>
                  <li><strong>Monitor Status:</strong> Track the status of your cases in real-time</li>
                  <li><strong>Receive Updates:</strong> Get notifications when potential matches are found</li>
                </ol>
              </div>
            )}

            {user?.role === 'police_officer' && (
              <div className="guide-card">
                <h4>👮 Police Officer Guide</h4>
                <ol>
                  <li><strong>View All Cases:</strong> Access all missing person reports in the system</li>
                  <li><strong>Verify Matches:</strong> Review and confirm facial recognition matches</li>
                  <li><strong>Manage Cases:</strong> Update case status based on investigation progress</li>
                  <li><strong>Generate Reports:</strong> Create statistics and search patterns for analysis</li>
                </ol>
              </div>
            )}

            {user?.role === 'government_official' && (
              <div className="guide-card">
                <h4>🏛️ Government Official Guide</h4>
                <ol>
                  <li><strong>Full System Access:</strong> Complete control over all cases, images, and data</li>
                  <li><strong>Manage Users:</strong> Create and manage accounts for police and other officials</li>
                  <li><strong>Verify Matches:</strong> Review and confirm facial recognition results</li>
                  <li><strong>System Reports:</strong> Generate comprehensive reports for policy and analysis</li>
                </ol>
              </div>
            )}
          </div>
        </div>

      </div>
    </div>
  );
};

export default Dashboard;
