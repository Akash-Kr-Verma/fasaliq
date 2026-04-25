import React, { useEffect, useState } from 'react';
import StatCard from '../components/StatCard';
import { getDashboard, getAnomalies } from '../api/adminService';
import { COLORS } from '../utils/theme';
import { downloadCSV } from '../utils/csvExport';
import {
  BarChart, Bar, XAxis, YAxis,
  CartesianGrid, Tooltip, ResponsiveContainer
} from 'recharts';

export default function Dashboard() {
  const [data, setData] = useState(null);
  const [allAnomalies, setAllAnomalies] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showAllAnomalies, setShowAllAnomalies] = useState(false);

  useEffect(() => {
    setLoading(true);
    Promise.all([
      getDashboard(),
      getAnomalies()
    ])
      .then(([dashRes, anomalyRes]) => {
        setData(dashRes.data);
        setAllAnomalies(anomalyRes.data.anomalies);
        setLoading(false);
      })
      .catch(() => setLoading(false));
  }, []);

  const getMostFrequentAnomaly = (anomalies) => {
    if (!anomalies || anomalies.length === 0) return 'None';
    const counts = {};
    anomalies.forEach(a => {
      const type = a.type || 'Unknown';
      counts[type] = (counts[type] || 0) + 1;
    });
    return Object.keys(counts).reduce((a, b) => counts[a] > counts[b] ? a : b);
  };

  const mostFrequentAnomaly = getMostFrequentAnomaly(allAnomalies);

  const chartData = data ? [
    { name: 'Farmers', value: data.total_farmers },
    { name: 'Buyers', value: data.total_buyers },
    { name: 'Recommendations', value: data.total_recommendations },
    { name: 'Surplus Alerts', value: data.total_surplus_alerts },
    { name: 'Anomalies', value: data.total_anomalies },
  ] : [];

  const handleDownloadCSV = () => {
    const exportData = allAnomalies.map(a => ({
      ID: a.id,
      Farmer: a.farmer_name,
      District: a.district,
      Type: a.type,
      Crop: a.detected_crop,
      Reason: a.reason,
      Date: new Date(a.reported_at).toLocaleString()
    }));
    downloadCSV(exportData, `maharashtra_anomalies_${new Date().toISOString().split('T')[0]}.csv`);
  };

  return (
    <div>
      <h2 style={{ color: COLORS.dark, marginBottom: 8 }}>
        Dashboard
      </h2>
      <p style={{ color: COLORS.gray, marginBottom: 24 }}>
        FasalIQ platform overview & intelligence feed
      </p>

      {loading ? (
        <p style={{ color: COLORS.gray }}>Loading...</p>
      ) : (
        <>
          <div style={{
            display: 'flex', gap: 16,
            flexWrap: 'wrap', marginBottom: 32
          }}>
            <StatCard
              title="Total Farmers"
              value={data?.total_farmers}
              icon="👨‍🌾"
              color={COLORS.primary}
            />
            <StatCard
              title="Total Buyers"
              value={data?.total_buyers}
              icon="🏪"
              color={COLORS.secondary}
            />
            <StatCard
              title="Recommendations"
              value={data?.total_recommendations}
              icon="🌾"
              color={COLORS.green}
            />
            <StatCard
              title="Surplus Alerts"
              value={data?.total_surplus_alerts}
              icon="⚠️"
              color={COLORS.amber}
            />
            <StatCard
              title="Most Frequent Issue"
              value={mostFrequentAnomaly}
              subtitle="State-wide trend"
              icon="📉"
              color={COLORS.coral}
            />
          </div>

          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(400px, 1fr))', gap: 24 }}>
            {/* Recent Anomalies Panel */}
            <div style={{
              background: COLORS.white, border: '1px solid #E5E3DC', borderRadius: 12, padding: 24
            }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
                <div>
                  <h3 style={{ color: COLORS.coral, marginTop: 0, display: 'flex', alignItems: 'center', gap: 8 }}>
                    🔴 Recent Anomalies
                  </h3>
                  <p style={{ fontSize: 12, color: COLORS.gray, marginBottom: 16 }}>
                    Critical production or market issues reported by farmers.
                  </p>
                </div>
                <button 
                  onClick={handleDownloadCSV}
                  style={{
                    padding: '8px 12px', background: COLORS.coral, color: '#white', 
                    border: 'none', borderRadius: 6, fontSize: 12, cursor: 'pointer',
                    color: 'white', fontWeight: 600
                  }}
                >
                  📥 Download CSV
                </button>
              </div>

              <div style={{ display: 'flex', flexDirection: 'column', gap: 12 }}>
                {(showAllAnomalies ? allAnomalies : (data?.recent_anomalies || [])).map((a, i) => (
                  <div key={i} style={{ padding: '12px 16px', background: '#FEF2F2', borderRadius: 8, borderLeft: `4px solid ${COLORS.coral}` }}>
                    <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 4 }}>
                      <strong style={{ fontSize: 13, color: COLORS.dark }}>
                        {a.detected_crop || 'Unknown'} — <span style={{ color: COLORS.coral }}>{a.reason || 'General Issue'}</span>
                      </strong>
                      <span style={{ fontSize: 11, color: COLORS.gray }}>
                        {new Date(a.reported_at).toLocaleDateString()}
                      </span>
                    </div>
                    <div style={{ fontSize: 12, color: COLORS.gray }}>
                      Farmer: <strong style={{ color: COLORS.dark }}>{a.farmer || a.farmer_name}</strong> in <strong style={{ color: COLORS.coral }}>{a.district}</strong>
                    </div>
                  </div>
                ))}
              </div>
              
              {allAnomalies.length > 5 && (
                <button 
                  onClick={() => setShowAllAnomalies(!showAllAnomalies)}
                  style={{ 
                    marginTop: 16, width: '100%', padding: '10px', 
                    background: '#FEE2E2', color: COLORS.coral, border: 'none', 
                    borderRadius: 8, fontSize: 13, fontWeight: 600, cursor: 'pointer' 
                  }}
                >
                  {showAllAnomalies ? '↑ Show Less' : `↓ Show All (${allAnomalies.length})`}
                </button>
              )}
            </div>

            {/* Anomaly Hotspots by District */}
            <div style={{
              background: COLORS.white, border: '1px solid #E5E3DC', borderRadius: 12, padding: 24
            }}>
              <h3 style={{ color: COLORS.dark, marginTop: 0, display: 'flex', alignItems: 'center', gap: 8 }}>
                📍 Anomaly Hotspots
              </h3>
              <p style={{ fontSize: 12, color: COLORS.gray, marginBottom: 16 }}>
                Districts with the most active production issues.
              </p>
              {data?.anomalies_by_district?.length > 0 ? (
                <ResponsiveContainer width="100%" height={180}>
                  <BarChart 
                    layout="vertical" 
                    data={data.anomalies_by_district}
                    margin={{ left: 40, right: 20 }}
                  >
                    <CartesianGrid strokeDasharray="3 3" horizontal={false} stroke="#f0f0f0"/>
                    <XAxis type="number" hide />
                    <YAxis 
                      dataKey="district" 
                      type="category" 
                      tick={{ fontSize: 11, fill: COLORS.dark }}
                      width={80}
                    />
                    <Tooltip cursor={{fill: 'transparent'}} />
                    <Bar 
                      dataKey="count" 
                      fill={COLORS.coral} 
                      radius={[0, 4, 4, 0]}
                      barSize={20}
                    />
                  </BarChart>
                </ResponsiveContainer>
              ) : (
                <p style={{ fontSize: 13, color: COLORS.gray }}>No data available.</p>
              )}
            </div>

            {/* Recent Recommendations Panel */}
            <div style={{
              background: COLORS.white, border: '1px solid #E5E3DC', borderRadius: 12, padding: 24
            }}>

              <h3 style={{ color: COLORS.green, marginTop: 0, display: 'flex', alignItems: 'center', gap: 8 }}>
                🌾 New Recommendations
              </h3>
              <p style={{ fontSize: 12, color: COLORS.gray, marginBottom: 16 }}>
                AI-driven crop suggestions provided to farmers.
              </p>
              {data?.recent_recommendations?.length > 0 ? (
                <div style={{ display: 'flex', flexDirection: 'column', gap: 12 }}>
                  {data.recent_recommendations.map((r, i) => (
                    <div key={i} style={{ padding: '12px 16px', background: '#F0FDF4', borderRadius: 8, borderLeft: `4px solid ${COLORS.green}` }}>
                      <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 4 }}>
                        <strong style={{ fontSize: 13 }}>{r.crop}</strong>
                        <span style={{ fontSize: 11, color: COLORS.gray }}>{new Date(r.created_at).toLocaleDateString()}</span>
                      </div>
                      <div style={{ fontSize: 12, color: COLORS.dark }}>
                        Farmer: <strong>{r.farmer}</strong> ({r.district}) • Score: <strong>{r.score}</strong>
                      </div>
                    </div>
                  ))}
                </div>
              ) : (
                <p style={{ fontSize: 13, color: COLORS.gray }}>No recent recommendations.</p>
              )}
            </div>
          </div>

          <div style={{
            background: COLORS.white,
            border: '1px solid #E5E3DC',
            borderRadius: 12,
            padding: 24,
            marginTop: 24
          }}>
            <h3 style={{
              color: COLORS.dark,
              marginBottom: 20, marginTop: 0
            }}>Platform Activity Summary</h3>
            <ResponsiveContainer width="100%" height={280}>
              <BarChart data={chartData}>
                <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0"/>
                <XAxis dataKey="name" tick={{ fontSize: 12 }}/>
                <YAxis tick={{ fontSize: 12 }}/>
                <Tooltip/>
                <Bar
                  dataKey="value"
                  fill={COLORS.primary}
                  radius={[4,4,0,0]}
                />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </>
      )}
    </div>
  );
}
