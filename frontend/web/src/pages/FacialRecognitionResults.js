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
  const [showContact, setShowContact] = useState(false);

  const [reportText, setReportText] = useState('');
  const [submitting, setSubmitting] = useState(false);

  const state = location.state || {};
  const { results = [], uploadedImage, hasMatch, error, missingPersonId } = state;

  const isSuccessPath = location.pathname === '/facial-results/success';
  const isFailurePath = location.pathname === '/facial-results/failure';

  const handleRetry = () => {
    navigate(missingPersonId ? `/facial-search/${missingPersonId}` : '/facial-search');
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
    if (!missingPersonId) {
      alert('Error: Case ID not found. Cannot forward for closure.');
      return;
    }
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
    if (!missingPersonId) {
      alert('Error: Case ID not found. Cannot escalate.');
      return;
    }
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

  const handleUpdateFamilyNoMatch = async () => {
    if (!missingPersonId) return;
    setSubmitting(true);
    try {
      if (reportText) {
        await api.submitPoliceReport(missingPersonId, reportText);
      }
      alert('Family updated with unsuccessful search results.');
      navigate('/police-dashboard');
    } catch (err) {
      console.error('Error updating family:', err);
      alert('Failed to submit report.');
    } finally {
      setSubmitting(false);
    }
  };

  const handleCreateReport = () => {
    if (user?.role === 'police_officer') {
      navigate('/reports', { state: { uploadedImage } });
    } else {
      navigate('/report', { state: { uploadedImage } });
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
        {/* Success Results */}
        {isSuccessPath && hasMatch && results.length > 0 ? (
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
                      <h3>
                        {match.missing_person?.full_name || 'Unknown'}
                        <span className={`source-badge source-${match.source_database}`}>
                          {match.source_database === 'training_dataset' ? 'Training Dataset' : 'System Database'}
                        </span>
                      </h3>
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

                      <div className="match-images-comparison" style={{ display: 'flex', gap: '20px', marginTop: '15px' }}>
                        {uploadedImage && (
                          <div className="match-image-container" style={{ flex: 1 }}>
                            <h4 style={{marginBottom: '10px', color: '#1e293b'}}>Primary / Uploaded Photo:</h4>
                            <img
                              src={uploadedImage}
                              alt="Uploaded Source"
                              className="match-image"
                              style={{ width: '100%', objectFit: 'cover', borderRadius: '6px', border: '1px solid #cbd5e1' }}
                            />
                          </div>
                        )}
                        {match.source_image?.image_file && (
                          <div className="match-image-container" style={{ flex: 1 }}>
                            <h4 style={{marginBottom: '10px', color: '#1e293b'}}>Database Match Photo:</h4>
                            <img
                              src={match.source_image.image_file}
                              alt="Database Match"
                              className="match-image"
                              style={{ width: '100%', objectFit: 'cover', borderRadius: '6px', border: '1px solid #cbd5e1' }}
                            />
                          </div>
                        )}
                      </div>
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
                        disabled={submitting || !missingPersonId}
                      >
                        Forward to Family for Closure
                      </button>
                      <button
                        className="btn-warning"
                        onClick={handleEscalate}
                        disabled={submitting || !missingPersonId}
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
        ) : isFailurePath && !hasMatch && !error ? (
          // No Match Found
          <div className="results-no-match-section">
            <div className="no-match-banner">
              <div className="no-match-icon">😔</div>
              <h2>No Successful Match</h2>
              <p>
                Unfortunately, we didn't find a match for this image in our database.
                This person may not be in our system yet.
              </p>
            </div>

            {/* Display the uploaded image so the officer can still view it */}
            {uploadedImage && (
              <div className="no-match-image-container" style={{ margin: '20px auto', maxWidth: '300px', textAlign: 'center' }}>
                <h4 style={{marginBottom: '10px', color: '#1e293b'}}>Primary / Uploaded Photo:</h4>
                <img
                  src={uploadedImage}
                  alt="Uploaded Source"
                  className="match-image"
                  style={{ width: '100%', objectFit: 'cover', borderRadius: '6px', border: '1px solid #cbd5e1' }}
                />
              </div>
            )}

            <div className="no-match-suggestions">
              <h3>What You Can Do:</h3>
              <div className="suggestions-grid">
                <div className="suggestion-card">
                  <div className="suggestion-icon">📋</div>
                  <h4>Report Missing Person</h4>
                  <p>If you know this person is missing, help us create their profile</p>
                  <button className="btn-primary btn-sm" onClick={handleCreateReport}>
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
                  {showContact ? (
                    <div style={{ marginTop: '10px', fontSize: '0.9em', textAlign: 'left', background: '#f8fafc', padding: '10px', borderRadius: '6px', border: '1px solid #e2e8f0', color: '#334155' }}>
                      <p style={{ margin: '0 0 5px 0' }}><strong>📞 Phone:</strong> +254 700 000 000</p>
                      <p style={{ margin: '0 0 5px 0' }}><strong>📧 Email:</strong> support@surasmart-police.go.ke</p>
                      <p style={{ margin: '0' }}><strong>🌐 Web:</strong> www.surasmart-police.go.ke</p>
                    </div>
                  ) : (
                    <button className="btn-secondary btn-sm" onClick={() => setShowContact(true)}>
                      Contact Us
                    </button>
                  )}
                </div>
              </div>
            </div>

            {/* Analysis Report Section for Authorities when NO Match */}
            {missingPersonId && (user?.role === 'police_officer' || user?.role === 'government_official') && (
              <div className="analysis-report-section" style={{ marginTop: '30px' }}>
                <h3>Update Family on Search Results</h3>
                <p style={{color: '#64748b', marginBottom: '15px'}}>Record the unsuccessful search attempt to keep the family informed.</p>
                <textarea
                  className="report-textarea"
                  placeholder="Enter your summary here to update the family portal..."
                  value={reportText}
                  onChange={(e) => setReportText(e.target.value)}
                  disabled={submitting}
                ></textarea>
                <div className="workflow-actions">
                  <button
                    className="btn-primary"
                    onClick={handleUpdateFamilyNoMatch}
                    disabled={submitting || !reportText}
                  >
                    Post Update to Family Portal
                  </button>
                </div>
              </div>
            )}

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
              <button className="btn-secondary" onClick={() => navigate(user?.role === 'police_officer' ? '/police-dashboard' : user?.role === 'government_official' ? '/government-dashboard' : '/family-dashboard')}>
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
              <button className="btn-secondary" onClick={() => navigate(user?.role === 'police_officer' ? '/police-dashboard' : user?.role === 'government_official' ? '/government-dashboard' : '/family-dashboard')}>
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
