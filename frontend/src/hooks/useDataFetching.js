import { useAuth } from './AuthContext';
import api from '../services/api';
import { useState, useEffect } from 'react';

/**
 * Custom hook for managing missing persons data
 */
export const useMissingPersons = () => {
  const [persons, setPersons] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const fetchPersons = async (params = {}) => {
    setLoading(true);
    setError(null);
    try {
      const response = await api.getMissingPersons(params);
      setPersons(response.data.results || []);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  return { persons, loading, error, fetchPersons };
};

/**
 * Custom hook for managing facial matches
 */
export const useMatches = () => {
  const [matches, setMatches] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const fetchMatches = async (params = {}) => {
    setLoading(true);
    setError(null);
    try {
      const response = await api.getMatches(params);
      setMatches(response.data.results || []);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  return { matches, loading, error, fetchMatches };
};

/**
 * Custom hook for managing notifications
 */
export const useNotifications = () => {
  const [notifications, setNotifications] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const fetchNotifications = async (params = {}) => {
    setLoading(true);
    setError(null);
    try {
      const response = await api.getNotifications(params);
      setNotifications(response.data.results || []);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const markAsRead = async (notificationId) => {
    try {
      await api.markNotificationAsRead(notificationId);
      await fetchNotifications();
    } catch (err) {
      console.error('Failed to mark notification as read:', err);
    }
  };

  return { notifications, loading, error, fetchNotifications, markAsRead };
};
