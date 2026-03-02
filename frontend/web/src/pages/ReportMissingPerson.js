import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import api from '../services/api';
import '../styles/Forms.css';

const ReportMissingPerson = () => {
  const navigate = useNavigate();
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [success, setSuccess] = useState(false);
  const [formData, setFormData] = useState({
    full_name: '',
    description: '',
    age: '',
    gender: '',
    last_seen_date: '',
    last_seen_location: '',
    identifying_marks: '',
  });

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData((prev) => ({
      ...prev,
      [name]: value,
    }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError(null);

    try {
      const response = await api.createMissingPerson({
        ...formData
      });

      setSuccess(true);
      setTimeout(() => {
        navigate(`/missing-person/${response.data.id}/upload`);
      }, 1500);
    } catch (err) {
      const errorData = err.response?.data;
      if (typeof errorData === 'object') {
        const message = Object.values(errorData).join('; ');
        setError(message);
      } else {
        setError(errorData || 'Failed to report missing person');
      }
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="form-container">
      <div className="form-card">
        <h1>Report Missing Person</h1>

        {error && <div className="error-message">{error}</div>}
        {success && (
          <div className="success-message">
            Missing person reported successfully. Redirecting...
          </div>
        )}

        <form onSubmit={handleSubmit}>
          <div className="form-group">
            <label htmlFor="full_name">Full Name *</label>
            <input
              type="text"
              id="full_name"
              name="full_name"
              value={formData.full_name}
              onChange={handleChange}
              required
              disabled={loading}
              placeholder="Enter full name"
            />
          </div>

          <div className="form-row">
            <div className="form-group">
              <label htmlFor="age">Age</label>
              <input
                type="number"
                id="age"
                name="age"
                value={formData.age}
                onChange={handleChange}
                disabled={loading}
                placeholder="Age"
              />
            </div>

            <div className="form-group">
              <label htmlFor="gender">Gender</label>
              <select
                id="gender"
                name="gender"
                value={formData.gender}
                onChange={handleChange}
                disabled={loading}
              >
                <option value="">Select gender</option>
                <option value="male">Male</option>
                <option value="female">Female</option>
                <option value="other">Other</option>
              </select>
            </div>
          </div>

          <div className="form-group">
            <label htmlFor="description">Description</label>
            <textarea
              id="description"
              name="description"
              value={formData.description}
              onChange={handleChange}
              disabled={loading}
              placeholder="Additional details about the missing person"
              rows="4"
            />
          </div>

          <div className="form-group">
            <label htmlFor="identifying_marks">Identifying Marks</label>
            <textarea
              id="identifying_marks"
              name="identifying_marks"
              value={formData.identifying_marks}
              onChange={handleChange}
              disabled={loading}
              placeholder="Scars, tattoos, birthmarks, etc."
              rows="3"
            />
          </div>

          <div className="form-row">
            <div className="form-group">
              <label htmlFor="last_seen_date">Last Seen Date</label>
              <input
                type="datetime-local"
                id="last_seen_date"
                name="last_seen_date"
                value={formData.last_seen_date}
                onChange={handleChange}
                disabled={loading}
              />
            </div>

            <div className="form-group">
              <label htmlFor="last_seen_location">Last Seen Location</label>
              <input
                type="text"
                id="last_seen_location"
                name="last_seen_location"
                value={formData.last_seen_location}
                onChange={handleChange}
                disabled={loading}
                placeholder="Location"
              />
            </div>
          </div>

          <button type="submit" disabled={loading} className="btn-primary btn-large">
            {loading ? 'Reporting...' : 'Report Missing Person'}
          </button>
        </form>
      </div>
    </div>
  );
};

export default ReportMissingPerson;
