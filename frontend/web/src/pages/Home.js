import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import '../styles/Home.css';


const Home = () => {
  const navigate = useNavigate();
  const { isAuthenticated, user } = useAuth();
  const [currentSlide, setCurrentSlide] = useState(0);
  const [isAutoPlaying, setIsAutoPlaying] = useState(true);

  // Slideshow data with hopeful messages
  const slideshowData = [
    {
      image: '/images/reunion1.jpg',
      title: 'Hope Reunited',
      message: 'Every second counts. With SuraSmart, families find closure and loved ones come home safely.'
    },
    {
      image: '/images/reunion2.webp',
      title: 'Never Give Up',
      message: 'Technology meets compassion. Our AI-powered search brings hope to thousands of waiting families.'
    },
    {
      image: '/images/reunion3.jpg',
      title: 'Together Again',
      message: 'From uncertainty to joy. SuraSmart bridges the gap between loss and reunion with precision and care.'
    },
    {
      image: '/images/reunion4.webp',
      title: 'A New Beginning',
      message: 'When families are reunited, communities heal. SuraSmart is dedicated to making every reunion possible.'
    }
  ];

  // Auto-advance slideshow
  useEffect(() => {
    if (!isAutoPlaying) return;
    
    const interval = setInterval(() => {
      setCurrentSlide((prev) => (prev + 1) % slideshowData.length);
    }, 6000); // Change slide every 6 seconds

    return () => clearInterval(interval);
  }, [isAutoPlaying, slideshowData.length]);

  const handleGetStarted = () => {
    if (isAuthenticated && user) {
      const dashboardRoutes = {
        'family_member': '/family-dashboard',
        'police_officer': '/police-dashboard',
        'government_official': '/government-dashboard'
      };
      navigate(dashboardRoutes[user.role] || '/login');
    } else {
      navigate('/login');
    }
  };

  const goToSlide = (index) => {
    setCurrentSlide(index);
    setIsAutoPlaying(false);
    // Resume autoplay after 10 seconds of manual interaction
    setTimeout(() => setIsAutoPlaying(true), 10000);
  };

  const nextSlide = () => {
    setCurrentSlide((prev) => (prev + 1) % slideshowData.length);
    setIsAutoPlaying(false);
    setTimeout(() => setIsAutoPlaying(true), 10000);
  };

  const prevSlide = () => {
    setCurrentSlide((prev) => (prev - 1 + slideshowData.length) % slideshowData.length);
    setIsAutoPlaying(false);
    setTimeout(() => setIsAutoPlaying(true), 10000);
  };

  return (
    <div className="home-container">
      {/* Navigation */}
      <nav className="home-nav">
        <div className="nav-container">
          <div className="nav-logo">
            <img 
              src="/images/SuraSmart_logo.png" 
              alt="SuraSmart Logo" 
              className="logo-img"
            />
            <div className="logo-text">
              <h1>SuraSmart</h1>
              <span className="tagline">Finding Hope, Connecting Lives</span>
            </div>
          </div>
          <div className="nav-links">
            <button
              className="nav-btn"
              style={{ background: 'transparent', border: '1px solid rgba(255,255,255,0.5)', color: 'white' }}
              onClick={() => navigate('/docs')}
            >
              Documentation
            </button>
            <button 
              className="nav-btn nav-admin" 
              onClick={() => navigate('/admin-dashboard')}
            >
              Admin Login
            </button>
            {isAuthenticated ? (
              <>
                <span className="nav-user">
                  Welcome, {user?.first_name || user?.username}!
                </span>
                <button 
                  className="nav-btn nav-secondary" 
                  onClick={() => navigate('/login')}
                >
                  Dashboard
                </button>
              </>
            ) : (
              <>
                <button 
                  className="nav-btn nav-secondary" 
                  onClick={() => navigate('/login')}
                >
                  Login
                </button>
                <button 
                  className="nav-btn nav-primary" 
                  onClick={() => navigate('/register')}
                >
                  Register
                </button>
              </>
            )}
          </div>
        </div>
      </nav>

      {/* Hero Section */}
      <section className="hero">
        <div className="hero-content fade-in">
          <h2>
            Welcome to <span className="logo-glitter-text">SuraSmart</span>
          </h2>
          <p>
            An AI-powered platform for finding and reconnecting missing persons. 
            Advanced facial recognition meets compassionate technology to bring families together.
          </p>
          <button className="hero-btn" onClick={handleGetStarted}>
            Get Started
          </button>
        </div>
      </section>

      {/* Slideshow Section - Replaced "Different Access Levels" */}
      <section className="slideshow-section">
        <div className="slideshow-container">
          <h3 className="slideshow-title slide-up">Stories of Hope & Reunion</h3>
          <div className="slideshow-wrapper">
            {slideshowData.map((slide, index) => (
              <div 
                key={index} 
                className={`slideshow-slide ${index === currentSlide ? 'active' : ''}`}
              >
                <img 
                  src={slide.image} 
                  alt={`Reunion story ${index + 1}`}
                  loading={index === 0 ? 'eager' : 'lazy'}
                />
                <div className="slideshow-message">
                  <h3>{slide.title}</h3>
                  <p>{slide.message}</p>
                </div>
              </div>
            ))}
            
            {/* Navigation Arrows */}
            <button 
              className="slideshow-arrow prev" 
              onClick={prevSlide}
              aria-label="Previous slide"
            >
              ‹
            </button>
            <button 
              className="slideshow-arrow next" 
              onClick={nextSlide}
              aria-label="Next slide"
            >
              ›
            </button>
            
            {/* Dots Indicator */}
            <div className="slideshow-controls">
              {slideshowData.map((_, index) => (
                <button
                  key={index}
                  className={`slideshow-dot ${index === currentSlide ? 'active' : ''}`}
                  onClick={() => goToSlide(index)}
                  aria-label={`Go to slide ${index + 1}`}
                />
              ))}
            </div>
          </div>
        </div>
      </section>

      {/* Features Section */}
      <section className="features">
        <h3 className="slide-up">How <span className="logo-glitter-text">SuraSmart</span> Works</h3>
        <div className="features-grid">
          <div className="feature-card slide-up">
            <div className="feature-icon">📋</div>
            <h4>Report</h4>
            <p>Report a missing person with detailed information and photos through our secure platform</p>
          </div>
          <div className="feature-card slide-up">
            <div className="feature-icon">📸</div>
            <h4>Upload</h4>
            <p>Share facial recognition images for AI-powered matching across multiple databases</p>
          </div>
          <div className="feature-card slide-up">
            <div className="feature-icon">🔍</div>
            <h4>Search</h4>
            <p>Find matches across morgue, jail, and police databases using advanced facial recognition</p>
          </div>
          <div className="feature-card slide-up">
            <div className="feature-icon">✅</div>
            <h4>Verify</h4>
            <p>Authorities verify and authenticate matched results with blockchain-backed security</p>
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="cta-section">
        <h3>Ready to Help?</h3>
        <p>
          Join thousands of people using SuraSmart to bring loved ones home. 
          Every report matters. Every search counts.
        </p>
        <button className="cta-btn" onClick={handleGetStarted}>
          {isAuthenticated ? 'Access Your Dashboard' : 'Create Account Now'}
        </button>
      </section>

      {/* Footer */}
      <footer className="home-footer">
        <p>© 2026 SuraSmart. Helping find missing persons worldwide. All rights reserved.</p>
      </footer>
    </div>
  );
};

export default Home;