// Authentication context for managing user state
import React, { createContext, useState, useContext, useEffect } from 'react';
import { jwtDecode } from 'jwt-decode';
import api from '../services/api';

const AuthContext = createContext();

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [selectedRole, setSelectedRole] = useState(localStorage.getItem('selected_role'));

  // Check if user is already logged in
  useEffect(() => {
    const checkAuth = async () => {
      const token = localStorage.getItem('access_token');
      if (token) {
        try {
          const decoded = jwtDecode(token);
          // Check if token is expired
          if (decoded.exp * 1000 > Date.now()) {
            const currentUser = await api.getCurrentUser();
            setUser(currentUser.data);
          } else {
            localStorage.removeItem('access_token');
            localStorage.removeItem('refresh_token');
          }
        } catch (err) {
          console.error('Auth check failed:', err);
          localStorage.removeItem('access_token');
          localStorage.removeItem('refresh_token');
        }
      }
      setLoading(false);
    };

    checkAuth();
  }, []);

  const login = async (username, password) => {
    try {
      setError(null);
      const response = await api.login(username, password);
      localStorage.setItem('access_token', response.data.access);
      localStorage.setItem('refresh_token', response.data.refresh);

      // Use user info from token response if available
      if (response.data.user) {
        setUser(response.data.user);
        return response.data.user;
      } else {
        // Fallback to fetching user if not in response
        const currentUser = await api.getCurrentUser();
        setUser(currentUser.data);
        return currentUser.data;
      }
    } catch (err) {
      const data = err.response?.data;
      let message;
      if (!err.response) {
        message = 'Cannot reach server. Check that the backend is running.';
      } else if (typeof data?.detail === 'string') {
        message = data.detail;
      } else if (Array.isArray(data?.detail)) {
        message = data.detail[0] ?? 'Login failed. Please try again.';
      } else if (data?.non_field_errors?.length) {
        message = data.non_field_errors[0];
      } else if (data?.username?.length) {
        message = data.username[0];
      } else if (data?.password?.length) {
        message = data.password[0];
      } else {
        message = 'Login failed. Please try again.';
      }
      setError(message);
      throw err;
    }
  };

  const logout = () => {
    localStorage.removeItem('access_token');
    localStorage.removeItem('refresh_token');
    localStorage.removeItem('selected_role');
    setUser(null);
    setSelectedRole(null);
  };

  const selectRole = async (role) => {
    setSelectedRole(role);
    localStorage.setItem('selected_role', role);
    return Promise.resolve();
  };

  const value = {
    user,
    loading,
    error,
    selectedRole,
    login,
    logout,
    selectRole,
    isAuthenticated: !!user,
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
};

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within AuthProvider');
  }
  return context;
};
