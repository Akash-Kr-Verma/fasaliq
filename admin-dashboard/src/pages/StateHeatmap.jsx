import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { getStateHeatmap } from '../api/adminService';
import { COLORS, DIVISIONS } from '../utils/theme';

const RISK_CONFIG = {
  low:      { label: 'Low Risk',      bg: '#EAF3DE', border: '#B5D98A', text: '#3B6D11', dot: '#3B6D11' },
  medium:   { label: 'Moderate',      bg: '#FFF8E1', border: '#F5D9A8', text: '#854F0B', dot: '#F5A623' },
  high:     { label: 'High Risk',     bg: '#FAEEDA', border: '#F0B97E', text: '#854F0B', dot: '#E07A00' },
  critical: { label: 'Critical',      bg: '#FAECE7', border: '#F5B8B8', text: '#993C1D', dot: '#D9534F' },
};

export default function StateHeatmap() {
  const [divisions, setDivisions] = useState([]);
  const [loading, setLoading] = useState(true);
  const navigate = useNavigate();

  useEffect(() => {
    getStateHeatmap()
      .then(r => { setDivisions(r.data.divisions || []); setLoading(false); })
      .catch(() => setLoading(false));
  }, []);

  const totalFarmers = divisions.reduce((a, d) => a + d.total_farmers, 0);
  const totalAlerts  = divisions.reduce((a, d) => a + d.surplus_alerts, 0);
  const criticalDivs = divisions.filter(d => d.risk_level === 'critical' || d.risk_level === 'high').length;

  return (
    <div>
      {/* Header */}
      <div style={{ marginBottom: 28 }}>
        <h2 style={{ color: COLORS.dark, marginBottom: 6 }}>Maharashtra State Heatmap</h2>
        <p style={{ color: COLORS.gray, margin: 0 }}>
          Division-level aggregated view — 6 revenue divisions, 36 districts. Click any division card to drill into its districts.
        </p>
      </div>

      {/* State-wide KPIs */}
      <div style={{ display: 'flex', gap: 16, flexWrap: 'wrap', marginBottom: 32 }}>
        {[
          { label: 'Total Farmers', value: totalFarmers, icon: '👨‍🌾', color: COLORS.primary },
          { label: 'Surplus Alerts', value: totalAlerts, icon: '⚠️', color: COLORS.amber },
          { label: 'High-Risk Divisions', value: criticalDivs, icon: '🔴', color: COLORS.coral },
          { label: 'Revenue Divisions', value: 6, icon: '🗂️', color: COLORS.secondary },
        ].map(({ label, value, icon, color }) => (
          <div key={label} style={{
            flex: 1, minWidth: 160,
            background: COLORS.white, border: '1px solid #E5E3DC',
            borderTop: `4px solid ${color}`, borderRadius: 12,
            padding: '18px 22px',
          }}>
            <div style={{ fontSize: 11, color: COLORS.gray, textTransform: 'uppercase', letterSpacing: '0.06em', marginBottom: 6 }}>
              {label}
            </div>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
              <span style={{ fontSize: 30, fontWeight: 700, color: COLORS.dark }}>{loading ? '…' : value}</span>
              <span style={{ fontSize: 26 }}>{icon}</span>
            </div>
          </div>
        ))}
      </div>

      {/* Division Cards Grid */}
      {loading ? (
        <p style={{ color: COLORS.gray }}>Loading division data…</p>
      ) : (
        <div style={{
          display: 'grid',
          gridTemplateColumns: 'repeat(auto-fill, minmax(340px, 1fr))',
          gap: 20
        }}>
          {divisions.map((div) => {
            const risk    = RISK_CONFIG[div.risk_level] || RISK_CONFIG.low;
            const divTheme = DIVISIONS[div.division];
            const divColor = divTheme?.color || COLORS.primary;

            return (
              <div
                key={div.division}
                style={{
                  background: COLORS.white,
                  border: `1px solid #E5E3DC`,
                  borderTop: `5px solid ${divColor}`,
                  borderRadius: 14,
                  padding: 22,
                  cursor: 'pointer',
                  transition: 'box-shadow 0.2s, transform 0.15s',
                }}
                onMouseEnter={e => {
                  e.currentTarget.style.boxShadow = `0 6px 24px ${divColor}30`;
                  e.currentTarget.style.transform = 'translateY(-2px)';
                }}
                onMouseLeave={e => {
                  e.currentTarget.style.boxShadow = 'none';
                  e.currentTarget.style.transform = 'translateY(0)';
                }}
              >
                {/* Division header */}
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: 16 }}>
                  <div>
                    <div style={{ fontSize: 18, fontWeight: 700, color: COLORS.dark }}>{div.division} Division</div>
                    <div style={{ fontSize: 12, color: COLORS.gray, marginTop: 2 }}>
                      {div.districts.length} districts
                    </div>
                  </div>
                  <span style={{
                    background: risk.bg,
                    color: risk.text,
                    border: `1px solid ${risk.border}`,
                    fontSize: 11, fontWeight: 700,
                    padding: '4px 10px', borderRadius: 20,
                    textTransform: 'uppercase', letterSpacing: '0.05em'
                  }}>
                    {risk.label}
                  </span>
                </div>

                {/* Metrics Grid */}
                <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 12, marginBottom: 16 }}>
                  {[
                    { label: 'Farmers', value: div.total_farmers, icon: '👨‍🌾' },
                    { label: 'Buyers', value: div.total_buyers, icon: '🏪' },
                    { label: 'Surplus Alerts', value: div.surplus_alerts, icon: '⚠️', danger: div.surplus_alerts > 0 },
                    { label: 'Demand Entries', value: div.demand_entries, icon: '📦' },
                  ].map(({ label, value, icon, danger }) => (
                    <div key={label} style={{
                      background: danger ? COLORS.warning : COLORS.lightGray,
                      borderRadius: 8, padding: '10px 12px'
                    }}>
                      <div style={{ fontSize: 10, color: danger ? COLORS.amber : COLORS.gray, marginBottom: 4, textTransform: 'uppercase' }}>
                        {icon} {label}
                      </div>
                      <div style={{ fontSize: 20, fontWeight: 700, color: danger ? COLORS.amber : COLORS.dark }}>
                        {value}
                      </div>
                    </div>
                  ))}
                </div>

                {/* Top Crop */}
                <div style={{
                  background: COLORS.lightGray, borderRadius: 8, padding: '10px 14px',
                  display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: 14
                }}>
                  <span style={{ fontSize: 12, color: COLORS.gray }}>🌾 Top Active Crop</span>
                  <span style={{ fontSize: 14, fontWeight: 600, color: COLORS.dark }}>
                    {div.top_crop || 'No data yet'}
                  </span>
                </div>

                {/* District Pills */}
                <div style={{ display: 'flex', flexWrap: 'wrap', gap: 6 }}>
                  {div.districts.map(d => (
                    <span
                      key={d}
                      onClick={(e) => {
                        e.stopPropagation();
                        navigate('/district', { state: { selectedDistrict: d } });
                      }}
                      style={{
                        fontSize: 11, padding: '3px 8px',
                        borderRadius: 12,
                        background: '#fff',
                        border: `1px solid ${divColor}40`,
                        color: divColor,
                        cursor: 'pointer',
                        transition: 'all 0.15s',
                      }}
                      onMouseEnter={e => { e.currentTarget.style.background = divColor; e.currentTarget.style.color = '#fff'; }}
                      onMouseLeave={e => { e.currentTarget.style.background = '#fff'; e.currentTarget.style.color = divColor; }}
                    >
                      {d}
                    </span>
                  ))}
                </div>
              </div>
            );
          })}
        </div>
      )}

      {/* Risk Legend */}
      <div style={{ marginTop: 32, padding: '16px 20px', background: COLORS.white, borderRadius: 12, border: '1px solid #E5E3DC', display: 'flex', gap: 24, flexWrap: 'wrap', alignItems: 'center' }}>
        <span style={{ fontSize: 12, color: COLORS.gray, fontWeight: 600 }}>RISK LEGEND:</span>
        {Object.entries(RISK_CONFIG).map(([k, v]) => (
          <div key={k} style={{ display: 'flex', alignItems: 'center', gap: 6, fontSize: 12 }}>
            <span style={{ width: 10, height: 10, borderRadius: '50%', background: v.dot, display: 'inline-block' }} />
            <span style={{ color: v.text }}>{v.label}</span>
            {k === 'low' && <span style={{ color: COLORS.gray }}>— 0 alerts</span>}
            {k === 'medium' && <span style={{ color: COLORS.gray }}>— 1 alert</span>}
            {k === 'high' && <span style={{ color: COLORS.gray }}>— 2-4 alerts</span>}
            {k === 'critical' && <span style={{ color: COLORS.gray }}>— 5+ alerts</span>}
          </div>
        ))}
      </div>
    </div>
  );
}
