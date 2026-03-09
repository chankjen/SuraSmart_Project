import React, { useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import api from '../services/api';
import '../styles/ChaseUI.css';

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
        <h1 className="chase-title" style={{ fontSize: '1.5rem', marginBottom: '1.5rem', color: 'var(--chase-blue-dark)' }}>
          Complete Your Report
        </h1>

        {error && (
          <div className="error-message" style={{ marginBottom: '20px', padding: '12px', background: '#fee2e2', color: '#991b1b', borderRadius: '8px', border: '1px solid #fca5a5' }}>
            {error}
          </div>
        )}

        {success && (
          <div className="success-message" style={{ marginBottom: '20px', padding: '12px', background: '#dcfce7', color: '#166534', borderRadius: '8px', border: '1px solid #86efac' }}>
            <strong>Success:</strong> Your Case has been successfully raised to the Police. Redirecting...
          </div>
        )}

        <form onSubmit={handleRaiseCase}>
          <div className="form-group" style={{ marginBottom: '20px' }}>
            <label htmlFor="image" style={{ display: 'block', marginBottom: '8px', fontWeight: '600' }}>Identification Photo *</label>
            <input
              type="file"
              id="image"
              accept="image/jpeg,image/jpg,image/png"
              onChange={handleFileChange}
              required
              disabled={loading || success}
              style={{ width: '100%', padding: '10px', border: '1px solid var(--chase-gray-200)', borderRadius: '8px' }}
            />
            <p style={{ fontSize: '0.8rem', color: 'var(--chase-gray-500)', marginTop: '8px' }}>
              Clear facial photo required for recognition.
            </p>
          </div>

          {preview && (
            <div style={{ margin: '20px 0', textAlign: 'center' }}>
              <img src={preview} alt="Preview" style={{ maxWidth: '100%', borderRadius: '8px', boxShadow: '0 4px 12px rgba(0,0,0,0.1)' }} />
            </div>
          )}

          <div className="form-group" style={{ marginBottom: '32px' }}>
            <label htmlFor="priority" style={{ display: 'block', marginBottom: '8px', fontWeight: '600' }}>Case Urgency</label>
            <select
              id="priority"
              value={priority}
              onChange={(e) => setPriority(e.target.value)}
              disabled={loading || success}
              style={{ width: '100%', padding: '12px', border: '1px solid var(--chase-gray-200)', borderRadius: '8px', background: 'white' }}
            >
              <option value="normal">Standard Priority</option>
              <option value="high">Urgent Response</option>
              <option value="urgent">Critical (Immediate Alert)</option>
            </select>
          </div>

          <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
            <button
              type="submit"
              disabled={loading || success}
              className="chase-button"
              style={{ padding: '1rem', fontSize: '1.1rem', width: '100%' }}
            >
              {loading ? 'Processing...' : 'Raise Case to Police'}
            </button>

            <button
              type="button"
              className="chase-button-outline"
              onClick={() => navigate('/family-dashboard')}
              style={{ padding: '0.75rem', width: '100%', border: '1px solid var(--chase-gray-200)', color: 'var(--chase-gray-500)' }}
            >
              Cancel
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};

export default UploadImage;