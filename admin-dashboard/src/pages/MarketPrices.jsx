import React, { useState, useEffect } from 'react';
import {
  addMarketPrice, updateMSP, getAllCrops
} from '../api/adminService';
import { COLORS, DISTRICTS, CROPS } from '../utils/theme';

export default function MarketPrices() {
  const [crops, setCrops] = useState([]);
  const [priceForm, setPriceForm] = useState({
    crop_name: 'Wheat', district: 'Pune',
    price: '', source: 'Manual'
  });
  const [mspForm, setMspForm] = useState({
    crop_name: 'Wheat', msp: ''
  });
  const [msg, setMsg] = useState('');

  useEffect(() => {
    getAllCrops().then(r => setCrops(r.data.crops || []));
  }, []);

  const submitPrice = async () => {
    try {
      await addMarketPrice({
        ...priceForm, price: parseFloat(priceForm.price)
      });
      setMsg('✅ Market price added successfully!');
      setPriceForm(p => ({ ...p, price: '' }));
    } catch {
      setMsg('❌ Failed to add price');
    }
  };

  const submitMSP = async () => {
    try {
      await updateMSP({
        ...mspForm, msp: parseFloat(mspForm.msp)
      });
      setMsg('✅ MSP updated successfully!');
      setMspForm(p => ({ ...p, msp: '' }));
    } catch {
      setMsg('❌ Failed to update MSP');
    }
  };

  const inputStyle = {
    padding: '10px 14px', borderRadius: 8,
    border: '1px solid #D3D1C7', fontSize: 14,
    background: COLORS.white, width: '100%',
    boxSizing: 'border-box'
  };

  const labelStyle = {
    fontSize: 12, color: COLORS.gray,
    marginBottom: 4, display: 'block',
    fontWeight: 500
  };

  return (
    <div>
      <h2 style={{ color: COLORS.dark, marginBottom: 8 }}>
        Market Prices
      </h2>
      <p style={{ color: COLORS.gray, marginBottom: 24 }}>
        Add mandi prices and update MSP rates
      </p>

      {msg && (
        <div style={{
          padding: '12px 16px', borderRadius: 8,
          marginBottom: 16,
          background: msg.includes('✅')
            ? COLORS.success : COLORS.danger,
          color: msg.includes('✅')
            ? COLORS.green : COLORS.coral
        }}>{msg}</div>
      )}

      <div style={{ display: 'flex', gap: 24, flexWrap: 'wrap' }}>
        <div style={{
          background: COLORS.white,
          border: '1px solid #E5E3DC',
          borderRadius: 12, padding: 24, flex: 1,
          minWidth: 280
        }}>
          <h3 style={{ color: COLORS.dark, marginTop: 0 }}>
            Add Market Price
          </h3>
          <div style={{ marginBottom: 14 }}>
            <label style={labelStyle}>Crop</label>
            <select
              value={priceForm.crop_name}
              onChange={e => setPriceForm(
                p => ({ ...p, crop_name: e.target.value })
              )}
              style={inputStyle}
            >
              {CROPS.map(c => (
                <option key={c} value={c}>{c}</option>
              ))}
            </select>
          </div>
          <div style={{ marginBottom: 14 }}>
            <label style={labelStyle}>District</label>
            <select
              value={priceForm.district}
              onChange={e => setPriceForm(
                p => ({ ...p, district: e.target.value })
              )}
              style={inputStyle}
            >
              {DISTRICTS.map(d => (
                <option key={d} value={d}>{d}</option>
              ))}
            </select>
          </div>
          <div style={{ marginBottom: 14 }}>
            <label style={labelStyle}>Price (₹ per quintal)</label>
            <input
              type="number"
              value={priceForm.price}
              onChange={e => setPriceForm(
                p => ({ ...p, price: e.target.value })
              )}
              placeholder="e.g. 2500"
              style={inputStyle}
            />
          </div>
          <button
            onClick={submitPrice}
            style={{
              width: '100%', padding: '12px',
              background: COLORS.primary,
              color: COLORS.white, border: 'none',
              borderRadius: 8, fontSize: 14,
              cursor: 'pointer', fontWeight: 500
            }}
          >Add Price</button>
        </div>

        <div style={{
          background: COLORS.white,
          border: '1px solid #E5E3DC',
          borderRadius: 12, padding: 24, flex: 1,
          minWidth: 280
        }}>
          <h3 style={{ color: COLORS.dark, marginTop: 0 }}>
            Update MSP
          </h3>
          <div style={{ marginBottom: 14 }}>
            <label style={labelStyle}>Crop</label>
            <select
              value={mspForm.crop_name}
              onChange={e => setMspForm(
                p => ({ ...p, crop_name: e.target.value })
              )}
              style={inputStyle}
            >
              {CROPS.map(c => (
                <option key={c} value={c}>{c}</option>
              ))}
            </select>
          </div>
          <div style={{ marginBottom: 14 }}>
            <label style={labelStyle}>New MSP (₹ per quintal)</label>
            <input
              type="number"
              value={mspForm.msp}
              onChange={e => setMspForm(
                p => ({ ...p, msp: e.target.value })
              )}
              placeholder="e.g. 2275"
              style={inputStyle}
            />
          </div>
          <div style={{
            background: COLORS.info,
            borderRadius: 8, padding: '10px 14px',
            fontSize: 12, color: COLORS.blue,
            marginBottom: 14
          }}>
            Current MSPs from DB:
            {crops.slice(0, 4).map(c => (
              <div key={c.id}>
                {c.name}: ₹{c.msp}
              </div>
            ))}
          </div>
          <button
            onClick={submitMSP}
            style={{
              width: '100%', padding: '12px',
              background: COLORS.secondary,
              color: COLORS.white, border: 'none',
              borderRadius: 8, fontSize: 14,
              cursor: 'pointer', fontWeight: 500
            }}
          >Update MSP</button>
        </div>
      </div>
    </div>
  );
}
