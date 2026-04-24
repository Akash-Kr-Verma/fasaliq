import React from 'react';
import { Navigate } from 'react-router-dom';

export default function ProtectedRoute({ children }) {
  const auth = localStorage.getItem('fasaliq_admin_auth');
  
  if (!auth) {
    return <Navigate to="/login" replace />;
  }

  return children;
}
