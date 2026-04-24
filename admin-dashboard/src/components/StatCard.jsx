import React from 'react';
import { COLORS } from '../utils/theme';

export default function StatCard({
  title, value, subtitle, color, icon, onClick
}) {
  return (
    <div 
      onClick={onClick}
      style={{
        background: COLORS.white,
        border: `1px solid #E5E3DC`,
        borderRadius: 12,
        padding: '20px 24px',
        borderTop: `4px solid ${color || COLORS.primary}`,
        flex: 1,
        minWidth: 180,
        cursor: onClick ? 'pointer' : 'default',
        transition: 'transform 0.2s',
      }}
      onMouseOver={(e) => onClick && (e.currentTarget.style.transform = 'translateY(-2px)')}
      onMouseOut={(e) => onClick && (e.currentTarget.style.transform = 'translateY(0)')}
    >
      <div style={{
        display: 'flex',
        justifyContent: 'space-between',
        alignItems: 'flex-start'
      }}>
        <div>
          <div style={{
            fontSize: 12, color: COLORS.gray,
            textTransform: 'uppercase',
            letterSpacing: '0.05em',
            marginBottom: 8
          }}>{title}</div>
          <div style={{
            fontSize: 32, fontWeight: 700,
            color: COLORS.dark, lineHeight: 1
          }}>{value ?? '—'}</div>
          {subtitle && (
            <div style={{
              fontSize: 12, color: COLORS.gray,
              marginTop: 6
            }}>{subtitle}</div>
          )}
        </div>
        {icon && (
          <span style={{ fontSize: 28 }}>{icon}</span>
        )}
      </div>
    </div>
  );
}
