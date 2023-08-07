/**
 * Authentication Service
 */
import api from './api';

export const authService = {
  // Login user
  async login(credentials) {
    try {
      const response = await api.post('/api/auth/api/login/', credentials);
      
      // Store tokens in localStorage
      localStorage.setItem('access_token', response.data.access);
      localStorage.setItem('refresh_token', response.data.refresh);
      localStorage.setItem('user', JSON.stringify(response.data.user));
      
      return response.data;
    } catch (error) {
      throw error;
    }
  },

  // Logout user
  async logout() {
    try {
      const refreshToken = localStorage.getItem('refresh_token');
      
      if (refreshToken) {
        await api.post('/api/auth/api/logout/', {
          refresh_token: refreshToken
        });
      }
    } catch (error) {
      // Ignore logout errors
      console.error('Logout error:', error);
    } finally {
      // Always clear localStorage
      localStorage.removeItem('access_token');
      localStorage.removeItem('refresh_token');
      localStorage.removeItem('user');
    }
  },

  // Refresh access token
  async refreshToken() {
    try {
      const refreshToken = localStorage.getItem('refresh_token');
      
      if (!refreshToken) {
        throw new Error('No refresh token found');
      }

      const response = await api.post('/api/auth/api/refresh/', {
        refresh: refreshToken
      });

      localStorage.setItem('access_token', response.data.access);
      return response.data.access;
    } catch (error) {
      // If refresh fails, logout user
      this.logout();
      throw error;
    }
  },

  // Get current user from localStorage
  getCurrentUser() {
    try {
      const userStr = localStorage.getItem('user');
      return userStr ? JSON.parse(userStr) : null;
    } catch (error) {
      console.error('Error parsing user data:', error);
      return null;
    }
  },

  // Check if user is authenticated
  isAuthenticated() {
    const token = localStorage.getItem('access_token');
    const user = this.getCurrentUser();
    return !!(token && user);
  },

  // Get access token
  getAccessToken() {
    return localStorage.getItem('access_token');
  },

  // Get refresh token
  getRefreshToken() {
    return localStorage.getItem('refresh_token');
  }
};

export default authService;
