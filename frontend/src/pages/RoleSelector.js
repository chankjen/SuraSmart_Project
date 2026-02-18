import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import '../styles/RoleSelector.css';

const RoleSelector = () => {
  const navigate = useNavigate();
  const { user, selectRole } = useAuth();
  const [selectedRole, setSelectedRole] = useState(null);
  const [loading, setLoading] = useState(false);

  const roles = [
    {
      id: 'family_member',
      name: 'Family Member',
      icon: '👨‍👩‍👧‍👦',
      description: 'Report missing persons and track cases',
      features: [
        'Report missing family members',
        'Upload photos and details',
        'Track case progress',
        'Receive notifications'
      ]
    },
    {
      id: 'police_officer',
      icon: '👮',
      name: 'Police Officer',
      description: 'Access all cases and verify matches',
      features: [
        'View all missing person cases',
        'Verify facial recognition matches',
        'Access investigation data',
        'Generate reports'
      ]
    },
    {
      id: 'government_official',
      icon: '🏛️',
      name: 'Government Official',
      description: 'Full administrative access',
      features: [
        'Full system access',
        'Verify all matches',
        'Manage users',
        'Generate statistics'
      ]
    }
  ];

  const handleContinue = async () => {
    if (!selectedRole) {
      alert('Please select a role to continue');
      return;
    }

    setLoading(true);
    try {
      await selectRole(selectedRole);
      // After role selection, go to facial recognition search
      navigate('/facial-search');
    } catch (err) {
      console.error('Error selecting role:', err);
      alert('Failed to select role. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="role-selector-container">
      <div className="role-selector-content">
        <div className="role-header">
          <h1>Welcome, {user?.first_name || user?.username}!</h1>
          <p>Please select your role to continue</p>
        </div>

        <div className="roles-grid">
          {roles.map((role) => (
            <div
              key={role.id}
              className={`role-card ${selectedRole === role.id ? 'selected' : ''}`}
              onClick={() => setSelectedRole(role.id)}
            >
              <div className="role-icon">{role.icon}</div>
              <h3>{role.name}</h3>
              <p className="role-description">{role.description}</p>
              <ul className="role-features-list">
                {role.features.map((feature, idx) => (
                  <li key={idx}>
                    <span className="checkmark">✓</span>
                    {feature}
                  </li>
                ))}
              </ul>
              <div className="role-selector-radio">
                <input
                  type="radio"
                  name="role"
                  value={role.id}
                  checked={selectedRole === role.id}
                  onChange={() => setSelectedRole(role.id)}
                  className="role-radio-input"
                />
              </div>
            </div>
          ))}
        </div>

        <div className="role-selector-actions">
          <button
            className="btn-primary btn-large"
            onClick={handleContinue}
            disabled={loading || !selectedRole}
          >
            {loading ? 'Loading...' : 'Continue to Facial Recognition'}
          </button>
          <button
            className="btn-secondary"
            onClick={() => navigate('/dashboard')}
            disabled={loading}
          >
            Go to Dashboard
          </button>
        </div>
      </div>
    </div>
  );
};

export default RoleSelector;
