import React, { useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import api from '../services/api';
import '../styles/upload.css';

const UploadImage = () => {
  const { missingPersonId } = useParams();
  const navigate = useNavigate();
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [success, setSuccess] = useState(false);
  const [preview, setPreview] = useState(null);
  const [priority, setPriority] = useState('normal');

  const handleFileChange = (e) => {
    const file = e.target.files?.[0];
    if (file) {
      if (!['image/jpeg', 'image/png', 'image/jpg'].includes(file.type)) {
        setError('Please select a valid image file (JPEG or PNG)');
        return;
      }
      if (file.size > 5 * 1024 * 1024) {
        setError('File size must be less than 5MB');
        return;
      }
      setError(null);
      const reader = new FileReader();
      reader.onloadend = () => {
        setPreview(reader.result);
      };
      reader.readAsDataURL(file);
    }
  };

  const handleRaiseCase = async (e) => {
    if (e) e.preventDefault();
    setLoading(true);
    setError(null);
    const fileInput = document.getElementById('image');
    const file = fileInput.files?.[0];

    try {
      // 1. Upload image first
      if (file) {
        await api.uploadImage(missingPersonId, file, priority);
      } else {
        setError('Please select an image before raising the case.');
        setLoading(false);
        return;
      }

      // 2. Raise the case to police
      await api.raiseCase(missingPersonId);

      // 3. Success State & Redirect
      setSuccess(true);
      setTimeout(() => {
        navigate('/family-dashboard');
      }, 2000); // 2 second delay to read message
    } catch (err) {
      const errorData = err.response?.data;
      const errorMessage = typeof errorData === 'object'
        ? Object.values(errorData).join('; ')
        : (errorData || 'Failed to complete reporting. Please try again.');
      setError(errorMessage);
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="chase-body">
      <div className="chase-header">
        <div className="chase-logo">Sura <span>Smart</span></div>
      </div>
      <div className="chase-container" style={{ maxWidth: '600px' }}>
        <div className="upload-card">
          <h1 className="upload-title">
            Complete Your Report
          </h1>

          {error && (
            <div className="alert alert-error">
              {error}
            </div>
          )}

          {success && (
            <div className="alert alert-success">
              <strong>Success:</strong> Your Case has been successfully raised to the Police. Redirecting...
            </div>
          )}

        <form onSubmit={handleRaiseCase}>
          <div className="upload-form-group">
            <label htmlFor="image" className="upload-label">Upload Identification Photo *</label>
            <input
              type="file"
              id="image"
              className="upload-input"
              accept="image/jpeg,image/jpg,image/png"
              onChange={handleFileChange}
              required
              disabled={loading || success}
            />
            <p className="upload-hint">
              Clear facial photo required for recognition.
            </p>
          </div>

          {preview && (
            <div className="upload-preview-container">
              <img src={preview} alt="Preview" className="upload-preview-image" />
            </div>
          )}

          <div className="upload-form-group">
            <label htmlFor="priority" className="upload-label">Case Urgency</label>
            <select
              id="priority"
              className="upload-select"
              value={priority}
              onChange={(e) => setPriority(e.target.value)}
              disabled={loading || success}
            >
              <option value="normal">Standard Priority</option>
              <option value="high">Urgent Response</option>
              <option value="urgent">Critical (Immediate Alert)</option>
            </select>
          </div>

          <div className="upload-actions">
            <button
              type="submit"
              disabled={loading || success}
              className="upload-button-primary"
            >
              {loading ? 'Processing...' : 'Raise Case to Police'}
            </button>

            <button
              type="button"
              className="upload-button-secondary"
              onClick={() => navigate('/family-dashboard')}
            >
              Cancel
            </button>
          </div>
        </form>
      </div>
    </div>
  </div>
  );
};

export default UploadImage;