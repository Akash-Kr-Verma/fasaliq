import React from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import { COLORS } from '../utils/theme';

const menuItems = [
  { label: 'Dashboard',        path: '/',        icon: '📊' },
  { label: 'State Heatmap',    path: '/heatmap', icon: '🌡️' },
  { label: 'District Detail',  path: '/district', icon: '🗺️' },
  { label: 'Surplus Alerts',   path: '/surplus', icon: '⚠️' },
  { label: 'Market Prices',    path: '/prices',  icon: '📈' },
  { label: 'Farmers',          path: '/farmers', icon: '👨‍🌾' },
  { label: 'Weather',          path: '/weather', icon: '🌦️' },
];

export default function Sidebar() {
  const navigate = useNavigate();
  const location = useLocation();

  return (
    <div style={{
      width: 220,
      minHeight: '100vh',
      background: COLORS.dark,
      display: 'flex',
      flexDirection: 'column',
      padding: '20px 0',
      position: 'fixed',
      left: 0, top: 0,
    }}>
      <div style={{ padding: '0 20px 24px' }}>
        <div style={{
          fontSize: 22, fontWeight: 700,
          color: COLORS.white, marginBottom: 4
        }}>FasalIQ</div>
        <div style={{
          fontSize: 11, color: '#888',
          letterSpacing: '0.05em'
        }}>ADMIN PORTAL</div>
      </div>

      {menuItems.map((item) => {
        const active = location.pathname === item.path;
        return (
          <div
            key={item.path}
            onClick={() => navigate(item.path)}
            style={{
              display: 'flex',
              alignItems: 'center',
              gap: 12,
              padding: '12px 20px',
              cursor: 'pointer',
              background: active ? COLORS.primary : 'transparent',
              borderLeft: active
                ? `3px solid ${COLORS.white}`
                : '3px solid transparent',
              color: active ? COLORS.white : '#aaa',
              fontSize: 14,
              transition: 'all 0.2s',
            }}
          >
            <span style={{ fontSize: 18 }}>{item.icon}</span>
            {item.label}
          </div>
        );
      })}

      <div style={{
        marginTop: 'auto',
        padding: '20px',
      }}>
        <div 
          onClick={() => {
            localStorage.removeItem('fasaliq_admin_auth');
            navigate('/login');
          }}
          style={{
            display: 'flex',
            alignItems: 'center',
            gap: 12,
            padding: '12px 20px',
            cursor: 'pointer',
            color: '#ff6b6b',
            fontSize: 14,
            borderRadius: 8,
            transition: 'all 0.2s',
            background: 'rgba(255,107,107,0.1)'
          }}
        >
          <span style={{ fontSize: 18 }}>🚪</span>
          Logout
        </div>
        <div style={{
          marginTop: 20,
          color: '#555',
          fontSize: 11
        }}>
          FasalIQ Admin v1.1
        </div>
      </div>
    </div>
  );
}
