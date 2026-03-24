import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import api from '../services/api';
import '../styles/FacialRecognition.css';

const FacialRecognitionSearch = () => {
  const { missingPersonId } = useParams();
  const navigate = useNavigate();
  const { user, logout } = useAuth();
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [preview, setPreview] = useState(null);
  const [selectedFile, setSelectedFile] = useState(null);
  const [missingPerson, setMissingPerson] = useState(null);
  const [searchResults, setSearchResults] = useState([]);
  const [searchPerformed, setSearchPerformed] = useState(false);
  const [primaryPhoto, setPrimaryPhoto] = useState(null);
  const [submitting, setSubmitting] = useState(false);
  const [activeCases, setActiveCases] = useState([]);
  const [fetchingCases, setFetchingCases] = useState(false);

  // Load missing person data if ID is provided
  useEffect(() => {
    if (missingPersonId) {
      loadMissingPerson();
    } else if (user?.role === 'police_officer') {
      fetchActiveCases();
    }
  }, [missingPersonId, user]);

  const fetchActiveCases = async () => {
    setFetchingCases(true);
    try {
      const response = await api.getMissingPersons();
      const results = response.data.results || response.data || [];
      // Filter for actionable cases
      const actionable = results.filter(c => ['RAISED', 'UNDER_INVESTIGATION', 'REPORTED'].includes(c.status));
      setActiveCases(actionable);
    } catch (err) {
      console.error('Failed to fetch cases:', err);
    } finally {
      setFetchingCases(false);
    }
  };

  const loadMissingPerson = async () => {
    try {
      const response = await api.getMissingPerson(missingPersonId);
      const data = response.data;
      setMissingPerson(data);
      
      // Find primary photo from case data
      if (data.facial_recognition_images && data.facial_recognition_images.length > 0) {
        const primary = data.facial_recognition_images.find(img => img.is_primary) || data.facial_recognition_images[0];
        setPrimaryPhoto(primary);
      }
    } catch (err) {
      console.error('Failed to load missing person:', err);
      setError('Failed to load missing person details');
    }
  };

  // Navigation / auth helpers
  const handleRoleChange = () => {
    navigate('/role-selector');
  };

  const handleLogout = async () => {
    try {
      await logout();
      navigate('/login');
    } catch (err) {
      console.error('Logout failed:', err);
    }
  };

  const handleFileChange = (e) => {
    const file = e.target.files?.[0];
    if (file) {
      // Validate file type
      if (!['image/jpeg', 'image/png', 'image/jpg'].includes(file.type)) {
        setError('Please select a valid image file (JPEG or PNG)');
        return;
      }

      // Validate file size (5MB max)
      if (file.size > 5 * 1024 * 1024) {
        setError('File size must be less than 5MB');
        return;
      }

      setError(null);
      setSelectedFile(file);

      // Create preview
      const reader = new FileReader();
      reader.onloadend = () => {
        setPreview(reader.result);
      };
      reader.readAsDataURL(file);
    }
  };

  const handleSearch = async (e) => {
    e.preventDefault();

    if (!selectedFile) {
      setError('Please select an image file to search');
      return;
    }

    setError(null);
    setLoading(true);

    try {
      // Perform actual AI facial recognition search
      const response = await api.searchFacialRecognition(selectedFile);
      const searchData = response.data;

      if (missingPersonId) {
        // If searching within a case context, we also "Raise" it as per workflow
        try {
          await api.raiseCase(missingPersonId);
          // Only redirect to dashboard for family members. 
          // Authorities (Police) need to proceed to the results page to review matches and take actions.
          if (user?.role === 'family_member' || user?.role === 'individual_user') {
            alert("Case raised to police successfully.");
            navigate('/family-dashboard');
            return;
          }
        } catch (e) {
          console.error("Auto-raise failed:", e);
        }
      }

      // Navigate to results page with the AI match data (for general search without case context)
      const resultsRoute = searchData.match_found ? '/facial-results/success' : '/facial-results/failure';
      navigate(resultsRoute, {
        state: {
          results: (searchData.match || searchData.best_match) ? [searchData.match || searchData.best_match] : [],
          uploadedImage: preview,
          hasMatch: searchData.match_found,
          message: searchData.message,
          searchSessionId: searchData.search_session_id,
          missingPersonId: missingPersonId // Pass if we are in a specific case context
        }
      });

    } catch (err) {
      console.error('Search error:', err);
      const errorMessage = err.response?.data?.error || err.response?.data?.detail || 'Failed to perform facial search. Please try again.';
      setError(errorMessage);
    } finally {
      setLoading(false);
    }
  };

  const handleAutomatedSearch = async () => {
    if (!missingPersonId || !primaryPhoto) return;

    setSubmitting(true);
    setError(null);

    try {
      const response = await api.runAiSearch(missingPersonId);
      const searchData = response.data;

      // Navigate to results page with the automated match data
      const resultsRoute = searchData.match_found ? '/facial-results/success' : '/facial-results/failure';
      navigate(resultsRoute, {
        state: {
          results: (searchData.match || searchData.best_match) ? [searchData.match || searchData.best_match] : [],
          uploadedImage: primaryPhoto.image_file,
          hasMatch: searchData.match_found,
          message: searchData.message,
          missingPersonId: missingPersonId,
          isAutomated: true
        }
      });
    } catch (err) {
      console.error('Automated search error:', err);
      setError(err.response?.data?.error || 'Failed to complete automated search.');
    } finally {
      setSubmitting(false);
    }
  };

  const handleCloseCase = async () => {
    if (!missingPerson) return;

    try {
      await api.updateMissingPerson(missingPerson.id, {
        status: 'found',
        notes: 'Case closed - facial recognition match confirmed'
      });
      alert('Case closed successfully!');
      navigate(user?.role === 'police_officer' ? '/police-dashboard' : user?.role === 'government_official' ? '/government-dashboard' : '/family-dashboard');
    } catch (err) {
      console.error('Failed to close case:', err);
      alert('Failed to close case. Please try again.');
    }
  };

  const handleEscalateCase = async () => {
    if (!missingPerson) return;

    try {
      await api.escalateCase(missingPerson.id);
      alert('Case escalated successfully!');
      navigate(user?.role === 'police_officer' ? '/police-dashboard' : user?.role === 'government_official' ? '/government-dashboard' : '/family-dashboard');
    } catch (err) {
      console.error('Failed to escalate case:', err);
      alert('Failed to escalate case. Please try again.');
    }
  };

  const handleZoomCase = async () => {
    if (!missingPerson) return;

    try {
      await api.updateMissingPerson(missingPerson.id, {
        status: 'zoom_required',
        notes: 'Case requires more details - no matches found'
      });
      alert('Case marked for zoom investigation!');
      navigate(user?.role === 'police_officer' ? '/police-dashboard' : user?.role === 'government_official' ? '/government-dashboard' : '/family-dashboard');
    } catch (err) {
      console.error('Failed to update case:', err);
      alert('Failed to update case. Please try again.');
    }
  };

  return (
    <div className="facial-recognition-container">
      {/* Header */}
      <header className="facial-header">
        <div className="facial-header-content">
          <div className="facial-logo">
            <h1 className="logo-glitter-text">🔍 SuraSmart</h1>
            <span>Facial Recognition Search</span>
          </div>
          <div className="facial-user-menu">
            <span className="facial-user-info">
              {user?.first_name || user?.username}
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
        {!missingPersonId && user?.role === 'police_officer' && activeCases.length > 0 && (
          <div className="case-selection-section" style={{ marginBottom: '40px' }}>
            <div className="upload-card" style={{ borderLeft: '4px solid var(--chase-blue)' }}>
              <h3>Select an Active Case for Analysis</h3>
              <p className="upload-subtitle">Choose a case from your jurisdiction to run an automated AI match using existing evidence.</p>
              
              <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(280px, 1fr))', gap: '15px', marginTop: '20px' }}>
                {activeCases.map(c => (
                  <div 
                    key={c.id} 
                    onClick={() => navigate(`/facial-search/${c.id}`)}
                    className="chase-list-item" 
                    style={{ 
                      padding: '15px', 
                      cursor: 'pointer', 
                      border: '1px solid var(--chase-gray-100)',
                      transition: 'all 0.2s ease'
                    }}
                    onMouseOver={(e) => e.currentTarget.style.borderColor = 'var(--chase-blue)'}
                    onMouseOut={(e) => e.currentTarget.style.borderColor = 'var(--chase-gray-100)'}
                  >
                    <div style={{ fontWeight: 'bold', color: '#f59e0b' }}>{c.full_name}</div>
                    <div style={{ fontSize: '0.85rem', color: 'var(--chase-gray-500)', marginTop: '4px' }}>
                      Status: {c.status} | Reported: {new Date(c.date_reported).toLocaleDateString()}
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>
        )}

        {missingPerson && (
          <div className="missing-person-details">
            <h2>Searching for: {missingPerson.full_name}</h2>
            <div className="person-info">
              <div className="info-item"><strong>Age:</strong> {missingPerson.age || 'Unknown'}</div>
              <div className="info-item"><strong>Gender:</strong> {missingPerson.gender || 'Unknown'}</div>
              <div className="info-item"><strong>Last Seen:</strong> {missingPerson.last_seen_location || 'Unknown'}</div>
              <div className="info-item"><strong>Description:</strong> {missingPerson.description || 'No description'}</div>
            </div>
          </div>
        )}

        {primaryPhoto && (
          <div className="case-photo-section" style={{ marginBottom: '30px' }}>
            <div className="upload-card" style={{ borderLeft: '4px solid var(--chase-blue)' }}>
              <h3>Case Evidence Detected</h3>
              <p className="upload-subtitle">We found a primary photo for this case. You can run AI matching directly using this image.</p>
              
              <div style={{ display: 'flex', gap: '25px', alignItems: 'center', marginTop: '20px' }}>
                <div className="image-preview-large" style={{ margin: 0, width: '150px', height: '150px' }}>
                  <img src={primaryPhoto.image_file} alt="Case Primary" style={{ width: '100%', height: '100%', objectFit: 'cover' }} />
                </div>
                <div>
                  <button 
                    onClick={handleAutomatedSearch}
                    disabled={submitting || loading}
                    className="chase-button"
                    style={{ padding: '0.85rem 1.5rem', background: 'var(--chase-blue-dark)' }}
                  >
                    {submitting ? 'Analyzing Case Photo...' : '🔍 Analyze Case Photo Now'}
                  </button>
                  <p style={{ marginTop: '10px', fontSize: '0.85rem', color: 'var(--chase-gray-500)' }}>
                    Uses the officially reported photo to search all compatible databases.
                  </p>
                </div>
              </div>
            </div>
          </div>
        )}

        <div className="facial-upload-section">
          <div className="upload-card">
            <h2>{missingPerson ? 'Upload Facial Image for Verification' : 'Upload an Image to Search'}</h2>
            <p className="upload-subtitle">
              {missingPerson
                ? 'Upload an image to verify against the reported missing person details'
                : 'Upload a facial image to search our database for matching missing persons'
              }
            </p>

            {error && <div className="error-message">{error}</div>}

            <form onSubmit={handleSearch} className="facial-form">
              <div className="form-group">
                <label htmlFor="image" className="file-input-label-large">
                  <div className="file-input-icon">📸</div>
                  <div className="file-input-text">
                    {preview ? (
                      <>
                        <strong>Image Selected ✓</strong>
                        <small>{selectedFile?.name}</small>
                      </>
                    ) : (
                      <>
                        <strong>Click to select an image</strong>
                        <small>or drag and drop</small>
                      </>
                    )}
                  </div>
                </label>
                <input
                  type="file"
                  id="image"
                  accept="image/jpeg,image/jpg,image/png"
                  onChange={handleFileChange}
                  disabled={loading}
                  className="file-input-hidden"
                />
              </div>

              {preview && (
                <div className="image-preview-large">
                  <img src={preview} alt="Preview" />
                  <button
                    type="button"
                    className="btn-remove-image"
                    onClick={() => {
                      setPreview(null);
                      setSelectedFile(null);
                    }}
                  >
                    ✕ Remove
                  </button>
                </div>
              )}

              <div className="form-hints">
                <p className="hint-title">Accepted Formats:</p>
                <ul className="hints-list">
                  <li>✓ JPEG, PNG formats</li>
                  <li>✓ Maximum size: 5MB</li>
                  <li>✓ Clear facial image recommended</li>
                  <li>✓ Good lighting for best results</li>
                </ul>
              </div>

              <button
                type="submit"
                disabled={loading || (!missingPerson && !selectedFile)}
                className="btn-primary btn-large btn-search"
              >
                {loading ? (
                  <>
                    <span className="spinner"></span>
                    Raising Case...
                  </>
                ) : (
                  <>
                    View Facial Matching Results
                  </>
                )}
              </button>
            </form>
          </div>
        </div>

        {/* Search Results */}
        {searchPerformed && (
          <div className="search-results-section">
            <h2>Search Results</h2>

            {searchResults.length > 0 ? (
              <div className="matches-found">
                <div className="results-summary">
                  <h3>✅ Matches Found ({searchResults.length})</h3>
                  <p>The following records match the search criteria (at least 2 matching components).</p>
                </div>

                <div className="matches-list">
                  {searchResults.map((match, index) => (
                    <div key={match.id || index} className="match-card">
                      <h4>{match.full_name}</h4>
                      <div className="match-details">
                        <span>Age: {match.age || 'Unknown'}</span>
                        <span>Gender: {match.gender || 'Unknown'}</span>
                        <span>Location: {match.last_seen_location || 'Unknown'}</span>
                      </div>
                      <p>{match.description || 'No additional details'}</p>
                    </div>
                  ))}
                </div>

                <div className="case-actions">
                  <h3>Case Management Options:</h3>
                  <div className="action-buttons">
                    <button
                      onClick={handleCloseCase}
                      className="btn-success btn-large"
                    >
                      ✅ Close Case
                    </button>
                    <p className="action-description">
                      Successful facial recognition match - case resolved
                    </p>
                  </div>

                  <div className="action-buttons">
                    <button
                      onClick={handleEscalateCase}
                      className="btn-warning btn-large"
                    >
                      ⚠️ Escalate Case
                    </button>
                    <p className="action-description">
                      Facial recognition successful but requires further investigation
                    </p>
                  </div>
                </div>
              </div>
            ) : (
              <div className="no-matches">
                <div className="results-summary">
                  <h3>❌ No Matches Found</h3>
                  <p>No database records match the search criteria with sufficient confidence.</p>
                </div>

                <div className="case-actions">
                  <h3>Case Management Options:</h3>
                  <div className="action-buttons">
                    <button
                      onClick={handleZoomCase}
                      className="btn-info btn-large"
                    >
                      🔍 Zoom Case
                    </button>
                    <p className="action-description">
                      No matches found - case requires more details for investigation
                    </p>
                  </div>
                </div>
              </div>
            )}
          </div>
        )}

        {/* Info Section */}
        <section className="facial-info">
          <h3>How It Works</h3>
          <div className="info-steps">
            <div className="info-step">
              <div className="step-number">1</div>
              <h4>Upload Image</h4>
              <p>Select a clear facial image from your device</p>
            </div>
            <div className="info-step">
              <div className="step-number">2</div>
              <h4>AI Processing</h4>
              <p>Our AI analyzes facial features and searches the database</p>
            </div>
            <div className="info-step">
              <div className="step-number">3</div>
              <h4>Find Matches</h4>
              <p>View potential matches from our missing persons database</p>
            </div>
            <div className="info-step">
              <div className="step-number">4</div>
              <h4>Take Action</h4>
              <p>Report findings to authorities or notify families</p>
            </div>
          </div>
        </section>
      </main>
    </div>
  );
};

export default FacialRecognitionSearch;
