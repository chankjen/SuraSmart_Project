import React, { useState, useEffect, useRef, useCallback } from 'react';

// =============================================================
//  KENYA COUNTY COORDINATE CENTRES (approx. on a 800x800 grid)
//  Derived from the standard Kenya county map layout.
// =============================================================
const COUNTY_CENTRES = {
  "Mombasa":       { x: 648, y: 630 },
  "Kwale":         { x: 600, y: 680 },
  "Kilifi":        { x: 635, y: 590 },
  "Tana River":    { x: 590, y: 520 },
  "Lamu":          { x: 700, y: 540 },
  "Taita Taveta":  { x: 530, y: 645 },
  "Garissa":       { x: 660, y: 390 },
  "Wajir":         { x: 700, y: 260 },
  "Mandera":       { x: 740, y: 170 },
  "Marsabit":      { x: 530, y: 200 },
  "Isiolo":        { x: 570, y: 320 },
  "Meru":          { x: 530, y: 360 },
  "Tharaka Nithi": { x: 505, y: 410 },
  "Embu":          { x: 475, y: 430 },
  "Kitui":         { x: 550, y: 470 },
  "Machakos":      { x: 460, y: 490 },
  "Makueni":       { x: 430, y: 540 },
  "Nyandarua":     { x: 380, y: 400 },
  "Nyeri":         { x: 410, y: 420 },
  "Kirinyaga":     { x: 440, y: 410 },
  "Murang'a":      { x: 420, y: 460 },
  "Kiambu":        { x: 390, y: 480 },
  "Turkana":       { x: 220, y: 200 },
  "West Pokot":    { x: 270, y: 285 },
  "Samburu":       { x: 400, y: 270 },
  "Trans Nzoia":   { x: 268, y: 340 },
  "Uasin Gishu":   { x: 280, y: 365 },
  "Elgeyo Marakwet":{ x: 300, y: 325 },
  "Nandi":         { x: 298, y: 393 },
  "Baringo":       { x: 330, y: 330 },
  "Laikipia":      { x: 380, y: 335 },
  "Nakuru":        { x: 332, y: 410 },
  "Narok":         { x: 300, y: 490 },
  "Kajiado":       { x: 380, y: 555 },
  "Kericho":       { x: 310, y: 440 },
  "Bomet":         { x: 295, y: 465 },
  "Kakamega":      { x: 258, y: 390 },
  "Vihiga":        { x: 255, y: 415 },
  "Bungoma":       { x: 240, y: 360 },
  "Busia":         { x: 228, y: 405 },
  "Siaya":         { x: 230, y: 430 },
  "Kisumu":        { x: 255, y: 445 },
  "Homa Bay":      { x: 255, y: 475 },
  "Migori":        { x: 255, y: 500 },
  "Kisii":         { x: 278, y: 480 },
  "Nyamira":       { x: 280, y: 458 },
  "Nairobi":       { x: 398, y: 508 },
};

// ------- Status colour palette -------
const STATUS_COLORS = {
  CLOSED:             { fill: '#22c55e', label: 'Closed',             ring: 'rgba(34,197,94,0.35)' },
  ESCALATED:          { fill: '#f59e0b', label: 'Escalated',          ring: 'rgba(245,158,11,0.35)' },
  PENDING_CLOSURE:    { fill: '#f97316', label: 'Pending Closure',    ring: 'rgba(249,115,22,0.35)' },
  UNDER_INVESTIGATION:{ fill: '#3b82f6', label: 'Under Investigation',ring: 'rgba(59,130,246,0.35)' },
  GOVERNMENT_REVIEW:  { fill: '#8b5cf6', label: 'Gov. Review',        ring: 'rgba(139,92,246,0.35)' },
  MATCH_FOUND:        { fill: '#06b6d4', label: 'Match Found',        ring: 'rgba(6,182,212,0.35)'  },
  ANALYZED:           { fill: '#0ea5e9', label: 'Analyzed',           ring: 'rgba(14,165,233,0.35)' },
  NO_MATCH:           { fill: '#64748b', label: 'No Match',           ring: 'rgba(100,116,139,0.35)'},
  RAISED:             { fill: '#ec4899', label: 'Raised',             ring: 'rgba(236,72,153,0.35)' },
  REPORTED:           { fill: '#ef4444', label: 'Reported',           ring: 'rgba(239,68,68,0.35)'  },
};

