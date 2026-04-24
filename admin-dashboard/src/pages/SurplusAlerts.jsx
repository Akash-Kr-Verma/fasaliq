import React, { useEffect, useState } from 'react';
import { getSurplusAlerts } from '../api/adminService';
import { COLORS, DISTRICTS } from '../utils/theme';

const SEVERITY_COLORS = {
  critical: { bg: '#FCEBEB', color: '#A32D2D', border: '#F5B8B8' },
  high: { bg: '#FAEEDA', color: '#854F0B', border: '#F5D9A8' },
  medium: { bg: '#E6F1FB', color: '#185FA5', border: '#B8D4F5' },
};

export default function SurplusAlerts() {
  const [alerts, setAlerts] = useState([]);
  const [district, setDistrict] = useState('');
  const [loading, setLoading] = useState(true);

  useEffect(() => { load(); }, []);

  const load = () => {
    setLoading(true);
    getSurplusAlerts(district)
      .then(r => { setAlerts(r.data.alerts || []); setLoading(false); })
      .catch(() => setLoading(false));
  };

  return (
    <div>
      <h2 style={{ color: COLORS.dark, marginBottom: 8 }}>
        Surplus Alerts
      </h2>
      <p style={{ color: COLORS.gray, marginBottom: 24 }}>
        Oversupply warnings before price crashes happen
      </p>

      <div style={{
        display: 'flex', gap: 12,
        marginBottom: 24, alignItems: 'center'
      }}>
        <select
          value={district}
          onChange={e => setDistrict(e.target.value)}
          style={{
            padding: '10px 16px', borderRadius: 8,
            border: '1px solid #D3D1C7',
            fontSize: 14, background: COLORS.white
          }}
        >
          <option value="">All Districts</option>
          {DISTRICTS.map(d => (
            <option key={d} value={d}>{d}</option>
          ))}
        </select>
        <button
          onClick={load}
          style={{
            padding: '10px 24px',
            background: COLORS.primary,
            color: COLORS.white,
            border: 'none', borderRadius: 8,
            fontSize: 14, cursor: 'pointer'
          }}
        >
          Filter
        </button>
      </div>

      {loading ? (
        <p style={{ color: COLORS.gray }}>Loading...</p>
      ) : alerts.length === 0 ? (
        <div style={{
          background: COLORS.success,
          border: '1px solid #C5DFB0',
          borderRadius: 12, padding: 24,
          textAlign: 'center', color: COLORS.green
        }}>
          ✅ No surplus alerts at this time
        </div>
      ) : (
        <div style={{ display: 'flex', flexDirection: 'column', gap: 12 }}>
          {alerts.map((alert, i) => {
            const style = SEVERITY_COLORS[alert.severity] ||
              SEVERITY_COLORS.medium;
            return (
              <div key={i} style={{
                background: style.bg,
                border: `1px solid ${style.border}`,
                borderRadius: 12, padding: 20,
                borderLeft: `4px solid ${style.color}`
              }}>
                <div style={{
                  display: 'flex', justifyContent: 'space-between',
                  alignItems: 'center', marginBottom: 8
                }}>
                  <strong style={{
                    fontSize: 16, color: COLORS.dark
                  }}>
                    {alert.district} — {alert.crop_id}
                  </strong>
                  <span style={{
                    background: style.bg,
                    color: style.color,
                    border: `1px solid ${style.border}`,
                    fontSize: 11, padding: '3px 10px',
                    borderRadius: 10, fontWeight: 600,
                    textTransform: 'uppercase'
                  }}>{alert.severity}</span>
                </div>
                <div style={{
                  display: 'flex', gap: 24, fontSize: 13,
                  color: COLORS.gray
                }}>
                  <span>Farmers: <strong style={{color: COLORS.dark}}>
                    {alert.farmer_count}
                  </strong></span>
                  <span>Capacity: <strong style={{color: COLORS.dark}}>
                    {alert.market_capacity}
                  </strong></span>
                  <span>Ratio: <strong style={{color: style.color}}>
                    {Math.round(alert.ratio * 100)}%
                  </strong></span>
                </div>
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
}
