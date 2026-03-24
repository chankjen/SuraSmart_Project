import React, { useState, useEffect, useCallback, useMemo } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import api from '../services/api';
import { KENYA_LOCATIONS } from '../constants/kenyaLocations';
import KenyaMapChart from '../components/KenyaMapChart';
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
            const parts = location.split(',').map(p => p.trim());
            let county = parts.length > 1 ? parts[parts.length - 1] : (parts[0] || 'Unknown');
            let subcounty = parts.length > 1 ? parts[0] : 'Unspecified';
            
            // Normalize county name
            county = county.replace(/\bcounty\b/i, '').trim();

            const ALIASES = {
                'membley': { c: 'Kiambu', s: 'Ruiru' },
                'kosovo': { c: 'Kiambu', s: 'Juja' }
            };

            const aliasMatch = ALIASES[county.toLowerCase()] || ALIASES[subcounty.toLowerCase()] || ALIASES[location.toLowerCase()];
            
            if (aliasMatch) {
                county = aliasMatch.c;
                subcounty = aliasMatch.s;
            } else {
                let foundAsSubcounty = false;
                for (const [cName, subList] of Object.entries(KENYA_LOCATIONS)) {
                    const matchedSub = subList.find(s => s.toLowerCase() === county.toLowerCase());
                    if (matchedSub) {
                        subcounty = matchedSub;
                        county = cName;
                        foundAsSubcounty = true;
                        break;
                    }
                }

                if (!foundAsSubcounty) {
                    const matchedCounty = Object.keys(KENYA_LOCATIONS).find(k => k.toLowerCase() === county.toLowerCase());
                    if (matchedCounty) {
                        county = matchedCounty;
                    } else {
                        county = county.split(' ').map(w => w ? w.charAt(0).toUpperCase() + w.slice(1).toLowerCase() : '').join(' ');
                    }
                }
            }

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
                            <div className="regional-total" style={{marginBottom: '20px'}}>
                                <strong>{regionalData.total}</strong>
                                <span>Total <span style={{ color: '#F014B1' }}>cases</span> in {selectedCounty}</span>
                            </div>
                            
                            {Object.entries(regionalData.subcounties).length > 0 ? (() => {
                                const pieColors = ['#F014B1', '#3b82f6', '#10b981', '#f59e0b', '#8b5cf6', '#ef4444', '#06b6d4', '#84cc16', '#a855f7', '#fb923c'];
                                let currentAngle = 0;
                                const pieChartSlices = Object.entries(regionalData.subcounties).map(([sub, count], i) => {
                                    const percentage = (count / regionalData.total) * 100;
                                    const startAngle = currentAngle;
                                    const endAngle = currentAngle + percentage;
                                    currentAngle = endAngle;
                                    return `${pieColors[i % pieColors.length]} ${startAngle}% ${endAngle}%`;
                                }).join(', ');
                                
                                return (
                                    <div style={{ display: 'flex', gap: '30px', alignItems: 'center', flexWrap: 'wrap' }}>
                                        <div style={{
                                            width: '150px', 
                                            height: '150px', 
                                            borderRadius: '50%', 
                                            background: `conic-gradient(${pieChartSlices})`,
                                            flexShrink: 0,
                                            boxShadow: '0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06)'
                                        }}></div>
                                        <div className="subcounty-list" style={{ flexGrow: 1, minWidth: '200px' }}>
                                            {Object.entries(regionalData.subcounties).map(([sub, count], i) => (
                                                <div key={sub} className="subcounty-item" style={{display: 'flex', justifyContent: 'space-between', marginBottom: '10px', padding: '5px 0', borderBottom: '1px solid #f1f5f9'}}>
                                                    <div style={{display: 'flex', alignItems: 'center', gap: '10px'}}>
                                                        <div style={{width: '14px', height: '14px', backgroundColor: pieColors[i % pieColors.length], borderRadius: '4px'}}></div>
                                                        <span className="sub-name" style={{fontWeight: '500', color: '#334155'}}>{sub}</span>
                                                    </div>
                                                    <span className="sub-count" style={{fontWeight: 'bold', color: '#0f172a'}}>
                                                        {count} <span style={{fontSize: '0.85em', color: '#64748b', fontWeight: 'normal'}}>({Math.round((count/regionalData.total)*100)}%)</span>
                                                    </span>
                                                </div>
                                            ))}
                                        </div>
                                    </div>
                                );
                            })() : (
                                <div className="no-data-notice">No cases recorded for this county.</div>
                            )}
                        </div>
                    </div>
                </div>

                {/* Kenya Interactive Map */}
                <div style={{ margin: '40px 0' }}>
                    <KenyaMapChart cases={cases} countyDynamics={stats.countyDynamics} />
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

