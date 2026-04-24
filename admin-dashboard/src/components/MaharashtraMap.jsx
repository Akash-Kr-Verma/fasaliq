import React from 'react';
import { COLORS, DIVISIONS } from '../utils/theme';

export default function MaharashtraMap({ selectedDistrict, onSelectDistrict }) {
  return (
    <div style={{
      background: COLORS.white,
      border: '1px solid #E5E3DC',
      borderRadius: 16,
      padding: 28,
      display: 'flex',
      flexDirection: 'column',
    }}>
      <h3 style={{ margin: '0 0 6px', color: COLORS.dark, fontSize: 16 }}>
        Maharashtra — Select a District
      </h3>
      <p style={{ margin: '0 0 20px', color: COLORS.gray, fontSize: 12 }}>
        36 districts across 6 revenue divisions
      </p>

      {/* Legend */}
      <div style={{
        display: 'flex', flexWrap: 'wrap', gap: 10, marginBottom: 20
      }}>
        {Object.entries(DIVISIONS).map(([divName, div]) => (
          <div key={divName} style={{ display: 'flex', alignItems: 'center', gap: 5, fontSize: 11, color: COLORS.gray }}>
            <span style={{ width: 10, height: 10, borderRadius: 3, background: div.color, display: 'inline-block' }} />
            {divName} Division
          </div>
        ))}
      </div>

      {/* Districts grouped by division */}
      <div style={{ display: 'flex', flexDirection: 'column', gap: 14 }}>
        {Object.entries(DIVISIONS).map(([divName, div]) => (
          <div key={divName}>
            <div style={{
              fontSize: 10, fontWeight: 700, color: div.color,
              textTransform: 'uppercase', letterSpacing: '0.08em',
              marginBottom: 8
            }}>
              {divName} Division
            </div>
            <div style={{ display: 'flex', flexWrap: 'wrap', gap: 8 }}>
              {div.districts.map((d) => {
                const isActive = selectedDistrict === d;
                return (
                  <div
                    key={d}
                    onClick={() => onSelectDistrict(d)}
                    style={{
                      background: isActive ? div.color : '#F9F8F5',
                      color: isActive ? '#fff' : COLORS.dark,
                      padding: '7px 14px',
                      borderRadius: 20,
                      cursor: 'pointer',
                      fontSize: 13,
                      fontWeight: isActive ? 700 : 400,
                      border: isActive ? `2px solid ${div.color}` : '1px solid #E5E3DC',
                      transition: 'all 0.18s',
                      boxShadow: isActive ? `0 2px 10px ${div.color}40` : 'none',
                      userSelect: 'none',
                    }}
                  >
                    {d}
                  </div>
                );
              })}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
