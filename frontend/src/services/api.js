import axios from 'axios';
import { jwtDecode } from 'jwt-decode';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000/api';

class ApiClient {
  constructor() {
    this.api = axios.create({
      baseURL: API_BASE_URL,
      headers: {
        'Content-Type': 'application/json',
      },
    });

    // Add request interceptor to include JWT token
    this.api.interceptors.request.use(
      (config) => {
        const token = localStorage.getItem('access_token');
        if (token) {
          config.headers.Authorization = `Bearer ${token}`;
        }
        return config;
      },
      (error) => Promise.reject(error)
    );

    // Add response interceptor to handle token refresh
    this.api.interceptors.response.use(
      (response) => response,
      async (error) => {
        const originalRequest = error.config;

        if (
          error.response?.status === 401 &&
          !originalRequest._retry &&
          localStorage.getItem('refresh_token')
        ) {
          originalRequest._retry = true;

          try {
            const refreshToken = localStorage.getItem('refresh_token');
            const response = await this.api.post('/auth/token/refresh/', {
              refresh: refreshToken,
            });

            localStorage.setItem('access_token', response.data.access);
            this.api.defaults.headers.Authorization = `Bearer ${response.data.access}`;
            originalRequest.headers.Authorization = `Bearer ${response.data.access}`;

            return this.api(originalRequest);
          } catch (refreshError) {
            localStorage.removeItem('access_token');
            localStorage.removeItem('refresh_token');
            window.location.href = '/login';
            return Promise.reject(refreshError);
          }
        }

        return Promise.reject(error);
      }
    );
  }

  // Authentication endpoints
  login(username, password) {
    return this.api.post('/auth/token/', { username, password });
  }

  register(userData) {
    return this.api.post('/auth/users/', userData);
  }

  getCurrentUser() {
    return this.api.get('/auth/users/me/');
  }

  changePassword(oldPassword, newPassword) {
    return this.api.post('/auth/users/change_password/', {
      old_password: oldPassword,
      new_password: newPassword,
    });
  }

  // Missing persons endpoints
  getMissingPersons(params = {}) {
    return this.api.get('/facial-recognition/missing-persons/', { params });
  }

  createMissingPerson(data) {
    return this.api.post('/facial-recognition/missing-persons/', data);
  }

  getMissingPerson(id) {
    return this.api.get(`/facial-recognition/missing-persons/${id}/`);
  }

  uploadImage(missingPersonId, imageFile, priority = 'normal') {
    const formData = new FormData();
    formData.append('image', imageFile);
    formData.append('priority', priority);

    return this.api.post(
      `/facial-recognition/missing-persons/${missingPersonId}/upload_image/`,
      formData,
      {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      }
    );
  }

  searchFacialRecognition(imageFile) {
    const formData = new FormData();
    formData.append('image', imageFile);

    return this.api.post(
      '/facial-recognition/search/',
      formData,
      {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      }
    );
  }

  // Facial match endpoints
  getMatches(params = {}) {
    return this.api.get('/facial-recognition/matches/', { params });
  }

  verifyMatch(matchId, notes = '') {
    return this.api.post(`/facial-recognition/matches/${matchId}/verify/`, { notes });
  }

  rejectMatch(matchId, notes = '') {
    return this.api.post(`/facial-recognition/matches/${matchId}/reject/`, { notes });
  }

  // Processing queue endpoints
  getProcessingQueue(params = {}) {
    return this.api.get('/facial-recognition/processing-queue/', { params });
  }

  // Notifications endpoints
  getNotifications(params = {}) {
    return this.api.get('/notifications/notifications/', { params });
  }

  markNotificationAsRead(notificationId) {
    return this.api.post(`/notifications/notifications/${notificationId}/mark_as_read/`);
  }

  markAllNotificationsAsRead() {
    return this.api.post('/notifications/notifications/mark_all_as_read/');
  }

  getNotificationPreferences() {
    return this.api.get('/notifications/preferences/my_preferences/');
  }

  updateNotificationPreferences(preferences) {
    return this.api.put('/notifications/preferences/my_preferences/', preferences);
  }

  // User management endpoints (for government officials)
  getUsers(params = {}) {
    return this.api.get('/auth/users/', { params });
  }

  verifyUser(userId) {
    return this.api.post(`/auth/users/${userId}/verify/`);
  }

  // Case management endpoints
  updateCaseStatus(caseId, status) {
    return this.api.patch(`/facial-recognition/missing-persons/${caseId}/`, { status });
  }
}

export default new ApiClient();
