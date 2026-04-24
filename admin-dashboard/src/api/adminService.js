import API from './config';

export const getDashboard = () =>
  API.get('/api/admin/dashboard');

export const getFarmers = (district = '') =>
  API.get(`/api/admin/farmers${district ? `?district=${district}` : ''}`);

export const getDistrictOverview = (district) =>
  API.get(`/api/admin/district-overview/${district}`);

export const getDistrictAnalytics = (district) =>
  API.get(`/api/admin/district-analytics/${district}`);

export const getStateHeatmap = () =>
  API.get('/api/admin/state-heatmap');

export const getSurplusAlerts = (district = '') =>
  API.get(`/api/admin/surplus-alerts${district ? `?district=${district}` : ''}`);

export const addMarketPrice = (data) =>
  API.post('/api/admin/market-price', data);

export const updateMSP = (data) =>
  API.put('/api/admin/msp-update', data);

export const getAllCrops = () =>
  API.get('/api/admin/crops');

export const getWeather = (district) =>
  API.get(`/api/data/weather/${district}`);

export const getAllPrices = (district) =>
  API.get(`/api/data/prices/${district}`);
