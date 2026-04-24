import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { COLORS } from '../utils/theme';

export default function Login() {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const navigate = useNavigate();

  const handleLogin = (e) => {
    e.preventDefault();
    try {
      // Basic Auth encoding
      const auth = window.btoa(`${username}:${password}`);
      localStorage.setItem('fasaliq_admin_auth', auth);
      // We'll try a small API call to verify if the credentials work
      // For now, we'll just redirect and the interceptor will handle 401s
      navigate('/');
    } catch (err) {
      setError('Invalid credentials format');
    }
  };

  return (
    <div style={{
      height: '100vh',
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'center',
      background: '#F1EFE8',
      fontFamily: '-apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif'
    }}>
      <div style={{
        background: COLORS.white,
        padding: '40px',
        borderRadius: '16px',
        boxShadow: '0 4px 20px rgba(0,0,0,0.08)',
        width: '100%',
        maxWidth: '400px'
      }}>
        <div style={{ textAlign: 'center', marginBottom: '32px' }}>
          <h1 style={{ color: COLORS.primary, margin: 0, fontSize: '28px' }}>FasalIQ</h1>
          <p style={{ color: COLORS.gray, margin: '8px 0 0', fontSize: '14px' }}>ADMIN PORTAL SECURE ACCESS</p>
        </div>

        <form onSubmit={handleLogin}>
          <div style={{ marginBottom: '20px' }}>
            <label style={{ display: 'block', fontSize: '12px', color: COLORS.gray, marginBottom: '6px', fontWeight: 600 }}>USERNAME</label>
            <input
              type="text"
              value={username}
              onChange={(e) => setUsername(e.target.value)}
              style={{
                width: '100%', padding: '12px', borderRadius: '8px', border: '1px solid #D3D1C7',
                boxSizing: 'border-box', outline: 'none'
              }}
              placeholder="Enter admin username"
              required
            />
          </div>

          <div style={{ marginBottom: '24px' }}>
            <label style={{ display: 'block', fontSize: '12px', color: COLORS.gray, marginBottom: '6px', fontWeight: 600 }}>PASSWORD</label>
            <input
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              style={{
                width: '100%', padding: '12px', borderRadius: '8px', border: '1px solid #D3D1C7',
                boxSizing: 'border-box', outline: 'none'
              }}
              placeholder="Enter admin password"
              required
            />
          </div>

          {error && <p style={{ color: COLORS.coral, fontSize: '12px', marginBottom: '16px' }}>{error}</p>}

          <button
            type="submit"
            style={{
              width: '100%', padding: '14px', background: COLORS.primary, color: COLORS.white,
              border: 'none', borderRadius: '8px', fontSize: '16px', fontWeight: 600, cursor: 'pointer'
            }}
          >
            Sign In
          </button>
        </form>

        <div style={{ marginTop: '24px', textAlign: 'center', fontSize: '12px', color: '#999' }}>
          Protected by FasalIQ Security Protocol
        </div>
      </div>
    </div>
  );
}
