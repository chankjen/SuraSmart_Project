import React, { useState, useEffect, useCallback } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import api from '../services/api';
import '../styles/ChaseUI.css';
import { QRCodeCanvas } from 'qrcode.react';

const AdminDashboard = () => {
  const { user, logout } = useAuth();
  const navigate = useNavigate();
  
  // State Management
  const [pendingUsers, setPendingUsers] = useState([]);
  const [auditLogs, setAuditLogs] = useState([]);
  const [systemStats, setSystemStats] = useState({
    totalUsers: 0,
    pendingVerification: 0,
    verifiedUsers: 0,
    systemUptime: '99.95%'
  });
  const [loading, setLoading] = useState(true);
  const [selectedUser, setSelectedUser] = useState(null);
  
  // Verification State
  const [showVerificationModal, setShowVerificationModal] = useState(false);
  const [verificationType, setVerificationType] = useState('');
  const [verificationNumber, setVerificationNumber] = useState('');
  
  // MFA State (TRD §4.2)
  const [showMfaModal, setShowMfaModal] = useState(false);
  const [mfaPassword, setMfaPassword] = useState('');
  const [otpCode, setOtpCode] = useState('');
  const [qrCodeData, setQrCodeData] = useState(null);

  // Audit Filter
  const [auditFilter, setAuditFilter] = useState('all');

  // Verification Types (8-digit requirement)
  const verificationTypes = [
    { value: 'NATIONAL_ID', label: 'National ID (Family Member)', pattern: /^\d{8}$/ },
    { value: 'SERVICE_NUMBER', label: 'Police Service Number', pattern: /^\d{8}$/ },
    { value: 'SECURITY_NUMBER', label: 'Security Number (Government)', pattern: /^\d{8}$/ }
  ];

  // Fetch Data
  const fetchAdminData = useCallback(async () => {
    try {
      const [usersResponse, auditResponse, statsResponse] = await Promise.all([
        api.getAllUsers(),
        api.getAuditLogs(),
        api.getSystemStats()
      ]);

      const allUsers = usersResponse.data.results || usersResponse.data || [];
      const auditLogsData = auditResponse.data.results || auditResponse.data || [];
      
      setPendingUsers(allUsers.filter(u => u.verification_status === 'pending'));
      setAuditLogs(auditLogsData);
      
      setSystemStats({
        totalUsers: statsResponse.data.totalUsers || 0,
        pendingVerification: statsResponse.data.pendingVerification || 0,
        verifiedUsers: statsResponse.data.verifiedUsers || 0,
        systemUptime: statsResponse.data.systemUptime || '99.99%'
      });
    } catch (error) {
      console.error('Error fetching admin ', error);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    if (user === null) return;
    if (user && user.role !== 'admin') {
      navigate('/login');
      return;
    }
    if (user) {
      fetchAdminData();
      const interval = setInterval(fetchAdminData, 30000);
      return () => clearInterval(interval);
    }
  }, [user, navigate, fetchAdminData]);

  const handleLogout = async () => {
    try {
      await api.logAuditEvent({ action: 'ADMIN_LOGOUT', user_id: user.id });
    } catch (error) {
      console.warn('Failed to log admin logout event:', error);
    } finally {
      logout();
      navigate('/login');
    }
  };

  // Step 1: Open Verification Modal
  const handleVerifyClick = (userItem) => {
    setSelectedUser(userItem);
    setShowVerificationModal(true);
    setVerificationType('');
    setVerificationNumber('');
  };

  // Step 2: Handle Verification Input
  const handleVerificationNumberChange = (e) => {
    const value = e.target.value.replace(/\D/g, '');
    if (value.length <= 8) setVerificationNumber(value);
  };

  // Step 3: Trigger MFA Before Approval (TRD §4.2)
  const handleProceedToMfa = async () => {
    if (verificationNumber.length !== 8 || !verificationType) {
      alert('Please complete verification details first.');
      return;
    }

    // Role-based ID matching check
    let expectedId = '';
    if (selectedUser.role === 'family_member') expectedId = selectedUser.national_id;
    else if (selectedUser.role === 'police_officer') expectedId = selectedUser.service_id;
    else if (selectedUser.role === 'government_official') expectedId = selectedUser.government_security_id;

    if (verificationNumber !== expectedId) {
      alert(`ID Mismatch: The input ID number (${verificationNumber}) does not match the registered record for this ${selectedUser.role.replace('_', ' ')}. Please re-entry the 8-digit ID or consider disapproval.`);
      return;
    }
    
    try {
        const response = await api.getMfaQr();
        setQrCodeData(response.data.provisioning_uri);
        setShowVerificationModal(false);
        setShowMfaModal(true);
    } catch (error) {
        console.error('Error fetching MFA QR:', error);
        alert('Failed to initialize MFA. Please try again.');
    }
  };

  // Step 4: Final Approval (After MFA)
  const handleFinalApprove = async () => {
    if (!mfaPassword || otpCode.length !== 6) {
      alert('Please enter your password and binary 6-digit MFA code.');
      return;
    }

    try {
      // 1. Verify MFA + Password (TRIM password to avoid mismatch)
      await api.verifyMFA({ password: mfaPassword.trim(), otp_code: otpCode });

      // 2. Approve User
      await api.approveUserRegistration(selectedUser.id, {
        verified_by: user.id,
        verification_type: verificationType,
        verification_number: verificationNumber
      });

      // 3. Send Email (Backend handles this)
      await api.sendApprovalEmail({
        to: selectedUser.email,
        user_id: selectedUser.id
      });

      // 4. Audit Log
      await api.logAuditEvent({
        action: 'USER_APPROVED',
        user_id: selectedUser.id,
        actor_id: user.id,
        metadata: { verification_type: verificationType, mfa_verified: true }
      });

      alert(`User approved. Login link sent (expires in 10 mins).`);
      setShowMfaModal(false);
      fetchAdminData();
    } catch (error) {
      console.error('Error approving user:', error);
      const errorCode = error.response?.data?.error_code;
      if (errorCode === 'WRONG_PASSWORD') {
        alert('Verification Failed: Incorrect admin password.');
      } else if (errorCode === 'WRONG_OTP') {
        alert('Verification Failed: Invalid MFA code. Please ensure your device time is correct and you are using the latest code.');
      } else {
        alert('Approval failed. Please check your credentials and try again.');
      }
    }
  };

  const handleResetMfa = async () => {
    if (!window.confirm('This will clear your current MFA setup. You will need to scan a new QR code. Continue?')) {
        return;
    }
    try {
        await api.resetMfa();
        // Refresh QR code
        const response = await api.getMfaQr();
        setQrCodeData(response.data.provisioning_uri);
        setOtpCode('');
        alert('MFA has been reset. Please delete the old entry in your app and scan the new QR code.');
    } catch (error) {
        console.error('Error resetting MFA:', error);
        alert('Failed to reset MFA.');
    }
  };

  const handleReject = async (userItem) => {
    let reason = '';
    if (userItem.role === 'family_member') {
      reason = 'Please match ID number with ID Names correctly';
    } else if (userItem.role === 'police_officer') {
      reason = 'Please match your service number with rank correctly';
    } else if (userItem.role === 'government_official') {
      reason = 'Please match your position and government security ID correctly';
    } else {
      reason = 'Details mismatch';
    }

    if (!window.confirm(`Are you sure you want to disapprove ${userItem.first_name} ${userItem.last_name}? Reason: ${reason}`)) {
      return;
    }

    try {
      await api.rejectUserRegistration(userItem.id, { reason });
      await api.logAuditEvent({
        action: 'USER_REJECTED',
        user_id: userItem.id,
        actor_id: user.id,
        metadata: { reason }
      });
      alert(`User disapproved: ${reason}`);
      fetchAdminData();
    } catch (error) {
      console.error('Error disapproving user:', error);
      alert('Disapproval failed.');
    }
  };

  // Export Audit Logs (30-day retention note)
  const handleExportAuditLogs = async () => {
    try {
      const response = await api.exportAuditLogs({ filter: auditFilter });
      const blob = new Blob([response.data], { type: 'text/csv' });
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `sura_audit_logs_${new Date().toISOString().split('T')[0]}.csv`;
      a.click();
    } catch (error) {
      alert('Failed to export audit logs.');
    }
  };

  if (user === null || loading) {
    return <div className="chase-body"><div className="chase-container">Loading Admin Portal...</div></div>;
  }

  return (
    <div className="chase-body">
      {/* Header */}
      <div className="chase-header">
        <div className="chase-logo">Sura <span>Smart</span> Admin</div>
        <div style={{ display: 'flex', alignItems: 'center', gap: '20px' }}>
          <span style={{ color: 'white' }}>Admin: {user?.first_name} {user?.last_name}</span>
          <button onClick={handleLogout} className="chase-button-outline" style={{ color: 'white', borderColor: 'white', padding: '0.5rem 1rem' }}>Logout</button>
        </div>
      </div>

      <div className="chase-container">
        <h1 className="chase-title">Admin Portal - System Oversight</h1>

        {/* Stats */}
        <div className="chase-grid">
          <div className="chase-card">
            <div className="chase-stat-label">Total Users</div>
            <div className="chase-stat-value">{systemStats.totalUsers}</div>
          </div>
          <div className="chase-card" style={{ borderTop: '4px solid #f59e0b' }}>
            <div className="chase-stat-label">Pending Verification</div>
            <div className="chase-stat-value" style={{ color: '#f59e0b' }}>{systemStats.pendingVerification}</div>
          </div>
          <div className="chase-card" style={{ borderTop: '4px solid #10b981' }}>
            <div className="chase-stat-label">Verified Users</div>
            <div className="chase-stat-value" style={{ color: '#10b981' }}>{systemStats.verifiedUsers}</div>
          </div>
          <div className="chase-card">
            <div className="chase-stat-label">System Uptime</div>
            <div className="chase-stat-value" style={{ fontSize: '1.5rem' }}>{systemStats.systemUptime}</div>
          </div>
        </div>

        {/* Pending Users */}
        <div className="chase-section">
          <h2 style={{ marginBottom: '24px', color: 'var(--chase-blue-dark)' }}>
            Pending User Registrations ({pendingUsers.length})
          </h2>
          {pendingUsers.length === 0 ? (
            <div className="chase-card" style={{ textAlign: 'center', padding: '60px' }}>
              <p style={{ color: 'var(--chase-gray-500)' }}>No pending user registrations.</p>
            </div>
          ) : (
            <div className="chase-card" style={{ padding: 0 }}>
              <div style={{ padding: '0 24px' }}>
                {pendingUsers.map(userItem => (
                  <div key={userItem.id} className="chase-list-item" style={{ flexDirection: 'column', alignItems: 'flex-start', gap: '15px', padding: '20px 0' }}>
                    <div style={{ width: '100%', display: 'flex', justifyContent: 'space-between' }}>
                      <div>
                        <h3 style={{ margin: '0 0 5px 0', color: 'var(--chase-blue-dark)' }}>{userItem.first_name} {userItem.last_name}</h3>
                        <p style={{ margin: '0', fontSize: '0.9rem', color: 'var(--chase-gray-500)' }}>Email: {userItem.email} | Role: <strong>{userItem.role}</strong></p>
                        <p style={{ margin: '5px 0 0 0', fontSize: '0.85rem', color: 'var(--chase-gray-500)' }}>Registered: {new Date(userItem.created_at).toLocaleString()}</p>
                      </div>
                      <span className="chase-status-pill" style={{ background: '#fef3c7', color: '#92400e' }}>PENDING</span>
                    </div>
                    <div style={{ width: '100%', display: 'flex', gap: '10px', borderTop: '1px solid var(--chase-gray-100)', paddingTop: '15px' }}>
                      <button onClick={() => handleVerifyClick(userItem)} className="chase-button" style={{ fontSize: '0.85rem' }}>✓ Approve</button>
                      <button onClick={() => handleReject(userItem)} className="chase-button-outline" style={{ fontSize: '0.85rem', color: '#dc2626', borderColor: '#dc2626' }}>✕ Disapprove</button>
                      <Link to={`/admin/user/${userItem.id}`} className="chase-button-outline" style={{ fontSize: '0.85rem' }}>View Details</Link>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>

        {/* Audit Logs */}
        <div className="chase-section" style={{ marginTop: '40px' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '24px' }}>
            <h2 style={{ color: 'var(--chase-blue-dark)', margin: 0 }}>System Audit Logs (30-Day Retention)</h2>
            <div style={{ display: 'flex', gap: '10px' }}>
              <select value={auditFilter} onChange={(e) => setAuditFilter(e.target.value)} style={{ padding: '8px 16px', borderRadius: '8px', border: '1px solid var(--chase-gray-200)' }}>
                <option value="all">All Activities</option>
                <option value="USER_APPROVED">User Approvals</option>
                <option value="ADMIN_ACTION">Admin Actions</option>
              </select>
              <button onClick={handleExportAuditLogs} className="chase-button-outline" style={{ padding: '8px 16px' }}>Export CSV</button>
            </div>
          </div>
          <div className="chase-card" style={{ padding: 0, maxHeight: '500px', overflowY: 'auto' }}>
            <table style={{ width: '100%', borderCollapse: 'collapse' }}>
              <thead style={{ background: 'var(--chase-gray-50)', position: 'sticky', top: 0 }}>
                <tr>
                  <th style={{ padding: '12px 24px', textAlign: 'left', borderBottom: '2px solid var(--chase-gray-200)' }}>Timestamp</th>
                  <th style={{ padding: '12px 24px', textAlign: 'left', borderBottom: '2px solid var(--chase-gray-200)' }}>Action</th>
                  <th style={{ padding: '12px 24px', textAlign: 'left', borderBottom: '2px solid var(--chase-gray-200)' }}>User</th>
                  <th style={{ padding: '12px 24px', textAlign: 'left', borderBottom: '2px solid var(--chase-gray-200)' }}>Blockchain Hash</th>
                </tr>
              </thead>
              <tbody>
                {auditLogs
                  .filter(log => {
                    if (auditFilter === 'all') return true;
                    if (auditFilter === 'USER_APPROVED') return log.action === 'USER_APPROVED' || log.action === 'USER_REJECTED';
                    if (auditFilter === 'ADMIN_ACTION') return log.action === 'ADMIN_LOGOUT' || log.action === 'USER_APPROVED' || log.action === 'USER_REJECTED';
                    return log.action === auditFilter;
                  })
                  .slice(0, 50).map(log => (
                  <tr key={log.id} style={{ borderBottom: '1px solid var(--chase-gray-100)' }}>
                    <td style={{ padding: '12px 24px', fontSize: '0.85rem', color: 'var(--chase-gray-500)' }}>{new Date(log.timestamp).toLocaleString()}</td>
                    <td style={{ padding: '12px 24px', fontSize: '0.85rem', fontWeight: '600' }}>{log.action}</td>
                    <td style={{ padding: '12px 24px', fontSize: '0.85rem' }}>{log.user_email || log.user_username || 'System'}</td>
                    <td style={{ padding: '12px 24px', fontSize: '0.75rem', fontFamily: 'monospace', color: 'var(--chase-blue)' }}>{log.blockchain_hash ? log.blockchain_hash.substring(0, 16) + '...' : 'Pending'}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      </div>

      {/* Verification Modal */}
      {showVerificationModal && selectedUser && (
        <div style={{ position: 'fixed', top: 0, left: 0, right: 0, bottom: 0, background: 'rgba(0, 0, 0, 0.5)', display: 'flex', alignItems: 'center', justifyContent: 'center', zIndex: 1000 }}>
          <div className="chase-card" style={{ maxWidth: '500px', width: '90%', padding: '2rem' }}>
            <h2 style={{ marginBottom: '1.5rem', color: 'var(--chase-blue-dark)' }}>Verify User: {selectedUser.first_name} {selectedUser.last_name}</h2>
            <div style={{ marginBottom: '20px' }}>
              <label style={{ display: 'block', marginBottom: '8px', fontWeight: '600' }}>Verification Type *</label>
              <select value={verificationType} onChange={(e) => setVerificationType(e.target.value)} style={{ width: '100%', padding: '12px', border: '1px solid var(--chase-gray-200)', borderRadius: '8px' }}>
                <option value="">Select Verification Type</option>
                {verificationTypes.map(type => (<option key={type.value} value={type.value}>{type.label}</option>))}
              </select>
            </div>
            <div style={{ marginBottom: '20px' }}>
              <label style={{ display: 'block', marginBottom: '8px', fontWeight: '600' }}>Verification Number (8 Digits) *</label>
              <input type="text" value={verificationNumber} onChange={handleVerificationNumberChange} placeholder="Enter 8-digit number" maxLength={8} style={{ width: '100%', padding: '12px', border: '1px solid var(--chase-gray-200)', borderRadius: '8px', letterSpacing: '2px', fontSize: '1.1rem' }} />
            </div>
            <div style={{ display: 'flex', gap: '12px' }}>
              <button onClick={handleProceedToMfa} className="chase-button" style={{ flex: 1, padding: '1rem' }}>Proceed to MFA</button>
              <button onClick={() => setShowVerificationModal(false)} className="chase-button-outline" style={{ flex: 1, padding: '1rem' }}>Cancel</button>
            </div>
          </div>
        </div>
      )}

      {/* MFA Modal (TRD §4.2) */}
      {showMfaModal && (
        <div style={{ position: 'fixed', top: 0, left: 0, right: 0, bottom: 0, background: 'rgba(0, 0, 0, 0.5)', display: 'flex', alignItems: 'center', justifyContent: 'center', zIndex: 1001 }}>
          <div className="chase-card" style={{ maxWidth: '500px', width: '90%', padding: '2rem' }}>
            <h2 style={{ marginBottom: '1.5rem', color: 'var(--chase-blue-dark)' }}>Security Verification (MFA)</h2>
            <p style={{ marginBottom: '20px', color: 'var(--chase-gray-500)' }}>Scan the QR code with your authenticator app and enter your password to approve this user.</p>
            
            {/* Real QR Code */}
            <div style={{ marginBottom: '20px', textAlign: 'center', padding: '20px', background: 'white', borderRadius: '12px', border: '1px solid var(--chase-gray-200)', boxShadow: 'inset 0 2px 4px rgba(0,0,0,0.05)' }}>
              {qrCodeData ? (
                <QRCodeCanvas value={qrCodeData} size={180} level="H" />
              ) : (
                <div style={{ height: '180px', display: 'flex', alignItems: 'center', justifyContent: 'center', color: 'var(--chase-gray-400)' }}>
                    Loading QR Code...
                </div>
              )}
            </div>

            <div style={{ marginBottom: '20px' }}>
              <label style={{ display: 'block', marginBottom: '8px', fontWeight: '600', fontSize: '0.9rem' }}>6-Digit MFA Code *</label>
              <input type="text" value={otpCode} onChange={(e) => setOtpCode(e.target.value.replace(/\D/g, '').substring(0, 6))} placeholder="000000" style={{ width: '100%', padding: '12px', border: '1px solid var(--chase-gray-200)', borderRadius: '8px', letterSpacing: '4px', textAlign: 'center', fontSize: '1.25rem', fontWeight: 'bold' }} />
            </div>

            <div style={{ marginBottom: '20px' }}>
              <label style={{ display: 'block', marginBottom: '8px', fontWeight: '600', fontSize: '0.9rem' }}>Admin Password *</label>
              <input type="password" value={mfaPassword} onChange={(e) => setMfaPassword(e.target.value)} placeholder="Enter password to confirm" style={{ width: '100%', padding: '12px', border: '1px solid var(--chase-gray-200)', borderRadius: '8px' }} />
            </div>

            <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
              <button onClick={handleFinalApprove} className="chase-button" style={{ padding: '1rem' }}>Confirm & Approve</button>
              <div style={{ display: 'flex', gap: '12px' }}>
                <button onClick={handleResetMfa} className="chase-button-outline" style={{ flex: 1, padding: '0.75rem', fontSize: '0.85rem', color: 'var(--chase-gray-500)' }}>Reset MFA Setup</button>
                <button onClick={() => setShowMfaModal(false)} className="chase-button-outline" style={{ flex: 1, padding: '0.75rem' }}>Cancel</button>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default AdminDashboard;