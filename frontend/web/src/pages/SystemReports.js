import React, { useState, useEffect, useCallback } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import api from '../services/api';
import '../styles/SystemReports.css';

const SystemReports = () => {
    const { user } = useAuth();
    const navigate = useNavigate();
    const [cases, setCases] = useState([]);
    const [loading, setLoading] = useState(true);
    const [filter, setFilter] = useState('ALL');
    const [reportDate] = useState(new Date().toLocaleDateString());

    const fetchReports = useCallback(async () => {
        try {
            setLoading(true);
            const response = await api.getMissingPersons();
            const results = response.data.results || response.data || [];
            setCases(results);
        } catch (error) {
            console.error('Error fetching reports:', error);
        } finally {
            setLoading(false);
        }
    }, []);

    useEffect(() => {
        fetchReports();
    }, [fetchReports]);

    const handlePrint = () => {
        window.print();
    };

    const filteredCases = filter === 'ALL' 
        ? cases 
        : cases.filter(c => c.status === filter);

    if (loading) {
        return <div className="chase-body"><div className="chase-container">Generating Official Report...</div></div>;
    }

    return (
        <div className="system-reports-page">
            <header className="chase-header no-print">
                <div className="chase-logo">Sura<span>Smart</span></div>
                <div style={{ display: 'flex', alignItems: 'center', gap: '20px' }}>
                    <span style={{ color: 'white' }}>Audit Officer {user?.first_name}</span>
                    <Link to="/government-dashboard" className="chase-button-outline" style={{ color: 'white', borderColor: 'white', textDecoration: 'none', padding: '0.5rem 1rem' }}>Dashboard</Link>
                </div>
            </header>

            <div className="chase-container">
                <div className="report-controls no-print">
                    <div>
                        <h1 style={{ color: 'var(--chase-blue-dark)', margin: 0 }}>System Reports Registry</h1>
                        <p style={{ color: 'var(--chase-gray-500)' }}>Configure and generate printable audit summaries.</p>
                    </div>
                    
                    <div style={{ display: 'flex', gap: '15px' }}>
                        <select 
                            className="chase-input" 
                            style={{ padding: '8px 12px' }}
                            value={filter}
                            onChange={(e) => setFilter(e.target.value)}
                        >
                            <option value="ALL">All Statuses</option>
                            <option value="CLOSED">Resolved Only</option>
                            <option value="ESCALATED">Escalations Only</option>
                            <option value="RAISED">Unassigned</option>
                        </select>
                        <button onClick={handlePrint} className="chase-button">
                            🖨️ Print Full Audit
                        </button>
                    </div>
                </div>

                <div className="audit-document">
                    <div className="audit-header">
                        <div className="audit-logo">Sura<span>Smart</span> OFFICIAL AUDIT</div>
                        <div className="audit-meta">
                            <div><strong>DATE:</strong> {reportDate}</div>
                            <div><strong>OFFICER:</strong> {user?.last_name?.toUpperCase()}, {user?.first_name}</div>
                            <div><strong>TOTAL RECORDS:</strong> {filteredCases.length}</div>
                        </div>
                    </div>

                    <div className="audit-table-container">
                        <table className="audit-table">
                            <thead>
                                <tr>
                                    <th>ID</th>
                                    <th>Full Name</th>
                                    <th>Status</th>
                                    <th>Reported Date</th>
                                    <th>Reporter</th>
                                    <th>Jurisdiction</th>
                                </tr>
                            </thead>
                            <tbody>
                                {filteredCases.map(c => (
                                    <tr key={c.id}>
                                        <td><code>{c.id.substring(0, 6)}</code></td>
                                        <td><strong>{c.full_name}</strong></td>
                                        <td>{c.status}</td>
                                        <td>{new Date(c.date_reported).toLocaleDateString()}</td>
                                        <td>
                                            <div style={{fontWeight: 'bold'}}>{c.reporter_name || 'System Generated'}</div>
                                            {c.reporter_blockchain_hash && (
                                                <div style={{fontSize: '0.8em', color: '#64748b', fontFamily: 'monospace'}}>
                                                    {c.reporter_blockchain_hash.substring(0, 16)}...
                                                </div>
                                            )}
                                        </td>
                                        <td>
                                            {(() => {
                                                const loc = c.last_seen_location || '';
                                                const parts = loc.split(', ');
                                                if (parts.length > 1) {
                                                    return `${parts[parts.length - 1]} - ${parts[0]}`;
                                                }
                                                return loc || c.jurisdiction;
                                            })()}
                                        </td>
                                    </tr>
                                ))}
                            </tbody>
                        </table>
                        {filteredCases.length === 0 && (
                            <div style={{ textAlign: 'center', padding: '40px', color: '#718096' }}>
                                No records found matching the current filter criteria.
                            </div>
                        )}
                    </div>

                    <div className="audit-footer">
                        <p>This report is confidential and intended for official government use only. 
                        Unauthorized reproduction or distribution is prohibited by federal law 
                        under the National Public Safety Identity Act.</p>
                        <div className="audit-stamp">OFFICIAL CERTIFIED CASE REGISTRY</div>
                    </div>
                </div>
            </div>
        </div>
    );
};

export default SystemReports;
