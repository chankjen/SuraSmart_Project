import React, { useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import api from '../services/api';
import '../styles/Forms.css';

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

      // Create preview
      const reader = new FileReader();
      reader.onloadend = () => {
        setPreview(reader.result);
      };
      reader.readAsDataURL(file);
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError(null);

    const fileInput = document.getElementById('image');
    const file = fileInput.files?.[0];

    if (!file) {
      setError('Please select an image');
      setLoading(false);
      return;
    }

    try {
      await api.uploadImage(missingPersonId, file, priority);
      setSuccess(true);

      setTimeout(() => {
        navigate(`/results/${missingPersonId}`);
      }, 1500);
    } catch (err) {
      const errorData = err.response?.data;
      if (typeof errorData === 'object') {
        const message = Object.values(errorData).join('; ');
        setError(message);
      } else {
        setError(errorData || 'Failed to upload image');
      }
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="form-container">
      <div className="form-card">
        <h1>Upload Facial Image</h1>

        {error && <div className="error-message">{error}</div>}
        {success && (
          <div className="success-message">
            Image uploaded successfully. Processing...
          </div>
        )}

        <form onSubmit={handleSubmit}>
          <div className="form-group">
            <label htmlFor="image">Select Image *</label>
            <div className="file-input-wrapper">
              <input
                type="file"
                id="image"
                accept="image/jpeg,image/jpg,image/png"
                onChange={handleFileChange}
                required
                disabled={loading}
              />
              <span className="file-input-label">
                {preview ? 'Image selected ✓' : 'Choose an image'}
              </span>
            </div>
            <p className="input-hint">Accepted formats: JPEG, PNG. Max size: 5MB</p>
          </div>

          {preview && (
            <div className="image-preview">
              <img src={preview} alt="Preview" />
            </div>
          )}

          <div className="form-group">
            <label htmlFor="priority">Processing Priority</label>
            <select
              id="priority"
              value={priority}
              onChange={(e) => setPriority(e.target.value)}
              disabled={loading}
            >
              <option value="low">Low</option>
              <option value="normal">Normal</option>
              <option value="high">High</option>
              <option value="urgent">Urgent</option>
            </select>
            <p className="input-hint">Higher priority images are processed first</p>
          </div>

          <button type="submit" disabled={loading} className="btn-primary btn-large">
            {loading ? 'Uploading...' : 'Upload Image'}
          </button>
        </form>
      </div>
    </div>
  );
};

export default UploadImage;
