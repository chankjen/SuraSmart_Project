import React from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import '../styles/Home.css';

const Home = () => {
  const navigate = useNavigate();
  const { isAuthenticated, user } = useAuth();

  const handleGetStarted = () => {
    if (isAuthenticated) {
      navigate('/dashboard');
    } else {
      navigate('/login');
    }
  };

  return (
    <div className="home-container">
      {/* Navigation */}
      <nav className="home-nav">
        <div className="nav-container">
          <div className="nav-logo">
            <img className="logo-img" src="/images/SuraSmart_logo.png" alt="SuraSmart logo" />
            <div className="logo-text">
              <h1>SuraSmart</h1>
              <span className="tagline">Finding Hope, Connecting Lives</span>
            </div>
          </div>
          <div className="nav-links">
            {isAuthenticated ? (
              <>
                <span className="nav-user">Welcome, {user?.first_name || user?.username}!</span>
                <button className="nav-btn" onClick={() => navigate('/dashboard')}>
                  Dashboard
                </button>
              </>
            ) : (
              <>
                <button className="nav-btn nav-secondary" onClick={() => navigate('/login')}>
                  Login
                </button>
                <button className="nav-btn nav-primary" onClick={() => navigate('/register')}>
                  Register
                </button>
              </>
            )}
          </div>
        </div>
      </nav>

      {/* Hero Section */}
      <section className="hero">
        <div className="hero-content">
          <h2>Welcome to SuraSmart</h2>
          <p>An AI-powered platform for finding and reconnecting missing persons</p>
          <button className="hero-btn" onClick={handleGetStarted}>
            {isAuthenticated ? 'Go to Dashboard' : 'Get Started'}
          </button>
        </div>
      </section>

      {/* Features Section */}
      <section className="features">
        <h3>How SuraSmart Works</h3>
        <div className="features-grid">
          <div className="feature-card">
            <div className="feature-icon">📋</div>
            <h4>Report</h4>
            <p>Report a missing person with detailed information and photos</p>
          </div>
          <div className="feature-card">
            <div className="feature-icon">📸</div>
            <h4>Upload</h4>
            <p>Share facial recognition images for AI-powered matching</p>
          </div>
          <div className="feature-card">
            <div className="feature-icon">🔍</div>
            <h4>Search</h4>
            <p>Find matches across databases using advanced facial recognition</p>
          </div>
          <div className="feature-card">
            <div className="feature-icon">✅</div>
            <h4>Verify</h4>
            <p>Authorities verify and authenticate matched results</p>
          </div>
        </div>
      </section>

      {/* Roles Section */}
      <section className="roles-section">
        <h3>Different Access Levels</h3>
        <div className="roles-grid">
          <div className="role-card family-member">
            <h4>👨‍👩‍👧 Family Members</h4>
            <p className="role-desc">Report missing family members and track cases</p>
            <ul className="role-features">
              <li>✓ Report missing persons</li>
              <li>✓ Upload photos</li>
              <li>✓ Track your cases</li>
              <li>✗ Limited to own cases</li>
            </ul>
          </div>

          <div className="role-card police-officer">
            <h4>👮 Police Officers</h4>
            <p className="role-desc">Investigate cases and verify matches</p>
            <ul className="role-features">
              <li>✓ Access all cases</li>
              <li>✓ Verify matches</li>
              <li>✓ Modify records</li>
              <li>✓ Full database access</li>
            </ul>
          </div>

          <div className="role-card government">
            <h4>🏛️ Government Officials</h4>
            <p className="role-desc">Support national investigations and coordination</p>
            <ul className="role-features">
              <li>✓ Access all cases</li>
              <li>✓ Verify matches</li>
              <li>✓ Modify records</li>
              <li>✓ Generate reports</li>
            </ul>
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="cta-section">
        <h3>Ready to Help?</h3>
        <p>Join thousands of people using SuraSmart to bring loved ones home</p>
        <button className="cta-btn" onClick={handleGetStarted}>
          {isAuthenticated ? 'Access Your Dashboard' : 'Create Account Now'}
        </button>
      </section>

      {/* Footer */}
      <footer className="home-footer">
        <p>&copy; 2026 SuraSmart. Helping find missing persons worldwide.</p>
      </footer>
    </div>
  );
};

export default Home;
