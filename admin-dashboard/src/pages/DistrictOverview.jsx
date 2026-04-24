import React, { useState, useEffect } from 'react';
import { getDistrictOverview, getDistrictAnalytics } from '../api/adminService';
import { COLORS } from '../utils/theme';
import MaharashtraMap from '../components/MaharashtraMap';
import StatCard from '../components/StatCard';
import {
  PieChart, Pie, Cell, Tooltip, Legend, ResponsiveContainer,
  BarChart, Bar, XAxis, YAxis, CartesianGrid, ReferenceLine
} from 'recharts';

const PIE_COLORS = [
  '#0F6E56','#534AB7','#854F0B','#993C1D',
  '#3B6D11','#185FA5','#2C2C2A','#5F5E5A'
];

const MSPTooltip = ({ active, payload, label }) => {
  if (active && payload && payload.length) {
    return (
      <div style={{ background: '#fff', border: '1px solid #E5E3DC', borderRadius: 8, padding: '10px 14px', fontSize: 12 }}>
        <p style={{ fontWeight: 700, margin: '0 0 6px', color: COLORS.dark }}>{label}</p>
        {payload.map((p) => (
          <p key={p.name} style={{ margin: '2px 0', color: p.color }}>
            {p.name}: ₹{p.value?.toLocaleString('en-IN')}
          </p>
        ))}
      </div>
    );
  }
  return null;
};

const GapTooltip = ({ active, payload, label }) => {
  if (active && payload && payload.length) {
    const gap = (payload[0]?.value || 0) - (payload[1]?.value || 0);
    return (
      <div style={{ background: '#fff', border: '1px solid #E5E3DC', borderRadius: 8, padding: '10px 14px', fontSize: 12 }}>
        <p style={{ fontWeight: 700, margin: '0 0 6px', color: COLORS.dark }}>{label}</p>
        {payload.map((p) => (
          <p key={p.name} style={{ margin: '2px 0', color: p.color }}>
            {p.name}: {p.value} T
          </p>
        ))}
        <p style={{ margin: '4px 0 0', fontWeight: 700, color: gap > 0 ? COLORS.amber : COLORS.green }}>
          {gap > 0 ? `Surplus: +${gap.toFixed(1)} T` : `Deficit: ${gap.toFixed(1)} T`}
        </p>
      </div>
    );
  }
  return null;
};

