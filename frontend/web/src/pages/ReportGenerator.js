import React, { useState, useEffect, useCallback } from 'react';
import { useParams, useNavigate, Link } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import api from '../services/api';
import '../styles/ReportGenerator.css';

const ReportGenerator = () => {
    const { id } = useParams();
    const navigate = useNavigate();
    const { user } = useAuth();
    
    const [cases, setCases] = useState([]);
    const [selectedCase, setSelectedCase] = useState(null);
    const [loading, setLoading] = useState(false);
    const [searchQuery, setSearchQuery] = useState('');
    const [officialStatement, setOfficialStatement] = useState('');
    const [reportDate] = useState(new Date().toLocaleDateString());

    const fetchCases = useCallback(async () => {
        try {
            setLoading(true);
            const response = await api.getMissingPersons();
            // Handle different API response structures
            const results = response.data.results || response.data || [];
            setCases(results);
        } catch (error) {
            console.error('Error fetching cases:', error);
        } finally {
            setLoading(false);
        }
    }, []);

    const fetchSpecificCase = useCallback(async (caseId) => {
        try {
            setLoading(true);
            const response = await api.getMissingPerson(caseId);
            setSelectedCase(response.data);
            if (response.data.police_analysis_report) {
                setOfficialStatement(response.data.police_analysis_report);
            }
        } catch (error) {
            console.error('Error fetching case:', error);
        } finally {
            setLoading(false);
        }
    }, []);

    useEffect(() => {
        if (id) {
            fetchSpecificCase(id);
        } else {
            fetchCases();
        }
    }, [id, fetchCases, fetchSpecificCase]);

    const handlePrint = () => {
        window.print();
    };

    const filteredCases = cases.filter(c => 
        c.full_name.toLowerCase().includes(searchQuery.toLowerCase()) ||
        c.id.includes(searchQuery)
    );

    if (loading && !selectedCase) {
        return <div className="chase-body"><div className="chase-container">Loading Case Data...</div></div>;
    }

    // Selection View
    if (!id && !selectedCase) {
        return (
            <div className="chase-body no-print">
                <header className="chase-header">
                    <div className="chase-logo">Sura<span>Smart</span></div>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '20px' }}>
                        <span style={{ color: 'white' }}>Officer {user?.first_name}</span>
                        <Link to="/police-dashboard" className="chase-button-outline" style={{ color: 'white', borderColor: 'white', textDecoration: 'none', padding: '0.5rem 1rem' }}>Dashboard</Link>
                    </div>
                </header>

                <div className="chase-container">
                    <div className="chase-card" style={{ padding: '2rem' }}>
                        <h1 style={{ color: 'var(--chase-blue-dark)', marginBottom: '1.5rem' }}>Select Case for Reporting</h1>
                        
                        <div style={{ marginBottom: '2rem' }}>
                            <input 
                                type="text" 
                                placeholder="Search by name or case ID..." 
                                className="chase-input"
                                value={searchQuery}
                                onChange={(e) => setSearchQuery(e.target.value)}
                                style={{ maxWidth: '400px' }}
                            />
                        </div>

                        <div className="chase-list">
                            {filteredCases.map(c => (
                                <div key={c.id} className="chase-list-item" style={{ padding: '1.25rem' }}>
                                    <div>
                                        <h3 style={{ margin: 0, color: 'var(--chase-blue-dark)' }}>{c.full_name}</h3>
                                        <p style={{ margin: '4px 0 0 0', color: 'var(--chase-gray-500)', fontSize: '0.9rem' }}>
                                            Status: {c.status} | Reported: {new Date(c.date_reported).toLocaleDateString()}
                                        </p>
                                    </div>
                                    <button 
                                        onClick={() => navigate(`/reports/${c.id}`)}
                                        className="chase-button"
                                        style={{ padding: '0.5rem 1rem' }}
                                    >
                                        Generate Report
                                    </button>
                                </div>
                            ))}
                            {filteredCases.length === 0 && <p style={{ textAlign: 'center', color: 'var(--chase-gray-500)', padding: '2rem' }}>No matching cases found.</p>}
                        </div>
                    </div>
                </div>
            </div>
        );
    }

    // Report Detail View
    return (
        <div className="report-page-container">
            {/* Action Bar (Hidden when printing) */}
            <div className="report-action-bar no-print">
                <div className="chase-container" style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                    <button onClick={() => navigate('/reports')} className="chase-button-outline" style={{ borderColor: 'white', color: 'white' }}>
                        ← Select Different Case
                    </button>
                    <div style={{ display: 'flex', gap: '15px' }}>
                        <button onClick={handlePrint} className="chase-button" style={{ background: 'white', color: 'var(--chase-blue-dark)' }}>
                            🖨️ Print Report
                        </button>
                        <Link to="/police-dashboard" className="chase-button" style={{ background: 'rgba(255,255,255,0.2)', color: 'white' }}>
                            Dashboard
                        </Link>
                    </div>
                </div>
            </div>

            {/* Actual Report Document */}
            <div className="report-document">
                <header className="report-header">
                    <div className="report-header-left">
                        <div className="report-branding">Sura<span>Smart</span></div>
                        <p className="report-unit">National Facial Recognition & Missing Persons Registry</p>
                        <p className="report-entity">Department of Public Safety - Identity Management Division</p>
                    </div>
                    <div className="report-header-right">
                        <div className="report-meta">
                            <p><strong>REPORT TYPE:</strong> OFFICIAL CASE SUMMARY</p>
                            <p><strong>CASE REF:</strong> {selectedCase?.id?.substring(0, 13).toUpperCase()}</p>
                            <p><strong>DATE ISSUED:</strong> {reportDate}</p>
                        </div>
                    </div>
                </header>

                <div className="report-watermark">CONFIDENTIAL</div>

                <section className="report-section">
                    <h2 className="section-title">Case Information</h2>
                    <div className="report-grid">
                        <div className="report-info-group">
                            <label>Subject Full Name</label>
                            <div className="info-value">{selectedCase?.full_name}</div>
                        </div>
                        <div className="report-info-group">
                            <label>Current Status</label>
                            <div className="info-value">{selectedCase?.status}</div>
                        </div>
                        <div className="report-info-group">
                            <label>Age / Gender</label>
                            <div className="info-value">{selectedCase?.age || 'N/A'} | {selectedCase?.gender?.toUpperCase() || 'N/A'}</div>
                        </div>
                        <div className="report-info-group">
                            <label>Report Date</label>
                            <div className="info-value">{new Date(selectedCase?.date_reported).toLocaleString()}</div>
                        </div>
                    </div>
                </section>

                <section className="report-section">
                    <h2 className="section-title">Incident Details</h2>
                    <div className="report-grid">
                        <div className="report-info-group full-width">
                            <label>Last Known Location</label>
                            <div className="info-value">{selectedCase?.last_seen_location || 'Not Specified'}</div>
                        </div>
                        <div className="report-info-group full-width">
                            <label>Physical Description & Identifying Marks</label>
                            <div className="info-value" style={{ whiteSpace: 'pre-wrap' }}>
                                {selectedCase?.description}
                                {selectedCase?.identifying_marks && `\n\nMarks: ${selectedCase.identifying_marks}`}
                            </div>
                        </div>
                    </div>
                </section>

                <section className="report-section">
                    <h2 className="section-title">Official Identification Data</h2>
                    <p className="section-hint">Facial recognition images and biometric reference data captured by the system.</p>
                    <div className="report-image-gallery">
                        {selectedCase?.facial_recognition_images?.map(img => (
                            <div key={img.id} className="report-image-item">
                                <img src={img.image_file} alt="Evidence" />
                                <span className="image-tag">{img.is_primary ? 'PRIMARY' : 'REFERENCE'}</span>
                            </div>
                        ))}
                        {(!selectedCase?.facial_recognition_images || selectedCase.facial_recognition_images.length === 0) && (
                            <p className="no-data">No facial biometric data available for this case.</p>
                        )}
                    </div>
                </section>

                <section className="report-section no-break">
                    <h2 className="section-title">Officer Statement of Analysis</h2>
                    <textarea 
                        className="report-textarea no-print"
                        placeholder="Type official analysis findings here. This content is editable before printing..."
                        value={officialStatement}
                        onChange={(e) => setOfficialStatement(e.target.value)}
                    ></textarea>
                    {/* Print-only statement display */}
                    <div className="print-only-statement">
                        {officialStatement || "No official statement provided at the time of report generation."}
                    </div>
                </section>

                <footer className="report-footer">
                    <div className="signature-section">
                        <div className="signature-box">
                            <div className="sig-line"></div>
                            <p>Authorized Officer Signature</p>
                            <p><strong>{user?.first_name} {user?.last_name}</strong></p>
                        </div>
                        <div className="signature-box">
                            <div className="sig-line"></div>
                            <p>Official Unit Stamp / Validation</p>
                            <p>SuraSmart Identity Division</p>
                        </div>
                    </div>
                    <div className="report-legal">
                        This document is a computer-generated official report from the SuraSmart Missing Persons Platform. 
                        The information contained herein is subject to real-time updates and should be verified against the live database records.
                        All facial recognition matches are subject to Human-in-the-Loop verification requirements.
                    </div>
                </footer>
            </div>
        </div>
    );
};

export default ReportGenerator;
