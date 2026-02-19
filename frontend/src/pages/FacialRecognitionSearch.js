import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import api from '../services/api';
import '../styles/FacialRecognition.css';

const FacialRecognitionSearch = () => {
  const navigate = useNavigate();
  const { user, logout } = useAuth();
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [preview, setPreview] = useState(null);
  const [selectedFile, setSelectedFile] = useState(null);

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
      setError('Please select an image to search');
      return;
    }

    setError(null);
    setLoading(true);

    try {
      // Call API to perform facial recognition search
      const response = await api.searchFacialRecognition(selectedFile);
      
      // Navigate to results page with the response data
      navigate('/facial-results', { 
        state: { 
          results: response.data.matches || [],
          uploadedImage: preview,
          hasMatch: response.data.matches && response.data.matches.length > 0
        } 
      });
    } catch (err) {
      console.error('Search error:', err);
      const errorMessage = err.response?.data?.detail || 'Failed to search for facial matches. Please try again.';
      setError(errorMessage);
      navigate('/facial-results', { 
        state: { 
          results: [],
          uploadedImage: preview,
          hasMatch: false,
          error: errorMessage
        } 
      });
    } finally {
      setLoading(false);
    }
  };

  const handleRoleChange = () => {
    navigate('/role-selector');
  };

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  return (
    <div className="facial-recognition-container">
      {/* Header */}
      <header className="facial-header">
        <div className="facial-header-content">
          <div className="facial-logo">
            <h1>🔍 SuraSmart</h1>
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
        <div className="facial-upload-section">
          <div className="upload-card">
            <h2>Upload an Image to Search</h2>
            <p className="upload-subtitle">
              Upload a facial image to search our database for matching missing persons
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
                disabled={loading || !selectedFile}
                className="btn-primary btn-large btn-search"
              >
                {loading ? (
                  <>
                    <span className="spinner"></span>
                    Searching Database...
                  </>
                ) : (
                  <>
                    🔍 Search for Matches
                  </>
                )}
              </button>
            </form>
          </div>
        </div>

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
