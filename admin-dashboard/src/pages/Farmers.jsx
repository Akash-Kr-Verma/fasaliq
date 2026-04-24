import React, { useEffect, useState } from 'react';
import { getFarmers } from '../api/adminService';
import { COLORS, DISTRICTS } from '../utils/theme';

export default function Farmers() {
  const [farmers, setFarmers] = useState([]);
  const [district, setDistrict] = useState('');
  const [loading, setLoading] = useState(true);

  useEffect(() => { load(); }, []);

  const load = () => {
    setLoading(true);
    getFarmers(district)
      .then(r => {
        setFarmers(r.data.farmers || []);
        setLoading(false);
      })
      .catch(() => setLoading(false));
  };

  return (
    <div>
      <h2 style={{ color: COLORS.dark, marginBottom: 8 }}>
        Farmers
      </h2>
      <p style={{ color: COLORS.gray, marginBottom: 24 }}>
        All registered farmers on FasalIQ
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
        >Filter</button>
        <span style={{ color: COLORS.gray, fontSize: 13 }}>
          Total: {farmers.length} farmers
        </span>
      </div>

      {loading ? (
        <p style={{ color: COLORS.gray }}>Loading...</p>
      ) : (
        <div style={{
          background: COLORS.white,
          border: '1px solid #E5E3DC',
          borderRadius: 12, overflow: 'hidden'
        }}>
          <table style={{
            width: '100%',
            borderCollapse: 'collapse',
            fontSize: 14
          }}>
            <thead>
              <tr style={{ background: COLORS.dark }}>
                {['ID','Name','Phone','District','Joined'].map(h => (
                  <th key={h} style={{
                    padding: '12px 16px',
                    color: COLORS.white,
                    textAlign: 'left',
                    fontWeight: 500, fontSize: 12,
                    textTransform: 'uppercase',
                    letterSpacing: '0.04em'
                  }}>{h}</th>
                ))}
              </tr>
            </thead>
            <tbody>
              {farmers.length === 0 ? (
                <tr>
                  <td colSpan={5} style={{
                    padding: 24, textAlign: 'center',
                    color: COLORS.gray
                  }}>No farmers found</td>
                </tr>
              ) : farmers.map((f, i) => (
                <tr key={f.id} style={{
                  background: i % 2 === 0
                    ? COLORS.white : COLORS.lightGray
                }}>
                  <td style={{ padding: '12px 16px', color: COLORS.gray }}>
                    {f.id}
                  </td>
                  <td style={{
                    padding: '12px 16px',
                    color: COLORS.dark, fontWeight: 500
                  }}>{f.name}</td>
                  <td style={{ padding: '12px 16px', color: COLORS.gray }}>
                    {f.phone}
                  </td>
                  <td style={{ padding: '12px 16px' }}>
                    <span style={{
                      background: COLORS.info,
                      color: COLORS.blue,
                      padding: '3px 10px', borderRadius: 10,
                      fontSize: 12, fontWeight: 500
                    }}>{f.district}</span>
                  </td>
                  <td style={{ padding: '12px 16px', color: COLORS.gray }}>
                    {f.created_at
                      ? new Date(f.created_at)
                          .toLocaleDateString('en-IN')
                      : '—'}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}
