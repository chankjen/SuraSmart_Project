import React, { useState, useEffect, useCallback, useMemo } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import api from '../services/api';
import { KENYA_LOCATIONS } from '../constants/kenyaLocations';
import '../styles/Analytics.css';

const AnalyticsDashboard = () => {
    const { user } = useAuth();
    const navigate = useNavigate();
    const [cases, setCases] = useState([]);
    const [loading, setLoading] = useState(true);
    const [stats, setStats] = useState({
        total: 0,
        resolved: 0,
        unattended: 0,
        escalated: 0,
        successRate: 0,
        statusDistribution: {},
        genderDistribution: {},
        topCounties: [],
        countyDynamics: {} // County -> { total, subcounties: { sub -> count } }
    });

    const [selectedCounty, setSelectedCounty] = useState('Nairobi');

    const calculateStats = useCallback((data) => {
        const total = data.length;
        const resolved = data.filter(c => ['CLOSED', 'found'].includes(c.status.toLowerCase())).length;
        const escalated = data.filter(c => c.status.toUpperCase() === 'ESCALATED').length;
        const unattended = data.filter(c => ['RAISED', 'REPORTED'].includes(c.status.toUpperCase())).length;
        
        // Distributions
        const statusDistribution = data.reduce((acc, c) => {
            acc[c.status] = (acc[c.status] || 0) + 1;
            return acc;
        }, {});

        const genderDistribution = data.reduce((acc, c) => {
            const g = c.gender ? c.gender.charAt(0).toUpperCase() + c.gender.slice(1).toLowerCase() : 'Unknown';
            acc[g] = (acc[g] || 0) + 1;
            return acc;
        }, {});

        // County Logic
        const countyMap = {};
        data.forEach(c => {
            const location = c.last_seen_location || '';
            const parts = location.split(', ');
            const county = parts.length > 1 ? parts[parts.length - 1].trim() : (parts[0] || 'Unknown');
            const subcounty = parts.length > 1 ? parts[0].trim() : 'Unspecified';
            
            if (!countyMap[county]) {
                countyMap[county] = { total: 0, subcounties: {} };
            }
            countyMap[county].total += 1;
            countyMap[county].subcounties[subcounty] = (countyMap[county].subcounties[subcounty] || 0) + 1;
        });

        const topCounties = Object.entries(countyMap)
            .filter(([name]) => name !== 'Unknown')
            .sort((a, b) => b[1].total - a[1].total)
            .slice(0, 5)
            .map(([name, data]) => ({ name, count: data.total }));

        const successRate = total > 0 ? (resolved / total) * 100 : 0;

        setStats({
            total,
            resolved,
            unattended,
            escalated,
            successRate,
            statusDistribution,
            genderDistribution,
            topCounties,
            countyDynamics: countyMap
        });
    }, []);

    useEffect(() => {
        const fetchAnalytics = async () => {
            try {
                const response = await api.getMissingPersons();
                const results = response.data.results || response.data || [];
                setCases(results);
                calculateStats(results);
            } catch (error) {
                console.error('Error fetching analytics:', error);
            } finally {
                setLoading(false);
            }
        };

        fetchAnalytics();
    }, [calculateStats]);

    const regionalData = useMemo(() => {
        return stats.countyDynamics[selectedCounty] || { total: 0, subcounties: {} };
    }, [stats.countyDynamics, selectedCounty]);

    if (loading) {
        return <div className="chase-body"><div className="chase-container">Analyzing Registry Data...</div></div>;
    }

    return (
        <div className="analytics-page">
            <header className="chase-header no-print">
                <div className="chase-logo">Sura<span>Smart</span></div>
                <div style={{ display: 'flex', alignItems: 'center', gap: '20px' }}>
                    <span style={{ color: 'white' }}>Analyst {user?.first_name}</span>
                    <Link to="/government-dashboard" className="chase-button-outline" style={{ color: 'white', borderColor: 'white', textDecoration: 'none', padding: '0.5rem 1rem' }}>Dashboard</Link>
                </div>
            </header>

            <div className="chase-container">
                <h1 className="analytics-title">System Analytics Dashboard</h1>
                <p className="analytics-subtitle">Real-time monitoring of missing person registry performance and status distribution.</p>

                {/* Hero Stats */}
                <div className="stats-grid">
                    <div className="stat-card">
                        <div className="stat-label">Total Reported</div>
                        <div className="stat-value">{stats.total}</div>
                        <div className="stat-trend trend-neutral">System Wide</div>
                    </div>
                    <div className="stat-card">
                        <div className="stat-label">Resolution Rate</div>
                        <div className="stat-value">{stats.successRate.toFixed(1)}%</div>
                        <div className="stat-trend trend-up">↑ Improved</div>
                    </div>
                    <div className="stat-card">
                        <div className="stat-label">National Escalations</div>
                        <div className="stat-value">{stats.escalated}</div>
                        <div className="stat-trend trend-warn">High Priority</div>
                    </div>
                    <div className="stat-card" style={{ borderTop: '4px solid #ef4444' }}>
                        <div className="stat-label">Unattended <span style={{ color: '#F014B1' }}>cases</span></div>
                        <div className="stat-value" style={{ color: '#ef4444' }}>{stats.unattended}</div>
                        <div className="stat-trend trend-warn">Requires Action</div>
                    </div>
                </div>

                <div className="charts-section">
                    <div className="chart-container">
                        <h3>Status & Demographics</h3>
                        
                        <div className="distribution-split">
                            <div className="dist-col">
                                <h4>Gender Distribution</h4>
                                <div className="mini-bar-chart">
                                    {Object.entries(stats.genderDistribution).map(([gender, count]) => (
                                        <div key={gender} className="mini-bar-item">
                                            <div className="mini-bar-info">
                                                <span>{gender}</span>
                                                <span>{count}</span>
                                            </div>
                                            <div className="mini-bar-track">
                                                <div 
                                                    className="mini-bar-fill" 
                                                    style={{ 
                                                        width: `${(count / stats.total) * 100}%`,
                                                        background: gender === 'Male' ? '#3b82f6' : gender === 'Female' ? '#ec4899' : '#94a3b8'
                                                    }}
                                                ></div>
                                            </div>
                                        </div>
                                    ))}
                                </div>
                            </div>
                            
                            <div className="dist-col">
                                <h4>Top 5 Reporting Counties</h4>
                                <div className="mini-bar-chart">
                                    {stats.topCounties.map(({name, count}) => (
                                        <div key={name} className="mini-bar-item">
                                            <div className="mini-bar-info">
                                                <span>{name}</span>
                                                <span>{count}</span>
                                            </div>
                                            <div className="mini-bar-track">
                                                <div 
                                                    className="mini-bar-fill" 
                                                    style={{ width: `${(count / stats.topCounties[0].count) * 100}%` }}
                                                ></div>
                                            </div>
                                        </div>
                                    ))}
                                </div>
                            </div>
                        </div>

                        <div style={{ marginTop: '30px', borderTop: '1px solid #f1f5f9', paddingTop: '20px' }}>
                            <h4 style={{ color: '#1e3a8a' }}>Registry Status Breakdown</h4>

                            <div className="status-tags">
                                {Object.entries(stats.statusDistribution).map(([status, count]) => (
                                    <div key={status} className="status-tag-item">
                                        <span className="status-tag-name">{status}</span>
                                        <span className="status-tag-count">{count}</span>
                                    </div>
                                ))}
                            </div>
                        </div>
                    </div>

                    <div className="chart-container">
                        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '20px' }}>
                            <h3 style={{ margin: 0 }}>Regional Oversight</h3>
                            <select 
                                value={selectedCounty} 
                                onChange={(e) => setSelectedCounty(e.target.value)}
                                className="chase-select-sm"
                                style={{ width: 'auto', padding: '4px 8px' }}
                            >
                                {Object.keys(KENYA_LOCATIONS).map(c => (
                                    <option key={c} value={c}>{c}</option>
                                ))}
                            </select>
                        </div>

                        <div className="regional-impact">
                            <div className="regional-total">
                                <strong>{regionalData.total}</strong>
                                <span>Total <span style={{ color: '#F014B1' }}>cases</span> in {selectedCounty}</span>
                            </div>
                            
                            <div className="subcounty-list">
                                {Object.entries(regionalData.subcounties).length > 0 ? (
                                    Object.entries(regionalData.subcounties).map(([sub, count]) => (
                                        <div key={sub} className="subcounty-item">
                                            <span className="sub-name">{sub}</span>
                                            <div className="sub-viz">
                                                <div className="mini-bar-track" style={{ flexGrow: 1 }}>
                                                    <div 
                                                        className="mini-bar-fill" 
                                                        style={{ width: `${(count / regionalData.total) * 100}%` }}
                                                    ></div>
                                                </div>
                                                <span className="sub-count">{count}</span>
                                            </div>

                                        </div>
                                    ))
                                ) : (
                                    <div className="no-data-notice">No cases recorded for this county.</div>
                                )}
                            </div>
                        </div>
                    </div>
                </div>

                <div className="insights-card">
                    <h3>Strategic insights</h3>
                    <ul className="insights-list">
                        <li><strong>Gender Gap:</strong> {stats.genderDistribution['Male'] > stats.genderDistribution['Female'] ? 'Male' : 'Female'} <span style={{ color: '#F014B1' }}>cases</span> are currently reported at a higher frequency.</li>
                        <li><strong>Hotspot Alert:</strong> {stats.topCounties[0]?.name || 'N/A'} remains the highest reporting area in the country.</li>
                        <li><strong>Registry Health:</strong> {stats.unattended} unattended <span style={{ color: '#F014B1' }}>cases</span> require immediate police follow-up to maintain resolution targets.</li>
                        <li><strong>Efficiency:</strong> National resolution rate is at {stats.successRate.toFixed(1)}%, targeting 85% by year-end.</li>
                    </ul>

                </div>
            </div>
        </div>
    );
};

export default AnalyticsDashboard;

