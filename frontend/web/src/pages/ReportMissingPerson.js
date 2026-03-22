import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import api from '../services/api';
import '../styles/Forms.css';

import { KENYA_LOCATIONS } from '../constants/kenyaLocations';

const EYE_COLORS = ['Brown', 'Blue', 'Hazel', 'Amber', 'Green', 'Gray', 'Black'];
const COMPLEXIONS = ['Fair', 'Light', 'Medium', 'Olive', 'Tan', 'Brown', 'Dark'];
const KENYAN_LANGUAGES = [
  'Gikuyu (Kikuyu)', 'Kamba (Akamba)', 'Luhya', 'Ekegusii (Gusii)', 'Meru (Kimîîru)', 
  'Embu (Kiembu)', 'Mbeere', 'Giryama', 'Chonyi', 'Dzihana', 'Kauma', 'Kambe', 
  'Duruma', 'Rabai', 'Suba', 'Taveta', 'Taita', 'Kwavi', 'Lunyala', 'Markweeta (Marakwet)', 
  'Sabaot', 'Terik', 'Dholuo (Luo)', 'Kipsigis', 'Nandi', 'Keiyo', 'Tugen', 'Pökoot', 
  'Samburu', 'Maasai (Maa)', 'Turkana', 'Datog', 'Oluwanga', 'Nyala', 'Olunyole', 
  'Somali', 'Oromo', 'Orma', 'Rendille', 'Aweer (Boni)', 'Dahalo', 'Garre', 'Burji', 
  'Arabic', 'English', 'Hindi / Hindustani', 'Gujarati', 'Punjabi', 'Konkani', 
  'Nubi', 'Kenyan Sign Language'
];

