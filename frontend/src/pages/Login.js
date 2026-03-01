import React, { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import '../styles/Auth.css';

const Login = () => {
  const navigate = useNavigate();
  const { login } = useAuth();
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [formData, setFormData] = useState({
    username: '',
    password: '',
    role: 'family_member',
    national_id: '',
    service_id: '',
    police_rank: '',
    government_security_id: '',
    government_position: '',
    position_specify: '',
  });

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData((prev) => ({
      ...prev,
      [name]: value,
    }));
  };

  const handleRoleChange = (e) => {
    const newRole = e.target.value;
    setFormData((prev) => ({
      ...prev,
      role: newRole,
      // Clear role-specific fields when role changes
      national_id: newRole === 'family_member' ? prev.national_id : '',
      service_id: newRole === 'police_officer' ? prev.service_id : '',
      police_rank: newRole === 'police_officer' ? prev.police_rank : '',
      government_security_id: newRole === 'government_official' ? prev.government_security_id : '',
      government_position: newRole === 'government_official' ? prev.government_position : '',
      position_specify: newRole === 'government_official' && prev.government_position === 'other' ? prev.position_specify : '',
    }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError(null);

    try {
      await login(formData.username, formData.password);
      // Navigate based on role
      const roleRoutes = {
        'family_member': '/family-dashboard',
        'police_officer': '/police-dashboard',
        'government_official': '/government-dashboard',
        'admin': '/admin-dashboard',
      };
      navigate(roleRoutes[formData.role] || '/dashboard');
    } catch (err) {
      setError(err.response?.data?.detail || 'Login failed. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  // Demo users for quick login testing
  const demoUsers = [
    {
      username: 'alex',
      password: 'family123',
      role: 'Family Member',
      national_id: '12345678'
    },
    {
      username: 'amanda',
      password: 'family123',
      role: 'Family Member',
      national_id: '87654321'
    },
    {
      username: 'bernard',
      password: 'police456',
      role: 'Police Officer',
      service_id: '11111111',
      police_rank: 'lieutenant'
    },
    {
      username: 'betty',
      password: 'police456',
      role: 'Police Officer',
      service_id: '22222222',
      police_rank: 'general'
    },
    {
      username: 'cate',
      password: 'official789',
      role: 'Government Official',
      government_security_id: '33333333',
      government_position: 'cs'
    },
    {
      username: 'dan',
      password: 'official789',
      role: 'Government Official',
      government_security_id: '44444444',
      government_position: 'ps'
    },
  ];

  const quickLogin = async (demoUser) => {
    // Populate form with demo user data
    const roleMapping = {
      'Family Member': 'family_member',
      'Police Officer': 'police_officer',
      'Government Official': 'government_official'
    };

    setFormData({
      username: demoUser.username,
      password: demoUser.password,
      role: roleMapping[demoUser.role],
      national_id: demoUser.national_id || '',
      service_id: demoUser.service_id || '',
      police_rank: demoUser.police_rank || '',
      government_security_id: demoUser.government_security_id || '',
      government_position: demoUser.government_position || '',
      position_specify: '',
    });

    // Submit the form
    setLoading(true);
    setError(null);

    try {
      const user = await login(demoUser.username, demoUser.password);
      const userRole = user?.role || 'family_member';

      const roleRoutes = {
        'family_member': '/family-dashboard',
        'police_officer': '/police-dashboard',
        'government_official': '/government-dashboard',
        'admin': '/admin-dashboard',
      };

      // Small delay to ensure state is updated
      setTimeout(() => {
        navigate(roleRoutes[userRole] || '/dashboard');
      }, 100);
    } catch (err) {
      console.error('Login failed:', err);
      setError(err.response?.data?.detail || 'Login failed. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="auth-container">
      <div className="auth-box">
        <h1 className="logo-glitter-text">SuraSmart</h1>
        <h2>Login</h2>

        {error && <div className="error-message">{error}</div>}

        <form onSubmit={handleSubmit}>
          <div className="form-group">
            <label htmlFor="username">Username</label>
            <input
              type="text"
              id="username"
              name="username"
              value={formData.username}
              onChange={handleChange}
              required
              disabled={loading}
              placeholder="Enter username"
            />
          </div>

          <div className="form-group">
            <label htmlFor="password">Password</label>
            <input
              type="password"
              id="password"
              name="password"
              value={formData.password}
              onChange={handleChange}
              required
              disabled={loading}
              placeholder="Enter password"
            />
          </div>

          <div className="form-group">
            <label htmlFor="role">User Category</label>
            <select
              id="role"
              name="role"
              value={formData.role}
              onChange={handleRoleChange}
              disabled={loading}
              required
            >
              <option value="family_member">Family Member</option>
              <option value="police_officer">Police Officer</option>
              <option value="government_official">Government Official</option>
            </select>
          </div>

          {/* Family Member Fields */}
          {formData.role === 'family_member' && (
            <div className="form-group">
              <label htmlFor="national_id">National ID (8 digits)</label>
              <input
                type="text"
                id="national_id"
                name="national_id"
                value={formData.national_id}
                onChange={handleChange}
                required
                disabled={loading}
                placeholder="12345678"
                pattern="[0-9]{8}"
                maxLength="8"
              />
              <small className="form-hint">Enter your 8-digit National ID number</small>
            </div>
          )}

          {/* Police Officer Fields */}
          {formData.role === 'police_officer' && (
            <>
              <div className="form-group">
                <label htmlFor="service_id">Service ID (8 digits)</label>
                <input
                  type="text"
                  id="service_id"
                  name="service_id"
                  value={formData.service_id}
                  onChange={handleChange}
                  required
                  disabled={loading}
                  placeholder="12345678"
                  pattern="[0-9]{8}"
                  maxLength="8"
                />
                <small className="form-hint">Enter your 8-digit Service ID</small>
              </div>

              <div className="form-group">
                <label htmlFor="police_rank">Police Rank</label>
                <select
                  id="police_rank"
                  name="police_rank"
                  value={formData.police_rank}
                  onChange={handleChange}
                  required
                  disabled={loading}
                >
                  <option value="">Select Rank</option>
                  <option value="ig">Inspector-General (IG)</option>
                  <option value="dig">Deputy Inspector-General (DIG)</option>
                  <option value="saig">Senior Assistant Inspector-General (SAIG)</option>
                  <option value="aig">Assistant Inspector-General (AIG)</option>
                  <option value="ssp">Senior Superintendent of Police (SSP)</option>
                  <option value="sp">Superintendent of Police (SP)</option>
                  <option value="asp">Assistant Superintendent of Police (ASP)</option>
                  <option value="ci">Chief Inspector (CI)</option>
                  <option value="ip">Inspector of Police (IP)</option>
                  <option value="ssgt">Senior Sergeant (SSgt)</option>
                  <option value="sgt">Sergeant (Sgt)</option>
                  <option value="cpl">Corporal (Cpl)</option>
                  <option value="constable">Constable</option>
                </select>
              </div>
            </>
          )}

          {/* Government Official Fields */}
          {formData.role === 'government_official' && (
            <>
              <div className="form-group">
                <label htmlFor="government_security_id">Government Security ID (8 digits)</label>
                <input
                  type="text"
                  id="government_security_id"
                  name="government_security_id"
                  value={formData.government_security_id}
                  onChange={handleChange}
                  required
                  disabled={loading}
                  placeholder="12345678"
                  pattern="[0-9]{8}"
                  maxLength="8"
                />
                <small className="form-hint">Enter your 8-digit Government Security ID</small>
              </div>

              <div className="form-group">
                <label htmlFor="government_position">Government Position</label>
                <select
                  id="government_position"
                  name="government_position"
                  value={formData.government_position}
                  onChange={handleChange}
                  required
                  disabled={loading}
                >
                  <option value="">Select Position</option>
                  <option value="cs">CS</option>
                  <option value="ps">PS</option>
                  <option value="security_officer">Security Officer</option>
                  <option value="other">Other - specify</option>
                </select>
              </div>

              {formData.government_position === 'other' && (
                <div className="form-group">
                  <label htmlFor="position_specify">Specify Position</label>
                  <input
                    type="text"
                    id="position_specify"
                    name="position_specify"
                    value={formData.position_specify}
                    onChange={handleChange}
                    required
                    disabled={loading}
                    placeholder="Enter your position"
                  />
                </div>
              )}
            </>
          )}

          <button type="submit" disabled={loading} className="btn-primary">
            {loading ? 'Logging in...' : 'Login'}
          </button>
        </form>

        <p className="auth-link">
          Don't have an account? <Link to="/register">Register here</Link>
        </p>

        {/* Demo Users Section */}
        <div className="demo-section">
          <h3>Demo Users (Testing)</h3>
          <p style={{ fontSize: '0.85em', color: '#666', marginBottom: '10px' }}>
            Click to populate credentials:
          </p>
          <div className="demo-users-grid">
            {demoUsers.map((user, idx) => (
              <div key={idx} className="demo-user-card">
                <button
                  type="button"
                  className="demo-user-btn"
                  onClick={() => quickLogin(user)}
                  disabled={loading}
                >
                  <strong>{user.username}</strong>
                  <small>{user.role}</small>
                  <small style={{ fontSize: '0.7em', color: '#888' }}>
                    {user.role === 'Family Member' && `ID: ${user.national_id}`}
                    {user.role === 'Police Officer' && `ID: ${user.service_id}`}
                    {user.role === 'Government Official' && `ID: ${user.government_security_id}`}
                  </small>
                </button>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
};

export default Login;
