import React, { useState } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import api from '../services/api';
import '../styles/FacialRecognition.css';

const FacialRecognitionResults = () => {
  const navigate = useNavigate();
  const location = useLocation();
  const { user, logout } = useAuth();
  const [showDetails, setShowDetails] = useState(null);

  const [reportText, setReportText] = useState('');
  const [submitting, setSubmitting] = useState(false);

  const state = location.state || {};
  const { results = [], uploadedImage, hasMatch, error, missingPersonId } = state;

  const handleRetry = () => {
    navigate('/facial-search');
  };

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  const handleRoleChange = () => {
    navigate('/role-selector');
  };

  const toggleDetails = (id) => {
    setShowDetails(showDetails === id ? null : id);
  };

  const handleForwardForClosure = async () => {
    if (!missingPersonId) return;
    setSubmitting(true);
    try {
      if (reportText) {
        await api.submitPoliceReport(missingPersonId, reportText);
      }
      await api.forwardForClosure(missingPersonId);
      alert('Case forwarded to family for closure.');
      navigate('/police-dashboard');
    } catch (err) {
      console.error('Error forwarding for closure:', err);
      alert('Failed to forward case.');
    } finally {
      setSubmitting(false);
    }
  };

  const handleEscalate = async () => {
    if (!missingPersonId) return;
    setSubmitting(true);
    try {
      if (reportText) {
        await api.submitPoliceReport(missingPersonId, reportText);
      }
      await api.escalateCase(missingPersonId);
      alert('Case escalated to government official.');
      navigate('/police-dashboard');
    } catch (err) {
      console.error('Error escalating case:', err);
      alert('Failed to escalate case.');
    } finally {
      setSubmitting(false);
    }
  };

  const handleSubmitGovReport = async () => {
    if (!missingPersonId) return;
    setSubmitting(true);
    try {
      await api.submitGovernmentReport(missingPersonId, reportText);
      alert('Government analysis report submitted.');
      navigate('/government-dashboard');
    } catch (err) {
      console.error('Error submitting government report:', err);
      alert('Failed to submit report.');
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <div className="facial-recognition-container">
      {/* Header */}
      <header className="facial-header">
        <div className="facial-header-content">
          <div className="facial-logo">
            <h1 className="logo-glitter-text">🔍 SuraSmart</h1>
            <span>Search Results</span>
          </div>
          <div className="facial-user-menu">
            <span className="facial-user-info">
              {user?.first_name || user?.username} ({user?.role})
            </span>
            <button className="btn-secondary btn-sm" onClick={handleRoleChange}>
              Change Role
            </button>
            <button className="btn-danger btn-sm" onClick={handleLogout}>
              Logout
            </button>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="facial-main">
        {/* Uploaded Image Display */}
        {uploadedImage && (
          <div className="results-uploaded-image">
            <h3>Uploaded Image</h3>
            <img src={uploadedImage} alt="Uploaded" className="uploaded-preview" />
          </div>
        )}

        {/* Success Results */}
        {hasMatch && results.length > 0 ? (
          <div className="results-success-section">
            <div className="success-banner">
              <div className="success-icon">✅</div>
              <h2>Match Found!</h2>
              <p>We found {results.length} potential match{results.length !== 1 ? 'es' : ''} in our database</p>
            </div>

            <div className="matches-container">
              {results.map((match, index) => (
                <div key={index} className="match-card">
                  <div className="match-header">
                    <div className="match-info">
                      <h3>{match.missing_person?.full_name || 'Unknown'}</h3>
                      <div className="match-confidence">
                        <span className="confidence-label">Confidence Score:</span>
                        <span className="confidence-value">
                          {(match.match_confidence * 100).toFixed(1)}%
                        </span>
                        <div className="confidence-bar">
                          <div
                            className="confidence-fill"
                            style={{
                              width: `${match.match_confidence * 100}%`,
                              backgroundColor:
                                match.match_confidence > 0.8
                                  ? '#27ae60'
                                  : match.match_confidence > 0.6
                                    ? '#f39c12'
                                    : '#e74c3c',
                            }}
                          ></div>
                        </div>
                      </div>
                    </div>
                    <button
                      className="btn-expand"
                      onClick={() => toggleDetails(index)}
                    >
                      {showDetails === index ? '▼' : '▶'} Details
                    </button>
                  </div>

                  {showDetails === index && (
                    <div className="match-details">
                      <div className="details-grid">
                        <div className="detail-item">
                          <span className="detail-label">Name:</span>
                          <span className="detail-value">
                            {match.missing_person?.full_name || 'N/A'}
                          </span>
                        </div>
                        <div className="detail-item">
                          <span className="detail-label">Age:</span>
                          <span className="detail-value">
                            {match.missing_person?.age || 'N/A'}
                          </span>
                        </div>
                        <div className="detail-item">
                          <span className="detail-label">Gender:</span>
                          <span className="detail-value">
                            {match.missing_person?.gender
                              ? match.missing_person.gender.charAt(0).toUpperCase() +
                              match.missing_person.gender.slice(1)
                              : 'N/A'}
                          </span>
                        </div>
                        <div className="detail-item">
                          <span className="detail-label">Last Location:</span>
                          <span className="detail-value">
                            {match.missing_person?.last_seen_location || 'N/A'}
                          </span>
                        </div>
                        <div className="detail-item full-width">
                          <span className="detail-label">Description:</span>
                          <span className="detail-value">
                            {match.missing_person?.description || 'No description available'}
                          </span>
                        </div>
                      </div>

                      {match.source_image?.image_file && (
                        <div className="match-image-container">
                          <h4>Database Image:</h4>
                          <img
                            src={match.source_image.image_file}
                            alt="Database Match"
                            className="match-image"
                          />
                        </div>
                      )}
                    </div>
                  )}
                </div>
              ))}
            </div>

            {/* Analysis Report Section for Authorities */}
            {(user?.role === 'police_officer' || user?.role === 'government_official') && (
              <div className="analysis-report-section">
                <h3>{user.role === 'police_officer' ? 'Police Match Analysis Report' : 'Government Analysis Report'}</h3>
                <textarea
                  className="report-textarea"
                  placeholder="Enter your analysis findings here..."
                  value={reportText}
                  onChange={(e) => setReportText(e.target.value)}
                  disabled={submitting}
                ></textarea>

                <div className="workflow-actions">
                  {user.role === 'police_officer' && (
                    <>
                      <button
                        className="btn-success"
                        onClick={handleForwardForClosure}
                        disabled={submitting}
                      >
                        Forward to Family for Closure
                      </button>
                      <button
                        className="btn-warning"
                        onClick={handleEscalate}
                        disabled={submitting}
                      >
                        Escalate Case
                      </button>
                    </>
                  )}
                  {user.role === 'government_official' && (
                    <button
                      className="btn-primary"
                      onClick={handleSubmitGovReport}
                      disabled={submitting}
                    >
                      Submit Government Report & Approve
                    </button>
                  )}
                </div>
              </div>
            )}

            <div className="results-actions">
              <button className="btn-primary" onClick={handleRetry} disabled={submitting}>
                🔍 Search Again
              </button>
              <button
                className="btn-secondary"
                onClick={() => navigate(user.role === 'police_officer' ? '/police-dashboard' : user.role === 'government_official' ? '/government-dashboard' : '/family-dashboard')}
                disabled={submitting}
              >
                Back to Dashboard
              </button>
            </div>
          </div>
        ) : !hasMatch && !error ? (
          // No Match Found
          <div className="results-no-match-section">
            <div className="no-match-banner">
              <div className="no-match-icon">😔</div>
              <h2>No Match Found</h2>
              <p>
                Unfortunately, we didn't find a match for this image in our database.
                This person may not be in our system yet.
              </p>
            </div>

            <div className="no-match-suggestions">
              <h3>What You Can Do:</h3>
              <div className="suggestions-grid">
                <div className="suggestion-card">
                  <div className="suggestion-icon">📋</div>
                  <h4>Report Missing Person</h4>
                  <p>If you know this person is missing, help us create their profile</p>
                  <button className="btn-primary btn-sm">
                    Create Report
                  </button>
                </div>
                <div className="suggestion-card">
                  <div className="suggestion-icon">📸</div>
                  <h4>Try Different Image</h4>
                  <p>Upload another photo that may have better facial visibility</p>
                  <button className="btn-primary btn-sm" onClick={handleRetry}>
                    Upload New Image
                  </button>
                </div>
                <div className="suggestion-card">
                  <div className="suggestion-icon">📞</div>
                  <h4>Contact Support</h4>
                  <p>Reach out to authorities if you have additional information</p>
                  <button className="btn-secondary btn-sm">
                    Contact Us
                  </button>
                </div>
              </div>
            </div>

            <div className="apology-message">
              <p>
                We apologize that we couldn't find a match. Please try again with a different
                image or report the person if you believe they are missing.
              </p>
            </div>

            <div className="results-actions">
              <button className="btn-primary" onClick={handleRetry}>
                🔄 Retry Search
              </button>
              <button className="btn-secondary" onClick={() => navigate('/dashboard')}>
                Back to Dashboard
              </button>
            </div>
          </div>
        ) : null}

        {/* Error State */}
        {error && (
          <div className="results-error-section">
            <div className="error-banner">
              <div className="error-icon">⚠️</div>
              <h2>Search Error</h2>
              <p>{error}</p>
            </div>

            <div className="error-suggestions">
              <h3>What You Can Do:</h3>
              <ul className="suggestions-list">
                <li>Try uploading a different image with better facial visibility</li>
                <li>Ensure the image is clear and well-lit</li>
                <li>Make sure the file format is JPEG or PNG</li>
                <li>Check that the file size is under 5MB</li>
              </ul>
            </div>

            <div className="results-actions">
              <button className="btn-primary" onClick={handleRetry}>
                🔄 Try Again
              </button>
              <button className="btn-secondary" onClick={() => navigate('/dashboard')}>
                Back to Dashboard
              </button>
            </div>
          </div>
        )}
      </main>
    </div>
  );
};

export default FacialRecognitionResults;