export default function DistrictOverview() {
  const [district, setDistrict] = useState('Pune');
  const [overviewData, setOverviewData] = useState(null);
  const [analyticsData, setAnalyticsData] = useState(null);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    loadAll(district);
  }, [district]);

  const loadAll = (d) => {
    setLoading(true);
    Promise.all([
      getDistrictOverview(d),
      getDistrictAnalytics(d)
    ])
      .then(([r1, r2]) => {
        setOverviewData(r1.data);
        setAnalyticsData(r2.data);
        setLoading(false);
      })
      .catch(() => setLoading(false));
  };

  const progressData = overviewData?.crops_in_progress
    ? Object.entries(overviewData.crops_in_progress).map(([name, value]) => ({ name, value }))
    : [];

  const demandData = overviewData?.buyer_demand
    ? Object.entries(overviewData.buyer_demand).map(([name, value]) => ({ name, value }))
    : [];

  const mspChartData = analyticsData?.msp_vs_market?.filter(d => d.msp > 0 || d.market_price) || [];
  const gapChartData = analyticsData?.supply_demand_gap || [];
  const compliance = analyticsData?.msp_compliance;

  return (
    <div>
      <h2 style={{ color: COLORS.dark, marginBottom: 8 }}>District Intelligence</h2>
      <p style={{ color: COLORS.gray, marginBottom: 24 }}>
        Select a district to view active crops, market analytics, and government intervention signals.
      </p>

      {/* ── Top Row: Map + Key Stats ── */}
      <div style={{ display: 'flex', gap: 24, marginBottom: 32, flexWrap: 'wrap' }}>
        <div style={{ flex: 1.5, minWidth: 350 }}>
          <MaharashtraMap selectedDistrict={district} onSelectDistrict={setDistrict} />
        </div>

        <div style={{ flex: 1, minWidth: 280, display: 'flex', flexDirection: 'column', gap: 14 }}>
          {loading ? (
            <div style={{ padding: 40, textAlign: 'center', color: COLORS.gray }}>Loading…</div>
          ) : overviewData ? (
            <>
              <StatCard title="Total Farmers" value={overviewData.total_farmers} icon="👨‍🌾" color={COLORS.primary} />
              <StatCard
                title="Projected Yield"
                value={`${Math.round(overviewData.projected_yield)} T`}
                subtitle={overviewData.yield_breakdown?.length > 0 
                  ? overviewData.yield_breakdown.map(y => `${y.crop}: ${y.total_yield}T`).join(', ')
                  : "From selected recommendations"}
                icon="🌾" color={COLORS.green}
              />
              <StatCard
                title="Surplus Risk"
                value={overviewData.surplus_alerts?.length || 0}
                subtitle="Active warnings"
                icon="⚠️" color={COLORS.amber}
              />
              {compliance && (
                <StatCard
                  title="MSP Compliance"
                  value={`${compliance.compliance_rate}%`}
                  subtitle={`${compliance.msp_covered}/${compliance.total_active_crops} crops protected`}
                  icon="🛡️"
                  color={compliance.compliance_rate === 100 ? COLORS.green : compliance.compliance_rate >= 50 ? COLORS.amber : COLORS.coral}
                />
              )}
            </>
          ) : (
            <div style={{ padding: 40, textAlign: 'center', color: COLORS.gray }}>Select a district</div>
          )}
        </div>
      </div>

      {overviewData && analyticsData && !loading && (
        <>
          {/* ── MSP vs Market Price ── */}
          <div style={{
            background: COLORS.white, border: '1px solid #E5E3DC',
            borderRadius: 12, padding: 24, marginBottom: 24
          }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 4 }}>
              <h3 style={{ margin: 0, color: COLORS.dark }}>MSP vs Market Price</h3>
              <span style={{ fontSize: 12, color: COLORS.gray }}>₹ per quintal</span>
            </div>
            <p style={{ color: COLORS.gray, fontSize: 12, marginTop: 4, marginBottom: 16 }}>
              🔴 Red bars indicate market price has fallen below MSP — government procurement may be needed.
            </p>
            {mspChartData.length > 0 ? (
              <ResponsiveContainer width="100%" height={280}>
                <BarChart data={mspChartData} margin={{ top: 10, right: 10, left: 0, bottom: 0 }}>
                  <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#f0f0f0" />
                  <XAxis dataKey="crop" fontSize={12} />
                  <YAxis fontSize={12} tickFormatter={v => `₹${v}`} />
                  <Tooltip content={<MSPTooltip />} />
                  <Legend />
                  <Bar dataKey="msp" name="MSP" fill={COLORS.secondary} radius={[4,4,0,0]} />
                  <Bar
                    dataKey="market_price"
                    name="Market Price"
                    radius={[4,4,0,0]}
                    fill={COLORS.primary}
                    // Custom cell coloring handled via data
                  />
                </BarChart>
              </ResponsiveContainer>
            ) : (
              <div style={{ padding: 32, textAlign: 'center', color: COLORS.gray }}>
                No market prices recorded for this district yet. Add prices via the Market Prices page.
              </div>
            )}
            {mspChartData.some(d => d.below_msp) && (
              <div style={{
                marginTop: 16, padding: '12px 16px',
                background: COLORS.danger, borderRadius: 8,
                borderLeft: `4px solid ${COLORS.coral}`,
                color: COLORS.coral, fontSize: 13
              }}>
                ⚠️ <strong>Intervention Alert:</strong>{' '}
                {mspChartData.filter(d => d.below_msp).map(d => d.crop).join(', ')} — market prices below MSP. Consider government procurement.
              </div>
            )}
          </div>

          {/* ── Supply-Demand Gap ── */}
          <div style={{
            background: COLORS.white, border: '1px solid #E5E3DC',
            borderRadius: 12, padding: 24, marginBottom: 24
          }}>
            <h3 style={{ margin: '0 0 4px', color: COLORS.dark }}>Supply vs Demand Gap</h3>
            <p style={{ color: COLORS.gray, fontSize: 12, marginTop: 4, marginBottom: 16 }}>
              Compare projected supply (farmer yield) vs buyer demand per crop. Surplus = supply exceeds demand.
            </p>
            {gapChartData.length > 0 ? (
              <ResponsiveContainer width="100%" height={280}>
                <BarChart data={gapChartData} margin={{ top: 10, right: 10, left: 0, bottom: 0 }}>
                  <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#f0f0f0" />
                  <XAxis dataKey="crop" fontSize={12} />
                  <YAxis fontSize={12} tickFormatter={v => `${v} T`} />
                  <Tooltip content={<GapTooltip />} />
                  <Legend />
                  <Bar dataKey="supply" name="Supply (T)" fill={COLORS.green} radius={[4,4,0,0]} />
                  <Bar dataKey="demand" name="Demand (T)" fill={COLORS.secondary} radius={[4,4,0,0]} />
                </BarChart>
              </ResponsiveContainer>
            ) : (
              <p style={{ color: COLORS.gray }}>No supply or demand data available for this district.</p>
            )}
          </div>

          {/* ── Trade & Logistics Intelligence ── */}
          <div style={{
            display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(400px, 1fr))', gap: 24, marginBottom: 24
          }}>
            {/* Potential Sources (Demand Matching) */}
            <div style={{
              background: COLORS.white, border: '1px solid #E5E3DC', borderRadius: 12, padding: 24,
              borderLeft: `6px solid ${COLORS.secondary}`
            }}>
              <h3 style={{ margin: 0, color: COLORS.secondary, display: 'flex', alignItems: 'center', gap: 8 }}>
                🚢 Supply Sourcing (Inbound)
              </h3>
              <p style={{ color: COLORS.gray, fontSize: 12, marginTop: 4, marginBottom: 16 }}>
                Districts with available supply for crops demanded in <strong>{district}</strong>.
              </p>
              {analyticsData.demand_matches?.length > 0 ? (
                <div style={{ display: 'flex', flexDirection: 'column', gap: 10 }}>
                  {analyticsData.demand_matches.map((m, i) => (
                    <div key={i} style={{ padding: '10px 14px', background: '#F8FAFC', borderRadius: 8, border: '1px solid #E2E8F0' }}>
                      <div style={{ display: 'flex', justifyContent: 'space-between', fontWeight: 600, fontSize: 14 }}>
                        <span>{m.crop}</span>
                        <span style={{ color: COLORS.secondary }}>+{m.potential_match} T Available</span>
                      </div>
                      <div style={{ fontSize: 12, color: COLORS.gray, marginTop: 2 }}>
                        Source: <strong>{m.source_district}</strong> (Total supply: {m.available_supply}T)
                      </div>
                    </div>
                  ))}
                </div>
              ) : (
                <p style={{ color: COLORS.gray, fontSize: 13 }}>No external supply matches found for local demand.</p>
              )}
            </div>

            {/* Potential Buyers (Supply Matching) */}
            <div style={{
              background: COLORS.white, border: '1px solid #E5E3DC', borderRadius: 12, padding: 24,
              borderLeft: `6px solid ${COLORS.green}`
            }}>
              <h3 style={{ margin: 0, color: COLORS.green, display: 'flex', alignItems: 'center', gap: 8 }}>
                📈 Market Opportunities (Outbound)
              </h3>
              <p style={{ color: COLORS.gray, fontSize: 12, marginTop: 4, marginBottom: 16 }}>
                Districts with high demand for surplus crops produced in <strong>{district}</strong>.
              </p>
              {analyticsData.supply_matches?.length > 0 ? (
                <div style={{ display: 'flex', flexDirection: 'column', gap: 10 }}>
                  {analyticsData.supply_matches.map((m, i) => (
                    <div key={i} style={{ padding: '10px 14px', background: '#F0FDF4', borderRadius: 8, border: '1px solid #DCFCE7' }}>
                      <div style={{ display: 'flex', justifyContent: 'space-between', fontWeight: 600, fontSize: 14 }}>
                        <span>{m.crop}</span>
                        <span style={{ color: COLORS.green }}>Sell up to {m.potential_match} T</span>
                      </div>
                      <div style={{ fontSize: 12, color: COLORS.gray, marginTop: 2 }}>
                        Destination: <strong>{m.target_district}</strong> (Total demand: {m.demand_qty}T)
                      </div>
                    </div>
                  ))}
                </div>
              ) : (
                <p style={{ color: COLORS.gray, fontSize: 13 }}>No external buyers found for local surplus.</p>
              )}
            </div>
          </div>

          {/* ── Bottom 2-col Grid ── */}
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(380px, 1fr))', gap: 24, marginBottom: 24 }}>
            {/* Crops in Progress */}
            <div style={{ background: COLORS.white, border: '1px solid #E5E3DC', borderRadius: 12, padding: 24 }}>
              <h3 style={{ color: COLORS.dark, marginTop: 0 }}>Crops in Progress</h3>
              {progressData.length > 0 ? (
                <ResponsiveContainer width="100%" height={220}>
                  <BarChart data={progressData}>
                    <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#f0f0f0" />
                    <XAxis dataKey="name" fontSize={11} />
                    <YAxis fontSize={11} />
                    <Tooltip />
                    <Bar dataKey="value" name="Farmers" fill={COLORS.primary} radius={[4,4,0,0]} />
                  </BarChart>
                </ResponsiveContainer>
              ) : (
                <p style={{ color: COLORS.gray }}>No crops currently in progress.</p>
              )}
            </div>

            {/* Buyer Demand Pie */}
            <div style={{ background: COLORS.white, border: '1px solid #E5E3DC', borderRadius: 12, padding: 24 }}>
              <h3 style={{ color: COLORS.dark, marginTop: 0 }}>Market Demand (Buyers)</h3>
              {demandData.length > 0 ? (
                <ResponsiveContainer width="100%" height={220}>
                  <PieChart>
                    <Pie data={demandData} cx="50%" cy="50%" outerRadius={75} dataKey="value" label={({name, value}) => `${name}: ${value}T`}>
                      {demandData.map((_, i) => <Cell key={i} fill={PIE_COLORS[i % PIE_COLORS.length]} />)}
                    </Pie>
                    <Tooltip />
                    <Legend />
                  </PieChart>
                </ResponsiveContainer>
              ) : (
                <p style={{ color: COLORS.gray }}>No buyer demand recorded.</p>
              )}
            </div>
          </div>

          {/* ── Surplus Warnings ── */}
          <div style={{
            background: '#FAEEDA', border: '1px solid #F5D9A8', borderRadius: 12, padding: 24
          }}>
            <h3 style={{ color: COLORS.amber, marginTop: 0 }}>⚠️ Surplus Warnings</h3>
            {overviewData.surplus_alerts?.length > 0 ? (
              <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(300px, 1fr))', gap: 12 }}>
                {overviewData.surplus_alerts.map((alert, i) => (
                  <div key={i} style={{ background: COLORS.white, borderRadius: 8, padding: '12px 16px', borderLeft: `4px solid ${COLORS.amber}` }}>
                    <strong>{alert.crop_name}</strong> — {alert.message}
                    <div style={{ marginTop: 4, fontSize: 11, color: COLORS.gray }}>
                      Severity: <span style={{ color: COLORS.amber, fontWeight: 700 }}>{alert.severity?.toUpperCase()}</span>
                    </div>
                  </div>
                ))}
              </div>
            ) : (
              <p style={{ color: COLORS.green, margin: 0 }}>✅ No surplus warnings for this district.</p>
            )}
          </div>
        </>
      )}
    </div>
  );
}
