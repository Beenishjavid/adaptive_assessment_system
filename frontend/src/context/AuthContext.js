/**
 * Authentication Context for React app
 */
import React, { createContext, useContext, useState, useEffect } from 'react';
import api from '../services/api';
import Cookies from 'js-cookie';

const AuthContext = createContext();

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);
  const [token, setToken] = useState(Cookies.get('access_token'));

  // Configure api defaults
  useEffect(() => {
    if (token) {
      api.defaults.headers.common['Authorization'] = `Bearer ${token}`;
    } else {
      delete api.defaults.headers.common['Authorization'];
    }
  }, [token]);

  // Check authentication status on app load
  useEffect(() => {
    const checkAuth = async () => {
      try {
        if (token) {
          const response = await api.get('/api/auth/profile/');
          setUser(response.data);
        }
      } catch (error) {
        console.error('Auth check failed:', error);
        logout();
      } finally {
        setLoading(false);
      }
    };

    checkAuth();
  }, [token]);

  const login = async (username, password) => {
    try {
      const response = await api.post('/api/auth/api/login/', {
        username,
        password,
      });

      const { access, refresh, user: userData } = response.data;
      
      setToken(access);
      setUser(userData);
      
      // Store tokens in cookies
      Cookies.set('access_token', access, { expires: 1 }); // 1 day
      Cookies.set('refresh_token', refresh, { expires: 7 }); // 7 days
      
      api.defaults.headers.common['Authorization'] = `Bearer ${access}`;
      
      return { success: true };
    } catch (error) {
      return {
        success: false,
        message: error.response?.data?.error || 'Login failed',
      };
    }
  };

  const register = async (userData) => {
    try {
      const response = await api.post('/api/auth/register/', userData);
      return { success: true, data: response.data };
    } catch (error) {
      return {
        success: false,
        message: error.response?.data || 'Registration failed',
      };
    }
  };

  const logout = () => {
    setUser(null);
    setToken(null);
    Cookies.remove('access_token');
    Cookies.remove('refresh_token');
    delete api.defaults.headers.common['Authorization'];
  };

  const updateProfile = async (profileData) => {
    try {
      const response = await api.patch('/api/auth/profile/', profileData);
      setUser(response.data);
      return { success: true, data: response.data };
    } catch (error) {
      return {
        success: false,
        message: error.response?.data || 'Profile update failed',
      };
    }
  };

  const forgotPassword = async (email) => {
    try {
      const response = await api.post('/api/auth/forgot-password/', { email });
      return { success: true, data: response.data };
    } catch (error) {
      return {
        success: false,
        message: error.response?.data?.email?.[0] || error.response?.data?.message || 'Failed to send reset email',
      };
    }
  };

  const resetPassword = async (token, newPassword, confirmPassword) => {
    try {
      const response = await api.post('/api/auth/reset-password/', {
        token,
        new_password: newPassword,
        new_password_confirm: confirmPassword,
      });
      return { success: true, data: response.data };
    } catch (error) {
      return {
        success: false,
        message: error.response?.data?.error || 'Failed to reset password',
      };
    }
  };

  const verifyResetToken = async (token) => {
    try {
      const response = await api.post('/api/auth/verify-reset-token/', { token });
      return { success: true, data: response.data };
    } catch (error) {
      return {
        success: false,
        message: error.response?.data?.error || 'Invalid token',
      };
    }
  };

  const value = {
    user,
    token,
    loading,
    login,
    register,
    logout,
    updateProfile,
    forgotPassword,
    resetPassword,
    verifyResetToken,
    isAuthenticated: !!user && !!token,
    isAdmin: user?.role === 'admin',
    isInstructor: user?.role === 'instructor',
    isStudent: user?.role === 'student',
  };

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  );
};
