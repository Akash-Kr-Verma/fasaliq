import axios from 'axios';

const API = axios.create({
  // Use environment variable if available, otherwise fallback to local for development
  // or the provided Render URL for production.
  baseURL: import.meta.env.VITE_API_URL || 'http://localhost:8000',
  headers: {
    'Content-Type': 'application/json',
  }
});

// Add a request interceptor to attach Basic Auth headers if credentials exist
API.interceptors.request.use((config) => {
  const auth = localStorage.getItem('fasaliq_admin_auth');
  if (auth) {
    config.headers.Authorization = `Basic ${auth}`;
  }
  return config;
}, (error) => {
  return Promise.reject(error);
});

// Add a response interceptor to handle 401 errors
API.interceptors.response.use((response) => response, (error) => {
  if (error.response && error.response.status === 401) {
    localStorage.removeItem('fasaliq_admin_auth');
    window.location.href = '/login';
  }
  return Promise.reject(error);
});

export default API;
