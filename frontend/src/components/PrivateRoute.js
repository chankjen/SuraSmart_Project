import React from 'react';
import { Navigate } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';

const PrivateRoute = ({ children }) => {
  const { isAuthenticated, loading, user } = useAuth();

  if (loading) {
    return (
      <div style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '100vh' }}>
        <p>Loading...</p>
      </div>
    );
  }

  // Check if user is authenticated or if there's a token (for immediate navigation)
  const hasToken = !!localStorage.getItem('access_token');
  const isAuth = isAuthenticated || (hasToken && user);

  return isAuth ? children : <Navigate to="/login" />;
};

export default PrivateRoute;
