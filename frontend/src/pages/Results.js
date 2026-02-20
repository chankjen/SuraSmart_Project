import React, { useState, useEffect, useCallback } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import api from '../services/api';
import '../styles/Results.css';

const Results = () => {
  const { missingPersonId } = useParams();
  const navigate = useNavigate();
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [missingPerson, setMissingPerson] = useState(null);
  const [matches, setMatches] = useState([]);
  const [processingQueue, setProcessingQueue] = useState([]);
  const [autoRefresh, setAutoRefresh] = useState(true);

  const fetchData = useCallback(async () => {
    try {
      const [personRes, matchesRes, queueRes] = await Promise.all([
        api.getMissingPerson(missingPersonId),
        api.getMatches({ missing_person: missingPersonId }),
        api.getProcessingQueue(),
      ]);

      setMissingPerson(personRes.data);
      setMatches(matchesRes.data.results || []);
      setProcessingQueue(queueRes.data.results || []);
      setError(null);
    } catch (err) {
      setError('Failed to load results');
      console.error(err);
    } finally {
      setLoading(false);
    }
  }, [missingPersonId]);

  useEffect(() => {
    fetchData();

    if (autoRefresh) {
      const interval = setInterval(fetchData, 3000);
      return () => clearInterval(interval);
    }
  }, [autoRefresh, fetchData]);

  const handleVerifyMatch = async (matchId) => {
    try {
      const notes = window.prompt('Enter verification notes (optional):');
      await api.verifyMatch(matchId, notes || '');
      fetchData();
    } catch (err) {
      alert('Failed to verify match');
    }
  };

  const handleRejectMatch = async (matchId) => {
    try {
      const notes = window.prompt('Enter reason for rejection (optional):');
      await api.rejectMatch(matchId, notes || '');
      fetchData();
    } catch (err) {
      alert('Failed to reject match');
    }
  };

  if (loading) {
    return (
      <div className="results-container">
        <div className="loading">Loading results...</div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="results-container">
        <div className="error-message">{error}</div>
      </div>
    );
  }

  const processingItems = processingQueue.filter(
    (item) => item.image && item.status === 'processing'
  );
  const pendingMatches = matches.filter((m) => m.status === 'pending_review');
  const verifiedMatches = matches.filter((m) => m.status === 'verified');
  const rejectedMatches = matches.filter((m) => m.status === 'false_positive');

  return (
    <div className="results-container">
      <div className="results-header">
        <button onClick={() => navigate('/dashboard')} className="btn-secondary">
          ← Back to Dashboard
        </button>
        <h1>Search Results</h1>
        <label className="auto-refresh-toggle">
          <input
            type="checkbox"
            checked={autoRefresh}
            onChange={(e) => setAutoRefresh(e.target.checked)}
          />
          Auto-refresh
        </label>
      </div>

      <div className="person-info">
        <h2>{missingPerson?.full_name}</h2>
        <p>Status: <span className={`status-badge status-${missingPerson?.status}`}>
          {missingPerson?.status?.toUpperCase()}
        </span></p>
        {missingPerson?.description && (
          <p><strong>Description:</strong> {missingPerson.description}</p>
        )}
        {missingPerson?.last_seen_location && (
          <p><strong>Last Seen:</strong> {missingPerson.last_seen_location}</p>
        )}
      </div>

      {processingItems.length > 0 && (
        <div className="section">
          <h3>🔄 Processing</h3>
          <div className="processing-list">
            {processingItems.map((item) => (
              <div key={item.id} className="processing-item">
                <p>Image {item.id.slice(0, 8)}... is being processed</p>
                <div className="progress-bar">
                  <div className="progress-fill"></div>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {pendingMatches.length > 0 && (
        <div className="section">
          <h3>⚠️ Pending Review ({pendingMatches.length})</h3>
          <div className="matches-grid">
            {pendingMatches.map((match) => (
              <div key={match.id} className="match-card pending">
                <div className="match-confidence">
                  {(match.match_confidence * 100).toFixed(1)}%
                </div>
                <p><strong>Source:</strong> {match.source_database}</p>
                <p><strong>Distance:</strong> {match.distance_metric?.toFixed(3)}</p>
                <div className="match-actions">
                  <button
                    onClick={() => handleVerifyMatch(match.id)}
                    className="btn-success btn-small"
                  >
                    Verify
                  </button>
                  <button
                    onClick={() => handleRejectMatch(match.id)}
                    className="btn-danger btn-small"
                  >
                    Reject
                  </button>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {verifiedMatches.length > 0 && (
        <div className="section">
          <h3>✅ Verified Matches ({verifiedMatches.length})</h3>
          <div className="matches-grid">
            {verifiedMatches.map((match) => (
              <div key={match.id} className="match-card verified">
                <div className="match-confidence verified-badge">
                  {(match.match_confidence * 100).toFixed(1)}%
                </div>
                <p><strong>Source:</strong> {match.source_database}</p>
                <p><strong>Verified by:</strong> {match.verified_by}</p>
                {match.verification_notes && (
                  <p><strong>Notes:</strong> {match.verification_notes}</p>
                )}
              </div>
            ))}
          </div>
        </div>
      )}

      {rejectedMatches.length > 0 && (
        <div className="section">
          <h3>❌ Rejected ({rejectedMatches.length})</h3>
          <div className="matches-grid">
            {rejectedMatches.map((match) => (
              <div key={match.id} className="match-card rejected">
                <p><strong>Source:</strong> {match.source_database}</p>
                {match.verification_notes && (
                  <p><strong>Reason:</strong> {match.verification_notes}</p>
                )}
              </div>
            ))}
          </div>
        </div>
      )}

      {matches.length === 0 && processingItems.length === 0 && (
        <div className="no-results">
          <p>No matches found yet. Please check back later as processing may be ongoing.</p>
        </div>
      )}
    </div>
  );
};

export default Results;