const ReportMissingPerson = () => {
  const navigate = useNavigate();
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [success, setSuccess] = useState(false);
  
  const [selectedCounty, setSelectedCounty] = useState('');
  const [selectedSubcounty, setSelectedSubcounty] = useState('');
  const [selectedLanguages, setSelectedLanguages] = useState([]);
  const [showOtherLanguage, setShowOtherLanguage] = useState(false);
  const [otherLanguage, setOtherLanguage] = useState('');

  const [formData, setFormData] = useState({
    full_name: '',
    description: '',
    age: '',
    gender: '',
    eye_color: '',
    height: '',
    height_unit: 'inches',
    complexion: '',
    languages: '',
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

  const handleCountyChange = (e) => {
    const county = e.target.value;
    setSelectedCounty(county);
    setSelectedSubcounty(''); // Reset subcounty
    setFormData(prev => ({
      ...prev,
      last_seen_location: county ? `Unspecified, ${county}` : ''
    }));
  };

  const handleSubcountyChange = (e) => {
    const subcounty = e.target.value;
    setSelectedSubcounty(subcounty);
    setFormData(prev => ({
      ...prev,
      last_seen_location: subcounty ? `${subcounty}, ${selectedCounty}` : `Unspecified, ${selectedCounty}`
    }));
  };

  const handleLanguageChange = (lang) => {
    if (lang === 'Other') {
      setShowOtherLanguage(!showOtherLanguage);
      return;
    }

    if (selectedLanguages.includes(lang)) {
      setSelectedLanguages(prev => prev.filter(l => l !== lang));
    } else {
      if (selectedLanguages.length >= 5) {
        alert('You can select up to 5 languages.');
        return;
      }
      setSelectedLanguages(prev => [...prev, lang]);
    }
  };

  const validateHeight = () => {
    const h = parseFloat(formData.height);
    if (!h) return true;
    
    if (formData.height_unit === 'inches' && h > 110) {
      alert('Height cannot exceed 110 inches.');
      return false;
    }
    if (formData.height_unit === 'ft' && h > 9.17) {
      alert('Height cannot exceed 9.17 feet (approx 110 inches).');
      return false;
    }
    if (formData.height_unit === 'meters' && h > 2.79) {
      alert('Height cannot exceed 2.79 meters (approx 110 inches).');
      return false;
    }
    return true;
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError(null);

    // Date Validation: Must be at least 1 hour ago
    if (formData.last_seen_date) {
      const selectedDate = new Date(formData.last_seen_date);
      const oneHourAgo = new Date(Date.now() - 60 * 60 * 1000);
      
      if (selectedDate > oneHourAgo) {
        alert('Last seen date must be at least one hour before the current time.');
        setLoading(false);
        return;
      }
    }

    // Age Validation
    const ageNum = parseInt(formData.age);
    if (ageNum < 1 || ageNum > 140) {
      alert('Age must be strictly between 1 and 140.');
      setLoading(false);
      return;
    }

    // Height Validation
    if (!validateHeight()) {
      setLoading(false);
      return;
    }

    // Language Validation
    const allLangs = [...selectedLanguages];
    if (showOtherLanguage && otherLanguage.trim()) {
      allLangs.push(otherLanguage.trim());
    }

    if (allLangs.length === 0) {
      alert('Please select at least one language.');
      setLoading(false);
      return;
    }
    if (allLangs.length > 5) {
      alert('You can select up to 5 languages.');
      setLoading(false);
      return;
    }

    try {
      const response = await api.createMissingPerson({
        ...formData,
        languages: allLangs.join(', ')
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
              <label htmlFor="age">Age (1-140) *</label>
              <input
                type="number"
                id="age"
                name="age"
                value={formData.age}
                onChange={handleChange}
                required
                disabled={loading}
                placeholder="Age"
                min="1"
                max="140"
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

          <div className="form-row">
            <div className="form-group">
              <label htmlFor="eye_color">Eye Color</label>
              <select
                id="eye_color"
                name="eye_color"
                value={formData.eye_color}
                onChange={handleChange}
                disabled={loading}
              >
                <option value="">Select eye color</option>
                {EYE_COLORS.map(color => (
                  <option key={color} value={color}>{color}</option>
                ))}
              </select>
            </div>

            <div className="form-group">
              <label htmlFor="complexion">Complexion</label>
              <select
                id="complexion"
                name="complexion"
                value={formData.complexion}
                onChange={handleChange}
                disabled={loading}
              >
                <option value="">Select complexion</option>
                {COMPLEXIONS.map(comp => (
                  <option key={comp} value={comp}>{comp}</option>
                ))}
              </select>
            </div>
          </div>

          <div className="form-row">
            <div className="form-group" style={{ flex: 2 }}>
              <label htmlFor="height">Height (Max 110 inches or equiv)</label>
              <input
                type="number"
                step="0.01"
                id="height"
                name="height"
                value={formData.height}
                onChange={handleChange}
                disabled={loading}
                placeholder="Enter height"
              />
            </div>
            <div className="form-group" style={{ flex: 1 }}>
              <label htmlFor="height_unit">Unit</label>
              <select
                id="height_unit"
                name="height_unit"
                value={formData.height_unit}
                onChange={handleChange}
                disabled={loading}
              >
                <option value="inches">Inches</option>
                <option value="ft">Feet (ft)</option>
                <option value="meters">Meters (m)</option>
              </select>
            </div>
          </div>

          <div className="form-group">
            <label>Languages (Select 1-5) *</label>
            <div className="languages-grid" style={{ 
              display: 'grid', 
              gridTemplateColumns: 'repeat(auto-fill, minmax(150px, 1fr))', 
              gap: '10px',
              maxHeight: '200px',
              overflowY: 'auto',
              padding: '10px',
              border: '1px solid #e2e8f0',
              borderRadius: '6px',
              marginBottom: '10px'
            }}>
              {KENYAN_LANGUAGES.map(lang => (
                <div key={lang} style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                  <input
                    type="checkbox"
                    id={`lang-${lang}`}
                    checked={selectedLanguages.includes(lang)}
                    onChange={() => handleLanguageChange(lang)}
                    disabled={loading}
                  />
                  <label htmlFor={`lang-${lang}`} style={{ fontSize: '0.85rem', margin: 0, fontWeight: 'normal' }}>{lang}</label>
                </div>
              ))}
              <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                <input
                  type="checkbox"
                  id="lang-other"
                  checked={showOtherLanguage}
                  onChange={() => handleLanguageChange('Other')}
                  disabled={loading}
                />
                <label htmlFor="lang-other" style={{ fontSize: '0.85rem', margin: 0, fontWeight: 'normal' }}>Other</label>
              </div>
            </div>
            
            {showOtherLanguage && (
              <input
                type="text"
                placeholder="Enter other language"
                value={otherLanguage}
                onChange={(e) => setOtherLanguage(e.target.value)}
                disabled={loading}
                className="chase-input"
                style={{ marginTop: '5px' }}
              />
            )}
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
                max={(() => {
                  const now = new Date();
                  const offset = now.getTimezoneOffset() * 60000;
                  const localISOTime = new Date(now.getTime() - offset - (60 * 60 * 1000)).toISOString().slice(0, 16);
                  return localISOTime;
                })()}
              />
            </div>

            <div className="form-group">
              <label htmlFor="county">County *</label>
              <select
                id="county"
                value={selectedCounty}
                onChange={handleCountyChange}
                disabled={loading}
                required
              >
                <option value="">Select County</option>
                {Object.keys(KENYA_LOCATIONS).map(county => (
                  <option key={county} value={county}>{county}</option>
                ))}
              </select>
            </div>
          </div>

          <div className="form-row">
            <div className="form-group">
              <label htmlFor="subcounty">Subcounty *</label>
              <select
                id="subcounty"
                value={selectedSubcounty}
                onChange={handleSubcountyChange}
                disabled={loading || !selectedCounty}
                required={!!selectedCounty}
              >
                <option value="">Select Subcounty</option>
                {selectedCounty && KENYA_LOCATIONS[selectedCounty].map(sub => (
                  <option key={sub} value={sub}>{sub}</option>
                ))}
              </select>
            </div>
            
            <div className="form-group">
              <label>Current Selection</label>
              <input 
                type="text" 
                value={formData.last_seen_location} 
                readOnly 
                disabled 
                className="chase-input-readonly"
                style={{ background: '#f8fafc', fontStyle: 'italic', color: '#1e3a8a', fontWeight: 'bold' }}
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
