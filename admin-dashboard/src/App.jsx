import React from 'react';
import {
  BrowserRouter as Router,
  Routes, Route, Navigate
} from 'react-router-dom';
import Sidebar from './components/Sidebar';
import ProtectedRoute from './components/ProtectedRoute';
import Dashboard from './pages/Dashboard';
import StateHeatmap from './pages/StateHeatmap';
import DistrictOverview from './pages/DistrictOverview';
import SurplusAlerts from './pages/SurplusAlerts';
import MarketPrices from './pages/MarketPrices';
import Farmers from './pages/Farmers';
import Weather from './pages/Weather';
import Login from './pages/Login';

function App() {
  return (
    <Router>
      <Routes>
        <Route path="/login" element={<Login />} />
        
        <Route path="/*" element={
          <ProtectedRoute>
            <div style={{
              display: 'flex',
              minHeight: '100vh',
              background: '#F1EFE8',
              fontFamily: '-apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif'
            }}>
              <Sidebar />
              <div style={{
                marginLeft: 220,
                flex: 1,
                padding: 32,
                maxWidth: 'calc(100vw - 220px)'
              }}>
                <Routes>
                  <Route path="/" element={<Dashboard />} />
                  <Route path="/heatmap" element={<StateHeatmap />} />
                  <Route path="/district" element={<DistrictOverview />} />
                  <Route path="/surplus" element={<SurplusAlerts />} />
                  <Route path="/prices" element={<MarketPrices />} />
                  <Route path="/farmers" element={<Farmers />} />
                  <Route path="/weather" element={<Weather />} />
                  <Route path="*" element={<Navigate to="/" replace />} />
                </Routes>
              </div>
            </div>
          </ProtectedRoute>
        } />
      </Routes>
    </Router>
  );
}

export default App;
