import React, { useState, useEffect, useCallback } from 'react';
import { useParams, useNavigate, Link } from 'react-router-dom';
import api from '../services/api';
import '../styles/ChaseUI.css';

const AdminUserDetails = () => {
    const { userId } = useParams();
    const navigate = useNavigate();
    const [userData, setUserData] = useState(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);

    const fetchUserDetails = useCallback(async () => {
        try {
            setLoading(true);
            const response = await api.getUser(userId);
            setUserData(response.data);
            setError(null);
        } catch (err) {
            console.error('Error fetching user details:', err);
            setError('Failed to load user details. Please try again.');
        } finally {
            setLoading(false);
        }
    }, [userId]);

    useEffect(() => {
        fetchUserDetails();
    }, [fetchUserDetails]);

    const handleApprove = async () => {
        if (!window.confirm('Are you sure you want to approve this user?')) return;
        try {
            await api.approveUserRegistration(userId, { notes: 'Approved via details view' });
            alert('User approved successfully!');
            fetchUserDetails();
        } catch (err) {
            console.error('Error approving user:', err);
            alert('Failed to approve user.');
        }
    };

    const handleReject = async () => {
        const reason = window.prompt('Enter reason for disapproval:', 'Details inconsistency');
        if (reason === null) return;
        try {
            await api.rejectUserRegistration(userId, { reason });
            alert('User disapproved.');
            fetchUserDetails();
        } catch (err) {
            console.error('Error rejecting user:', err);
            alert('Failed to disapprove user.');
        }
    };

    if (loading) {
        return (
            <div className="chase-body">
                <div className="chase-header">
                    <div className="chase-logo">Sura <span>Smart</span></div>
                </div>
                <div className="chase-container" style={{ textAlign: 'center', padding: '100px' }}>
                    <p style={{ fontSize: '1.2rem', color: 'var(--chase-gray-500)' }}>Loading user details...</p>
                </div>
            </div>
        );
    }

    if (error || !userData) {
        return (
            <div className="chase-body">
                <div className="chase-header">
                    <div className="chase-logo">Sura <span>Smart</span></div>
                </div>
                <div className="chase-container">
                    <Link to="/admin-dashboard" className="chase-button-outline" style={{ marginBottom: '20px', display: 'inline-block' }}>
                        ← Back to Dashboard
                    </Link>
                    <div className="chase-card" style={{ textAlign: 'center', padding: '60px' }}>
                        <p style={{ color: '#dc2626', fontWeight: 'bold' }}>{error || 'User not found'}</p>
                    </div>
                </div>
            </div>
        );
    }

    return (
        <div className="chase-body">
            <div className="chase-header">
                <div className="chase-logo">Sura <span>Smart</span></div>
                <div style={{ display: 'flex', gap: '20px' }}>
                    <Link to="/admin-dashboard" style={{ color: 'white', textDecoration: 'none', fontWeight: '600' }}>Dashboard</Link>
                </div>
            </div>

            <div className="chase-container">
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '30px' }}>
                    <h1 className="chase-title" style={{ marginBottom: 0 }}>User Details</h1>
                    <div style={{ display: 'flex', gap: '10px' }}>
                        <Link to="/admin-dashboard" className="chase-button-outline">Back to List</Link>
                        {userData.verification_status === 'pending' && (
                            <>
                                <button onClick={handleApprove} className="chase-button">Approve User</button>
                                <button onClick={handleReject} className="chase-button-outline" style={{ color: '#dc2626', borderColor: '#dc2626' }}>Disapprove</button>
                            </>
                        )}
                    </div>
                </div>

                <div style={{ display: 'grid', gridTemplateColumns: '1fr 2fr', gap: '30px' }}>
                    {/* Basic Info */}
                    <div>
                        <div className="chase-card" style={{ marginBottom: '20px' }}>
                            <div className="chase-stat-label">Verification Status</div>
                            <div style={{ marginTop: '10px' }}>
                                <span className="chase-status-pill" style={{ 
                                    background: userData.verification_status === 'pending' ? '#fef3c7' : 
                                               userData.verification_status === 'verified' ? '#dcfce7' : '#fef2f2',
                                    color: userData.verification_status === 'pending' ? '#92400e' : 
                                           userData.verification_status === 'verified' ? '#166534' : '#991b1b',
                                    fontSize: '0.9rem',
                                    padding: '8px 16px'
                                }}>
                                    {userData.verification_status.toUpperCase()}
                                </span>
                            </div>
                        </div>

                        <div className="chase-card">
                            <h3 style={{ borderBottom: '1px solid var(--chase-gray-100)', paddingBottom: '10px', marginBottom: '15px', color: 'var(--chase-blue-dark)' }}>Account Overview</h3>
                            <div style={{ display: 'flex', flexDirection: 'column', gap: '15px' }}>
                                <div>
                                    <div className="chase-stat-label" style={{ fontSize: '0.75rem' }}>Username</div>
                                    <div style={{ fontWeight: '600' }}>{userData.username}</div>
                                </div>
                                <div>
                                    <div className="chase-stat-label" style={{ fontSize: '0.75rem' }}>Full Name</div>
                                    <div style={{ fontWeight: '600' }}>{userData.first_name} {userData.last_name}</div>
                                </div>
                                <div>
                                    <div className="chase-stat-label" style={{ fontSize: '0.75rem' }}>Email Address</div>
                                    <div style={{ fontWeight: '600' }}>{userData.email}</div>
                                </div>
                                <div>
                                    <div className="chase-stat-label" style={{ fontSize: '0.75rem' }}>Date Joined</div>
                                    <div style={{ fontWeight: '600' }}>{new Date(userData.created_at).toLocaleString()}</div>
                                </div>
                            </div>
                        </div>
                    </div>

                    {/* Registration Details */}
                    <div className="chase-card">
                        <h3 style={{ borderBottom: '1px solid var(--chase-gray-100)', paddingBottom: '10px', marginBottom: '20px', color: 'var(--chase-blue-dark)' }}>Registration Information</h3>
                        
                        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '30px' }}>
                            <div>
                                <h4 style={{ color: 'var(--chase-blue)', marginBottom: '15px' }}>Identity & Role</h4>
                                <div style={{ display: 'flex', flexDirection: 'column', gap: '20px' }}>
                                    <div className="chase-list-item" style={{ flexDirection: 'column', alignItems: 'flex-start', borderBottom: 'none', padding: 0 }}>
                                        <div className="chase-stat-label" style={{ fontSize: '0.7rem' }}>Primary Role</div>
                                        <div style={{ fontWeight: '600', textTransform: 'capitalize' }}>{userData.role.replace('_', ' ')}</div>
                                    </div>

                                    {userData.national_id && (
                                        <div className="chase-list-item" style={{ flexDirection: 'column', alignItems: 'flex-start', borderBottom: 'none', padding: 0 }}>
                                            <div className="chase-stat-label" style={{ fontSize: '0.7rem' }}>National ID Number</div>
                                            <div style={{ fontWeight: '600', fontSize: '1.1rem', color: 'var(--chase-blue-dark)' }}>{userData.national_id}</div>
                                        </div>
                                    )}

                                    {userData.service_id && (
                                        <div className="chase-list-item" style={{ flexDirection: 'column', alignItems: 'flex-start', borderBottom: 'none', padding: 0 }}>
                                            <div className="chase-stat-label" style={{ fontSize: '0.7rem' }}>Police Service ID</div>
                                            <div style={{ fontWeight: '600', fontSize: '1.1rem', color: 'var(--chase-blue-dark)' }}>{userData.service_id}</div>
                                        </div>
                                    )}

                                    {userData.police_rank && (
                                        <div className="chase-list-item" style={{ flexDirection: 'column', alignItems: 'flex-start', borderBottom: 'none', padding: 0 }}>
                                            <div className="chase-stat-label" style={{ fontSize: '0.7rem' }}>Police Rank</div>
                                            <div style={{ fontWeight: '600' }}>{userData.police_rank_display || userData.police_rank}</div>
                                        </div>
                                    )}

                                    {userData.government_security_id && (
                                        <div className="chase-list-item" style={{ flexDirection: 'column', alignItems: 'flex-start', borderBottom: 'none', padding: 0 }}>
                                            <div className="chase-stat-label" style={{ fontSize: '0.7rem' }}>Gov. Security Number</div>
                                            <div style={{ fontWeight: '600', fontSize: '1.1rem', color: 'var(--chase-blue-dark)' }}>{userData.government_security_id}</div>
                                        </div>
                                    )}
                                </div>
                            </div>

                            <div>
                                <h4 style={{ color: 'var(--chase-blue)', marginBottom: '15px' }}>Organization & Contact</h4>
                                <div style={{ display: 'flex', flexDirection: 'column', gap: '20px' }}>
                                    <div className="chase-list-item" style={{ flexDirection: 'column', alignItems: 'flex-start', borderBottom: 'none', padding: 0 }}>
                                        <div className="chase-stat-label" style={{ fontSize: '0.7rem' }}>Phone Number</div>
                                        <div style={{ fontWeight: '600' }}>{userData.phone_number || 'Not provided'}</div>
                                    </div>

                                    <div className="chase-list-item" style={{ flexDirection: 'column', alignItems: 'flex-start', borderBottom: 'none', padding: 0 }}>
                                        <div className="chase-stat-label" style={{ fontSize: '0.7rem' }}>Organization / Station</div>
                                        <div style={{ fontWeight: '600' }}>{userData.organization || 'Not provided'}</div>
                                    </div>

                                    {userData.government_position && (
                                        <div className="chase-list-item" style={{ flexDirection: 'column', alignItems: 'flex-start', borderBottom: 'none', padding: 0 }}>
                                            <div className="chase-stat-label" style={{ fontSize: '0.7rem' }}>Position</div>
                                            <div style={{ fontWeight: '600' }}>
                                                {userData.government_position === 'other' ? userData.position_specify : userData.government_position}
                                            </div>
                                        </div>
                                    )}
                                </div>
                            </div>
                        </div>

                        <div style={{ marginTop: '40px', padding: '20px', background: 'var(--chase-gray-50)', borderRadius: 'var(--radius)', border: '1px solid var(--chase-gray-100)' }}>
                            <h4 style={{ margin: '0 0 10px 0', fontSize: '0.9rem' }}>Compliance & Audit Info</h4>
                            <p style={{ margin: 0, fontSize: '0.85rem', color: 'var(--chase-gray-500)' }}>
                                This user registered from within the <strong>{userData.jurisdiction || 'KE'}</strong> jurisdiction. 
                                All data is stored in compliance with local data protection regulations. 
                                Internal System ID: <code>{userData.id}</code>
                            </p>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    );
};

export default AdminUserDetails;
