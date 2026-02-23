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

  // Load missing person data if ID is provided
  useEffect(() => {
    if (missingPersonId) {
      loadMissingPerson();
    }
  }, [missingPersonId]);

  const loadMissingPerson = async () => {
    try {
      const response = await api.getMissingPerson(missingPersonId);
      setMissingPerson(response.data);
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

    if (!missingPerson) {
      setError('Missing person data not loaded');
      return;
    }

    setError(null);
    setLoading(true);

    try {
      // Perform database search based on missing person details
      const response = await api.searchMissingPersons({
        name: missingPerson.full_name,
        age: missingPerson.age,
        gender: missingPerson.gender,
        location: missingPerson.last_seen_location,
        description: missingPerson.description
      });

      const matches = response.data || [];

      // Filter matches based on criteria (at least 2 matching components)
      const filteredMatches = matches.filter(match => {
        let matchScore = 0;

        // Name match (partial or full)
        if (match.full_name && missingPerson.full_name) {
          const nameMatch = match.full_name.toLowerCase().includes(missingPerson.full_name.toLowerCase()) ||
            missingPerson.full_name.toLowerCase().includes(match.full_name.toLowerCase());
          if (nameMatch) matchScore += 1;
        }

        // Age match (within 5 years)
        if (match.age && missingPerson.age) {
          const ageDiff = Math.abs(parseInt(match.age) - parseInt(missingPerson.age));
          if (ageDiff <= 5) matchScore += 1;
        }

        // Gender match
        if (match.gender && missingPerson.gender &&
          match.gender.toLowerCase() === missingPerson.gender.toLowerCase()) {
          matchScore += 1;
        }

        // Location match
        if (match.last_seen_location && missingPerson.last_seen_location) {
          const locationMatch = match.last_seen_location.toLowerCase().includes(missingPerson.last_seen_location.toLowerCase()) ||
            missingPerson.last_seen_location.toLowerCase().includes(match.last_seen_location.toLowerCase());
          if (locationMatch) matchScore += 0.5;
        }

        return matchScore >= 2; // At least 2 matching components
      });

      setSearchResults(filteredMatches);
      setSearchPerformed(true);

      // If no matches found, show "zoom case" option
      if (filteredMatches.length === 0) {
        setError('No matches found. Consider zooming the case for more details.');
      }

    } catch (err) {
      console.error('Search error:', err);
      const errorMessage = err.response?.data?.detail || 'Failed to search database. Please try again.';
      setError(errorMessage);
      setSearchPerformed(true);
    } finally {
      setLoading(false);
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
      navigate('/dashboard');
    } catch (err) {
      console.error('Failed to close case:', err);
      alert('Failed to close case. Please try again.');
    }
  };

  const handleEscalateCase = async () => {
    if (!missingPerson) return;

    try {
      await api.updateMissingPerson(missingPerson.id, {
        status: 'escalated',
        notes: 'Case escalated - facial recognition successful but requires further investigation'
      });
      alert('Case escalated successfully!');
      navigate('/dashboard');
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
      navigate('/dashboard');
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
                    Searching Database...
                  </>
                ) : (
                  <>
                    🔍 {missingPerson ? 'Search for Matches' : 'Search Database'}
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
