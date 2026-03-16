import React, { useState, useEffect, useCallback } from 'react';
import { useNavigate, useLocation, Link } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import api from '../services/api';
import '../styles/ChaseUI.css';

const CaseSummaryPage = () => {
    const { user, logout } = useAuth();
    const navigate = useNavigate();
    const location = useLocation();
    const [cases, setCases] = useState([]);
    const [loading, setLoading] = useState(true);

    // Determine page type and title from path
    const path = location.pathname;
    let title = "Your Cases";
    let filterStatus = null;

    if (path === '/reported-cases') {
        title = "Total Cases Reported";
    } else if (path === '/active-searches') {
        title = "Active Searches";
        filterStatus = 'active'; // Logic to filter active cases
    } else if (path === '/resolved-cases') {
        title = "Resolved Cases";
        filterStatus = 'resolved'; // Logic to filter resolved cases
    }

    const fetchCases = useCallback(async () => {
        try {
            const response = await api.getMissingPersons();
            // Handle paginated response: { count, results } or direct array
            const allCases = Array.isArray(response.data) ? response.data : response.data.results;
            let userCases = allCases.filter(caseItem => caseItem.reported_by === user.id);

            if (filterStatus === 'active') {
                userCases = userCases.filter(c => c.status !== 'CLOSED');
            } else if (filterStatus === 'resolved') {
                userCases = userCases.filter(c => c.status === 'CLOSED');
            }

            setCases(userCases);
        } catch (error) {
            console.error('Error fetching cases:', error);
        } finally {
            setLoading(false);
        }
    }, [user, filterStatus]);

    useEffect(() => {
        if (user && user.role === 'family_member') {
            fetchCases();
        } else if (user) {
            navigate('/login');
        }
    }, [user, navigate, fetchCases]);

    const handleLogout = () => {
        logout();
        navigate('/login');
    };

    if (loading) return <div className="chase-body"><div className="chase-container">Loading cases...</div></div>;

    return (
        <div className="chase-body">
            <header className="chase-header">
                <div className="chase-logo">Sura<span>Smart</span></div>
                <div style={{ display: 'flex', alignItems: 'center', gap: '20px' }}>
                    <span>{user?.first_name} {user?.last_name}</span>
                    <button onClick={handleLogout} className="chase-button-outline" style={{ color: 'white', borderColor: 'white', padding: '0.5rem 1rem' }}>Logout</button>
                </div>
            </header>

            <div className="chase-container">
                <div style={{ marginBottom: '20px' }}>
                    <Link to="/family-dashboard" style={{ color: 'var(--chase-blue)', textDecoration: 'none', fontWeight: '600' }}>← Back to Dashboard</Link>
                </div>

                <h1 className="chase-title">{title}</h1>

                <div className="chase-card" style={{ padding: 0 }}>
                    {cases.length === 0 ? (
                        <div style={{ padding: '40px', textAlign: 'center', color: 'var(--chase-gray-500)' }}>
                            No cases found in this category.
                        </div>
                    ) : (
                        <div style={{ padding: '0 24px' }}>
                            {cases.map(caseItem => (
                                <div key={caseItem.id} className="chase-list-item">
                                    <div>
                                        <div style={{ fontWeight: '600', fontSize: '1.1rem', marginBottom: '4px' }}>{caseItem.full_name}</div>
                                        <div style={{ fontSize: '0.85rem', color: 'var(--chase-gray-500)' }}>
                                            Reported on {new Date(caseItem.date_reported).toLocaleDateString()}
                                        </div>
                                    </div>
                                    <div style={{ display: 'flex', alignItems: 'center', gap: '24px' }}>
                                        <span className={`chase-status-pill ${caseItem.status === 'CLOSED' ? 'status-resolved' : 'status-active'}`}>
                                            {caseItem.status}
                                        </span>
                                        <Link to={`/missing-person/${caseItem.id}`} className="chase-button-outline" style={{ padding: '6px 16px', fontSize: '0.85rem' }}>
                                            View Details
                                        </Link>
                                    </div>
                                </div>
                            ))}
                        </div>
                    )}
                </div>
            </div>
        </div>
    );
};

export default CaseSummaryPage;
