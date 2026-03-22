import React, { useState, useEffect, useCallback } from 'react';
import { useParams, useNavigate, Link } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import api from '../services/api';
import '../styles/ChaseUI.css';

const MissingPersonDetails = () => {
    const { id } = useParams();
    const navigate = useNavigate();
    const { user } = useAuth();
    const [missingPerson, setMissingPerson] = useState(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);

    const fetchData = useCallback(async () => {
        try {
            setLoading(true);
            const response = await api.getMissingPerson(id);
            setMissingPerson(response.data);
        } catch (err) {
            console.error('Error fetching missing person details:', err);
            setError('Failed to load missing person details. Please try again later.');
        } finally {
            setLoading(false);
        }
    }, [id]);

    useEffect(() => {
        fetchData();
    }, [fetchData]);

    const handleApproveClosure = async () => {
        if (!window.confirm('Are you sure you want to approve this match and close the case? (Dual Signature)')) return;
        try {
            await api.signClosure(id);
            alert('Case closure signed. If the police have also signed, the case is now CLOSED.');
            fetchData();
        } catch (err) {
            console.error('Error closing case:', err);
            alert('Failed to sign case closure.');
        }
    };

    const handleRaiseCase = async () => {
        if (!window.confirm('Are you sure you want to raise this case to the police?')) return;
        try {
            await api.raiseCase(id);
            alert('Case successfully raised to the police.');
            fetchData();
        } catch (err) {
            console.error('Error raising case:', err);
            alert('Failed to raise case.');
        }
    };

    if (loading) return <div className="chase-body"><div className="chase-container">Loading details...</div></div>;
    if (error) return <div className="chase-body"><div className="chase-container"><div className="chase-card" style={{ color: 'red' }}>{error}</div></div></div>;
    if (!missingPerson) return <div className="chase-body"><div className="chase-container">Person not found.</div></div>;

    return (
        <div className="chase-body">
            <header className="chase-header">
                <div className="chase-logo">Sura<span>Smart</span></div>
                <div style={{ display: 'flex', alignItems: 'center', gap: '20px' }}>
                    <span style={{ color: 'white' }}>{user?.first_name} {user?.last_name}</span>
                    <Link 
                        to={user?.role === 'police_officer' ? '/police-dashboard' : user?.role === 'government_official' ? '/government-dashboard' : '/family-dashboard'} 
                        className="chase-button-outline" 
                        style={{ color: 'white', borderColor: 'white', padding: '0.5rem 1rem', textDecoration: 'none' }}
                    >
                        Dashboard
                    </Link>
                </div>
            </header>

            <div className="chase-container">
                <div style={{ marginBottom: '20px' }}>
                    <button onClick={() => navigate(-1)} style={{ background: 'none', border: 'none', color: 'var(--chase-blue)', fontWeight: '600', cursor: 'pointer', display: 'flex', alignItems: 'center', gap: '8px' }}>
                        ← Back
                    </button>
                </div>

                <div className="chase-card" style={{ padding: '2rem' }}>
                    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '2rem', borderBottom: '1px solid var(--chase-gray-100)', paddingBottom: '1.5rem' }}>
                        <div>
                            <h1 style={{ fontSize: '2rem', color: 'var(--chase-blue-dark)', marginBottom: '8px' }}>{missingPerson.full_name}</h1>
                            <div style={{ display: 'flex', gap: '12px', alignItems: 'center' }}>
                                {missingPerson.status === 'CLOSED' ? (
                                    <button disabled className="chase-button" style={{ padding: '6px 12px', fontSize: '0.85rem', background: '#dc2626', cursor: 'default' }}>
                                        Case Closed
                                    </button>
                                ) : (
                                    <span className={`chase-status-pill status-active`}>
                                        {missingPerson.status}
                                    </span>
                                )}
                                <span style={{ color: 'var(--chase-gray-500)', fontSize: '0.9rem' }}>
                                    Case ID: {missingPerson.id.substring(0, 8)}...
                                </span>
                            </div>
                        </div>
                        <div style={{ display: 'flex', gap: '10px' }}>
                            {missingPerson.status === 'REPORTED' && user?.role === 'family_member' && (
                                <button onClick={handleRaiseCase} className="chase-button" style={{ padding: '0.75rem 1.5rem' }}>
                                    Raise to Police
                                </button>
                            )}
                            {missingPerson.status === 'PENDING_CLOSURE' && user?.role === 'family_member' && (
                                <div style={{ display: 'flex', flexDirection: 'column', gap: '8px', alignItems: 'flex-end' }}>
                                    {!missingPerson.dual_signature_family ? (
                                        <button 
                                            onClick={handleApproveClosure} 
                                            className="chase-button" 
                                            style={{ padding: '0.75rem 1.5rem', background: 'var(--chase-green)' }}
                                        >
                                            {missingPerson.dual_signature_police ? 'Finalize & Close Case' : 'Approve Closure'}
                                        </button>
                                    ) : (
                                        <span className="chase-status-pill" style={{ background: '#fef3c7', color: '#92400e', border: '1px solid #f59e0b' }}>
                                            Family Signed - Awaiting Police
                                        </span>
                                    )}
                                    {missingPerson.dual_signature_police && !missingPerson.dual_signature_family && (
                                        <small style={{ color: 'var(--chase-green)', fontSize: '0.85rem', fontWeight: 'bold' }}>✓ Police Signature Verified</small>
                                    )}
                                </div>
                            )}
                        </div>
                    </div>

                    <div className="chase-grid" style={{ gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))', gap: '2rem' }}>
                        <div>
                            <h3 style={{ color: 'var(--chase-blue)', marginBottom: '1rem', borderBottom: '1px solid var(--chase-gray-100)', paddingBottom: '0.5rem' }}>Personal Information</h3>
                            <div style={{ display: 'grid', gap: '12px' }}>
                                <p><strong>Age:</strong> {missingPerson.age || 'Not specified'}</p>
                                <p><strong>Gender:</strong> {missingPerson.gender ? missingPerson.gender.charAt(0).toUpperCase() + missingPerson.gender.slice(1) : 'Not specified'}</p>
                                <p><strong>Eye Color:</strong> {missingPerson.eye_color || 'Not specified'}</p>
                                <p><strong>Complexion:</strong> {missingPerson.complexion || 'Not specified'}</p>
                                <p><strong>Height:</strong> {missingPerson.height ? `${missingPerson.height} ${missingPerson.height_unit}` : 'Not specified'}</p>
                                <p><strong>Languages:</strong> {missingPerson.languages || 'Not specified'}</p>
                                <p><strong>Identifying Marks:</strong> {missingPerson.identifying_marks || 'None reported'}</p>
                                <p><strong>Description:</strong> {missingPerson.description || 'No description provided'}</p>
                            </div>
                        </div>

                        <div>
                            <h3 style={{ color: 'var(--chase-blue)', marginBottom: '1rem', borderBottom: '1px solid var(--chase-gray-100)', paddingBottom: '0.5rem' }}>Last Seen Details</h3>
                            <div style={{ display: 'grid', gap: '12px' }}>
                                <p><strong>Date:</strong> {missingPerson.last_seen_date ? new Date(missingPerson.last_seen_date).toLocaleDateString() : 'Not specified'}</p>
                                <p><strong>Location:</strong> {missingPerson.last_seen_location || 'Not specified'}</p>
                                <p><strong>Jurisdiction:</strong> {missingPerson.jurisdiction}</p>
                            </div>
                        </div>
                    </div>

                    {/* Photo Gallery */}
                    <div style={{ marginTop: '3rem' }}>
                        <h3 style={{ color: 'var(--chase-blue)', marginBottom: '1.5rem', borderBottom: '1px solid var(--chase-gray-100)', paddingBottom: '0.5rem' }}>Uploaded Photos</h3>
                        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(150px, 1fr))', gap: '1.5rem' }}>
                            {missingPerson.facial_recognition_images && missingPerson.facial_recognition_images.length > 0 ? (
                                missingPerson.facial_recognition_images.map(img => (
                                    <div key={img.id} style={{ position: 'relative', borderRadius: '12px', overflow: 'hidden', boxShadow: '0 4px 6px rgba(0,0,0,0.1)', border: '1px solid var(--chase-gray-200)' }}>
                                        <img 
                                            src={img.image_file} 
                                            alt="Missing Person" 
                                            style={{ width: '100%', height: '180px', objectFit: 'cover' }} 
                                        />
                                        {img.is_primary && (
                                            <span style={{ position: 'absolute', top: '8px', right: '8px', background: 'var(--chase-blue)', color: 'white', padding: '2px 8px', borderRadius: '4px', fontSize: '0.7rem', fontWeight: 'bold' }}>
                                                PRIMARY
                                            </span>
                                        )}
                                    </div>
                                ))
                            ) : (
                                <div style={{ gridColumn: '1 / -1', padding: '2rem', textAlign: 'center', background: 'var(--chase-gray-50)', borderRadius: '12px', color: 'var(--chase-gray-500)' }}>
                                    No photos uploaded yet. 
                                    <Link to={`/missing-person/${missingPerson.id}/upload`} style={{ marginLeft: '8px', color: 'var(--chase-blue)', fontWeight: '600' }}>Upload Photos</Link>
                                </div>
                            )}
                        </div>
                    </div>

                    {/* Case Findings / Reports */}
                    {(missingPerson.police_analysis_report || missingPerson.government_analysis_report) && (
                        <div style={{ marginTop: '3rem' }}>
                            <h3 style={{ color: 'var(--chase-blue)', marginBottom: '1.5rem', borderBottom: '1px solid var(--chase-gray-100)', paddingBottom: '0.5rem' }}>Official Reports</h3>
                            <div style={{ display: 'grid', gap: '1rem' }}>
                                {missingPerson.police_analysis_report && (
                                    <div style={{ padding: '1.5rem', background: '#f0f9ff', borderRadius: '12px', border: '1px solid #bae6fd' }}>
                                        <h4 style={{ color: '#0369a1', marginBottom: '8px' }}>Police Analysis Report</h4>
                                        <p style={{ color: '#0c4a6e', lineHeight: '1.5' }}>{missingPerson.police_analysis_report}</p>
                                    </div>
                                )}
                                {missingPerson.government_analysis_report && (
                                    <div style={{ padding: '1.5rem', background: '#fef3c7', borderRadius: '12px', border: '1px solid #fde68a' }}>
                                        <h4 style={{ color: '#b45309', marginBottom: '8px' }}>Government Review Report</h4>
                                        <p style={{ color: '#78350f', lineHeight: '1.5' }}>{missingPerson.government_analysis_report}</p>
                                    </div>
                                )}
                            </div>
                        </div>
                    )}
                </div>
            </div>
        </div>
    );
};

export default MissingPersonDetails;