function getDominantStatus(countyData) {
  if (!countyData || countyData.total === 0) return null;
  const breakdown = countyData.statusBreakdown || {};
  const priority = [
    'ESCALATED','GOVERNMENT_REVIEW','MATCH_FOUND','UNDER_INVESTIGATION',
    'ANALYZED','RAISED','REPORTED','PENDING_CLOSURE','NO_MATCH','CLOSED',
  ];
  for (const s of priority) {
    if ((breakdown[s] || 0) > 0) return s;
  }
  return null;
}

function getColor(status) {
  return STATUS_COLORS[status] || { fill: '#94a3b8', label: status, ring: 'rgba(148,163,184,0.3)' };
}

// ------- Ripple CSS injected once -------
const RIPPLE_STYLE = `
@keyframes ripple {
  0%   { r: 8;  opacity: 0.8; }
  100% { r: 22; opacity: 0;   }
}
@keyframes ripple2 {
  0%   { r: 8;  opacity: 0.5; }
  100% { r: 28; opacity: 0;   }
}
.county-dot:hover { filter: brightness(1.2); cursor: pointer; }
`;

// ─────────────────────────────────────────────────────────────────────────────
const KenyaMapChart = ({ cases = [], countyDynamics = {} }) => {
  const [fullscreen, setFullscreen]           = useState(false);
  const [selectedCounty, setSelectedCounty]   = useState(null);
  const [tooltip, setTooltip]                 = useState(null);   // { x, y, county }
  const [filterStatus, setFilterStatus]       = useState('ALL');
  const [searchQuery, setSearchQuery]         = useState('');
  const [highlightedCounty, setHighlightedCounty] = useState(null);
  const [animFrame, setAnimFrame]             = useState(0);
  const svgRef                                = useRef(null);
  const rafRef                                = useRef(null);

  // Pulse animation ticker (drives ripple phase offset)
  useEffect(() => {
    let frame = 0;
    const tick = () => {
      frame = (frame + 1) % 120;
      setAnimFrame(frame);
      rafRef.current = requestAnimationFrame(tick);
    };
    rafRef.current = requestAnimationFrame(tick);
    return () => cancelAnimationFrame(rafRef.current);
  }, []);

  // Enrich countyDynamics with status breakdown
  const enrichedCounties = React.useMemo(() => {
    const out = {};
    cases.forEach(c => {
      const location = c.last_seen_location || '';
      const parts    = location.split(',').map(p => p.trim());
      let county     = parts.length > 1 ? parts[parts.length - 1] : parts[0] || 'Unknown';
      county         = county.replace(/\bcounty\b/i, '').trim();
      // Title case
      county = county.split(' ').map(w => w ? w.charAt(0).toUpperCase() + w.slice(1).toLowerCase() : '').join(' ');

      const status = (c.status || 'REPORTED').toUpperCase();
      if (!out[county]) out[county] = { total: 0, statusBreakdown: {}, residents: [] };
      out[county].total++;
      out[county].statusBreakdown[status] = (out[county].statusBreakdown[status] || 0) + 1;
      out[county].residents.push(c);
    });
    return out;
  }, [cases]);

  const handleCountyClick = useCallback((countyName) => {
    setSelectedCounty(prev => prev === countyName ? null : countyName);
    setTooltip(null);
  }, []);

  const visibleCounties = React.useMemo(() => {
    return Object.keys(COUNTY_CENTRES).filter(name => {
      const q = searchQuery.toLowerCase();
      if (q && !name.toLowerCase().includes(q)) return false;
      if (filterStatus !== 'ALL') {
        const dom = getDominantStatus(enrichedCounties[name]);
        if (dom !== filterStatus) return false;
      }
      return true;
    });
  }, [searchQuery, filterStatus, enrichedCounties]);

  const countyList = Object.keys(COUNTY_CENTRES).sort();

  // ── Render ──────────────────────────────────────────────────────────────────
  const mapContent = (
    <div style={{ position: 'relative', width: '100%', height: '100%' }}>
      {/* SVG Map */}
      <svg
        ref={svgRef}
        viewBox="0 0 800 800"
        style={{ width: '100%', height: '100%', display: 'block' }}
        aria-label="Interactive Kenya County Map"
      >
        <style>{RIPPLE_STYLE}</style>

        {/* Background */}
        <rect width="800" height="800" fill="#e0f2fe" rx="16" />

        {/* Kenya rough border silhouette (simplified path) */}
        <path
          d="M190,80 L290,60 L390,55 L480,70 L570,80 L640,110 L720,150 L760,220 L770,310
             L750,400 L720,460 L700,530 L680,590 L660,640 L630,680 L590,720 L550,745
             L510,755 L470,750 L440,720 L400,740 L360,750 L310,730 L280,700 L250,650
             L220,600 L200,540 L185,470 L175,390 L170,310 L175,230 L185,160 Z"
          fill="#f0fdf4"
          stroke="#94a3b8"
          strokeWidth="2"
          opacity="0.5"
        />

        {/* County dots + ripple rings */}
        {countyList.map(name => {
          const { x, y } = COUNTY_CENTRES[name];
          const data     = enrichedCounties[name];
          const domStat  = getDominantStatus(data);
          const color    = getColor(domStat);
          const hasData  = data && data.total > 0;
          const isVis    = visibleCounties.includes(name);
          const isSelec  = selectedCounty === name;
          const isHover  = highlightedCounty === name;
          const phase    = ((animFrame + (x + y)) % 120) / 120; // staggered
          const r1       = hasData ? 8 + phase * 14 : 0;
          const r2       = hasData ? 8 + ((phase + 0.3) % 1) * 20 : 0;
          const opacity1 = hasData ? 0.6 * (1 - phase) : 0;
          const opacity2 = hasData ? 0.3 * (1 - ((phase + 0.3) % 1)) : 0;

          return (
            <g
              key={name}
              style={{ opacity: isVis ? 1 : 0.15, transition: 'opacity 0.3s' }}
              onClick={() => handleCountyClick(name)}
              onMouseEnter={() => {
                setHighlightedCounty(name);
                setTooltip({ x, y, county: name });
              }}
              onMouseLeave={() => {
                setHighlightedCounty(null);
                setTooltip(null);
              }}
              className="county-dot"
              role="button"
              aria-label={`${name}: ${data?.total || 0} cases`}
            >
              {/* Ripple rings */}
              {hasData && (
                <>
                  <circle cx={x} cy={y} r={r1} fill={color.ring} stroke="none" />
                  <circle cx={x} cy={y} r={r2} fill={color.ring} stroke="none" />
                </>
              )}

              {/* Main dot */}
              <circle
                cx={x} cy={y}
                r={isSelec ? 11 : isHover ? 10 : hasData ? 8 : 5}
                fill={hasData ? color.fill : '#cbd5e1'}
                stroke={isSelec ? '#fff' : 'none'}
                strokeWidth={isSelec ? 2.5 : 0}
                style={{ transition: 'r 0.2s' }}
              />

              {/* Count badge */}
              {hasData && (isSelec || isHover) && (
                <g>
                  <rect x={x + 10} y={y - 18} width={32} height={16} rx={5} fill="#1e293b" opacity={0.85} />
                  <text x={x + 26} y={y - 6} textAnchor="middle" fill="white" fontSize="9" fontWeight="bold">
                    {data.total}
                  </text>
                </g>
              )}

              {/* County name label */}
              <text
                x={x} y={y + 20}
                textAnchor="middle"
                fontSize={isSelec || isHover ? 10 : 8}
                fontWeight={isSelec ? 'bold' : '600'}
                fill={isSelec ? '#1e293b' : '#334155'}
                style={{ pointerEvents: 'none', transition: 'font-size 0.2s' }}
              >
                {name}
              </text>
            </g>
          );
        })}

        {/* SVG Tooltip */}
        {tooltip && (() => {
          const { x, y, county } = tooltip;
          const d = enrichedCounties[county];
          const stat = getDominantStatus(d);
          const c    = getColor(stat);
          const tx   = Math.min(x + 15, 730);
          const ty   = Math.max(y - 50, 20);
          return (
            <g pointerEvents="none">
              <rect x={tx} y={ty} width={130} height={50} rx={8} fill="#1e293b" opacity={0.95} />
              <text x={tx + 65} y={ty + 16} textAnchor="middle" fill="white" fontSize="10" fontWeight="bold">{county}</text>
              <circle cx={tx + 14} cy={ty + 32} r={5} fill={c.fill} />
              <text x={tx + 24} y={ty + 36} fill="#e2e8f0" fontSize="9">{stat ? c.label : 'No data'}</text>
              <text x={tx + 115} y={ty + 36} textAnchor="end" fill="#fbbf24" fontSize="9" fontWeight="bold">
                {d?.total || 0} cases
              </text>
            </g>
          );
        })()}
      </svg>
    </div>
  );

  // ── County detail panel ────────────────────────────────────────────────────
  const detailPanel = selectedCounty && (() => {
    const d    = enrichedCounties[selectedCounty] || { total: 0, statusBreakdown: {}, residents: [] };
    const dom  = getDominantStatus(d);
    const col  = getColor(dom);
    return (
      <div style={{
        background: '#1e293b',
        color: 'white',
        borderRadius: '12px',
        padding: '20px',
        marginTop: '12px',
        border: `2px solid ${col.fill}`,
        animation: 'fadeIn 0.3s ease',
      }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '12px' }}>
          <h3 style={{ margin: 0, color: col.fill, fontSize: '1.1rem' }}>{selectedCounty} County</h3>
          <button
            onClick={() => setSelectedCounty(null)}
            style={{ background: 'none', border: 'none', color: '#94a3b8', cursor: 'pointer', fontSize: '1.2rem' }}
          >✕</button>
        </div>
        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '8px', marginBottom: '14px' }}>
          <div style={{ background: 'rgba(255,255,255,0.08)', borderRadius: '8px', padding: '10px', textAlign: 'center' }}>
            <div style={{ fontSize: '1.8rem', fontWeight: '800', color: '#fbbf24' }}>{d.total}</div>
            <div style={{ fontSize: '0.7rem', color: '#94a3b8', textTransform: 'uppercase' }}>Total Cases</div>
          </div>
          <div style={{ background: 'rgba(255,255,255,0.08)', borderRadius: '8px', padding: '10px', textAlign: 'center' }}>
            <div style={{ fontSize: '1.2rem', fontWeight: '800', color: col.fill }}>{dom ? col.label : 'None'}</div>
            <div style={{ fontSize: '0.7rem', color: '#94a3b8', textTransform: 'uppercase' }}>Primary Status</div>
          </div>
        </div>
        <div style={{ display: 'grid', gap: '6px' }}>
          {Object.entries(d.statusBreakdown || {}).sort((a, b) => b[1] - a[1]).map(([st, cnt]) => {
            const sc = getColor(st);
            const pct = d.total > 0 ? (cnt / d.total) * 100 : 0;
            return (
              <div key={st} style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                <div style={{ width: '10px', height: '10px', borderRadius: '50%', background: sc.fill, flexShrink: 0 }} />
                <div style={{ flex: 1, fontSize: '0.78rem', color: '#cbd5e1' }}>{sc.label}</div>
                <div style={{ width: '80px', height: '6px', background: 'rgba(255,255,255,0.1)', borderRadius: '3px', overflow: 'hidden' }}>
                  <div style={{ width: `${pct}%`, height: '100%', background: sc.fill, borderRadius: '3px' }} />
                </div>
                <div style={{ fontSize: '0.78rem', fontWeight: '700', color: 'white', minWidth: '28px', textAlign: 'right' }}>{cnt}</div>
              </div>
            );
          })}
        </div>
      </div>
    );
  })();

  // ── Legend ─────────────────────────────────────────────────────────────────
  const legend = (
    <div style={{ display: 'flex', flexWrap: 'wrap', gap: '8px', marginBottom: '12px' }}>
      {Object.entries(STATUS_COLORS).map(([key, val]) => (
        <div
          key={key}
          onClick={() => setFilterStatus(prev => prev === key ? 'ALL' : key)}
          style={{
            display: 'flex', alignItems: 'center', gap: '5px',
            cursor: 'pointer',
            padding: '3px 8px',
            borderRadius: '12px',
            background: filterStatus === key ? val.fill : 'rgba(255,255,255,0.08)',
            border: `1.5px solid ${val.fill}`,
            fontSize: '0.72rem',
            fontWeight: '600',
            color: filterStatus === key ? '#fff' : val.fill,
            transition: 'all 0.2s',
          }}
        >
          <span style={{ width: '8px', height: '8px', borderRadius: '50%', background: val.fill, display: 'inline-block' }} />
          {val.label}
        </div>
      ))}
      {filterStatus !== 'ALL' && (
        <div
          onClick={() => setFilterStatus('ALL')}
          style={{ cursor: 'pointer', padding: '3px 8px', borderRadius: '12px', border: '1.5px solid #94a3b8', color: '#94a3b8', fontSize: '0.72rem' }}
        >
          ✕ Clear Filter
        </div>
      )}
    </div>
  );

  // ── Controls ───────────────────────────────────────────────────────────────
  const controls = (
    <div style={{ display: 'flex', gap: '10px', marginBottom: '14px', flexWrap: 'wrap', alignItems: 'center' }}>
      <input
        value={searchQuery}
        onChange={e => setSearchQuery(e.target.value)}
        placeholder="🔍 Search county..."
        style={{
          flex: 1,
          minWidth: '160px',
          padding: '7px 12px',
          borderRadius: '8px',
          border: '1.5px solid #334155',
          background: 'rgba(255,255,255,0.07)',
          color: '#fff',
          fontSize: '0.85rem',
          outline: 'none',
        }}
      />
      <div style={{ fontSize: '0.8rem', color: '#94a3b8' }}>
        <strong style={{ color: '#fbbf24' }}>{visibleCounties.length}</strong> / 47 counties
      </div>
      <button
        onClick={() => setFullscreen(true)}
        title="Fullscreen Map"
        style={{
          background: 'linear-gradient(135deg,#3b82f6,#6366f1)',
          color: 'white',
          border: 'none',
          borderRadius: '8px',
          padding: '7px 14px',
          cursor: 'pointer',
          fontWeight: '700',
          fontSize: '0.82rem',
          display: 'flex',
          alignItems: 'center',
          gap: '5px',
        }}
      >
        ⛶ Zoom View
      </button>
    </div>
  );

  // ── Stats summary bar ──────────────────────────────────────────────────────
  const totalCases   = cases.length;
  const closedCases  = cases.filter(c => c.status.toUpperCase() === 'CLOSED').length;
  const escalated    = cases.filter(c => c.status.toUpperCase() === 'ESCALATED').length;
  const countiesWithData = Object.keys(enrichedCounties).length;

  const summaryBar = (
    <div style={{
      display: 'grid', gridTemplateColumns: 'repeat(4,1fr)', gap: '10px', marginBottom: '14px'
    }}>
      {[
        { label: 'Total Cases',    val: totalCases,         col: '#fbbf24' },
        { label: 'Closed',         val: closedCases,        col: '#22c55e' },
        { label: 'Escalated',      val: escalated,          col: '#f59e0b' },
        { label: 'Counties Active',val: countiesWithData,   col: '#3b82f6' },
      ].map(item => (
        <div key={item.label} style={{
          background: 'rgba(255,255,255,0.06)',
          borderRadius: '8px',
          padding: '10px',
          textAlign: 'center',
          border: `1.5px solid ${item.col}22`,
        }}>
          <div style={{ fontSize: '1.4rem', fontWeight: '800', color: item.col }}>{item.val}</div>
          <div style={{ fontSize: '0.68rem', color: '#94a3b8', textTransform: 'uppercase', letterSpacing: '0.5px' }}>{item.label}</div>
        </div>
      ))}
    </div>
  );

  // ── Wrapper ────────────────────────────────────────────────────────────────
  const containerStyle = {
    background: 'linear-gradient(135deg, #0f172a 0%, #1e3a5f 100%)',
    paddingBottom: '4px',
    borderRadius: '16px',
    padding: '20px',
    boxShadow: '0 20px 40px rgba(0,0,0,0.2)',
  };

  const fullscreenOverlay = fullscreen ? (
    <div
      style={{
        position: 'fixed', inset: 0, zIndex: 9999,
        background: 'linear-gradient(135deg,#0f172a 0%,#1e3a5f 100%)',
        display: 'flex', flexDirection: 'column',
        padding: '20px',
      }}
    >
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '14px' }}>
        <h2 style={{ color: '#fbbf24', margin: 0, fontSize: '1.3rem' }}>🗺️ Kenya Missing Persons Map — Full View</h2>
        <button
          onClick={() => setFullscreen(false)}
          style={{
            background: '#ef4444', color: 'white', border: 'none',
            borderRadius: '8px', padding: '8px 16px',
            cursor: 'pointer', fontWeight: '700', fontSize: '0.9rem',
            display: 'flex', alignItems: 'center', gap: '6px',
          }}
        >
          ✕ Close
        </button>
      </div>
      {summaryBar}
      {legend}
      {controls}
      <div style={{ flex: 1, overflow: 'hidden', borderRadius: '12px', border: '1px solid #334155', display: 'flex', gap: '16px' }}>
        <div style={{ flex: 1 }}>{mapContent}</div>
        {selectedCounty && (
          <div style={{ width: '280px', overflowY: 'auto', paddingRight: '4px' }}>
            {detailPanel}
          </div>
        )}
      </div>
    </div>
  ) : null;

  return (
    <>
      {fullscreenOverlay}
      <div style={containerStyle}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '14px' }}>
          <h3 style={{ color: '#fbbf24', margin: 0, fontSize: '1.1rem', fontWeight: '800', letterSpacing: '0.5px' }}>
            🗺️ Kenya County Case Heatmap
          </h3>
          <span style={{ fontSize: '0.75rem', color: '#94a3b8' }}>
            Click a dot to inspect · Hover for tooltip
          </span>
        </div>
        {summaryBar}
        {legend}
        {controls}
        <div style={{ display: 'grid', gridTemplateColumns: selectedCounty ? '1fr 280px' : '1fr', gap: '16px' }}>
          <div style={{ borderRadius: '12px', overflow: 'hidden', border: '1px solid #334155', minHeight: '440px' }}>
            {mapContent}
          </div>
          {selectedCounty && (
            <div>{detailPanel}</div>
          )}
        </div>
      </div>

      <style>{`
        @keyframes fadeIn { from { opacity:0; transform:translateY(8px); } to { opacity:1; transform:translateY(0); } }
      `}</style>
    </>
  );
};

export default KenyaMapChart;
