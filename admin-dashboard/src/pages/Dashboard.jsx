import React, { useEffect, useState } from 'react';
import StatCard from '../components/StatCard';
import { getDashboard } from '../api/adminService';
import { COLORS } from '../utils/theme';
import {
  BarChart, Bar, XAxis, YAxis,
  CartesianGrid, Tooltip, ResponsiveContainer
} from 'recharts';

export default function Dashboard() {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    getDashboard()
      .then(r => { setData(r.data); setLoading(false); })
      .catch(() => setLoading(false));
  }, []);

  const chartData = data ? [
    { name: 'Farmers', value: data.total_farmers },
    { name: 'Buyers', value: data.total_buyers },
    { name: 'Recommendations', value: data.total_recommendations },
    { name: 'Surplus Alerts', value: data.total_surplus_alerts },
    { name: 'Anomalies', value: data.total_anomalies },
  ] : [];

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
              title="Anomalies"
              value={data?.total_anomalies}
              icon="🔴"
              color={COLORS.coral}
            />
          </div>

          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(400px, 1fr))', gap: 24 }}>
            {/* Recent Anomalies Panel */}
            <div style={{
              background: COLORS.white, border: '1px solid #E5E3DC', borderRadius: 12, padding: 24
            }}>
              <h3 style={{ color: COLORS.coral, marginTop: 0, display: 'flex', alignItems: 'center', gap: 8 }}>
                🔴 Recent Anomalies
              </h3>
              <p style={{ fontSize: 12, color: COLORS.gray, marginBottom: 16 }}>
                Critical production or market issues reported by farmers.
              </p>
              {data?.recent_anomalies?.length > 0 ? (
                <div style={{ display: 'flex', flexDirection: 'column', gap: 12 }}>
                  {data.recent_anomalies.map((a, i) => (
                    <div key={i} style={{ padding: '12px 16px', background: '#FEF2F2', borderRadius: 8, borderLeft: `4px solid ${COLORS.coral}` }}>
                      <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 4 }}>
                        <strong style={{ fontSize: 13 }}>{a.detected_crop || 'Unknown'} — {a.reason || 'General Issue'}</strong>
                        <span style={{ fontSize: 11, color: COLORS.gray }}>{new Date(a.reported_at).toLocaleDateString()}</span>
                      </div>
                      <div style={{ fontSize: 12, color: COLORS.dark }}>
                        Farmer: <strong>{a.farmer}</strong> ({a.district}) • Type: {a.type}
                      </div>
                    </div>
                  ))}
                </div>
              ) : (
                <p style={{ fontSize: 13, color: COLORS.gray }}>No recent anomalies reported.</p>
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
