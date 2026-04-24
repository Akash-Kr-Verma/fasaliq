import React, { useState } from 'react';
import { getWeather } from '../api/adminService';
import { COLORS, DISTRICTS } from '../utils/theme';

export default function Weather() {
  const [district, setDistrict] = useState('Pune');
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(false);

  const load = () => {
    setLoading(true);
    getWeather(district)
      .then(r => { setData(r.data); setLoading(false); })
      .catch(() => setLoading(false));
  };

  return (
    <div>
      <h2 style={{ color: COLORS.dark, marginBottom: 8 }}>
        Weather Forecast
      </h2>
      <p style={{ color: COLORS.gray, marginBottom: 24 }}>
        7-day district weather from IMD via Open-Meteo
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
          {DISTRICTS.map(d => (
            <option key={d} value={d}>{d}</option>
          ))}
        </select>
        <button
          onClick={load}
          style={{
            padding: '10px 24px',
            background: COLORS.primary,
            color: COLORS.white, border: 'none',
            borderRadius: 8, fontSize: 14,
            cursor: 'pointer'
          }}
        >
          {loading ? 'Loading...' : 'Get Forecast'}
        </button>
      </div>

      {data && (
        <div style={{
          display: 'grid',
          gridTemplateColumns: 'repeat(auto-fill, minmax(160px, 1fr))',
          gap: 12
        }}>
          {data.forecast?.map((day, i) => (
            <div key={i} style={{
              background: COLORS.white,
              border: '1px solid #E5E3DC',
              borderRadius: 12, padding: 16,
              borderTop: day.alert
                ? `4px solid ${COLORS.amber}`
                : `4px solid ${COLORS.primary}`
            }}>
              <div style={{
                fontSize: 11, color: COLORS.gray,
                marginBottom: 8, fontWeight: 500
              }}>{new Date(day.date)
                .toLocaleDateString('en-IN',
                  { weekday: 'short', day: 'numeric', month: 'short' }
                )}</div>
              <div style={{
                fontSize: 22, fontWeight: 700,
                color: COLORS.dark
              }}>{day.max_temp}°C</div>
              <div style={{
                fontSize: 12, color: COLORS.gray,
                marginBottom: 8
              }}>Min: {day.min_temp}°C</div>
              <div style={{
                fontSize: 12, color: COLORS.blue
              }}>🌧️ {day.rainfall_mm}mm</div>
              <div style={{
                fontSize: 12, color: COLORS.gray
              }}>💨 {day.windspeed_kmh} km/h</div>
              {day.alert && (
                <div style={{
                  marginTop: 8, fontSize: 11,
                  color: COLORS.amber,
                  background: COLORS.warning,
                  borderRadius: 6, padding: '4px 8px'
                }}>⚠️ {day.alert}</div>
              )}
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
