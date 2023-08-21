import React, { useState, useEffect } from 'react';
import { toast } from 'react-hot-toast';
import api from '../services/api';

const TestLogin = () => {
  const [credentials, setCredentials] = useState({
    username: 'instructor1',
    password: 'instructor123'
  });
  const [isLoggedIn, setIsLoggedIn] = useState(false);
  const [userInfo, setUserInfo] = useState(null);

  useEffect(() => {
    // Check if already logged in
    const token = localStorage.getItem('access_token');
    if (token) {
      setIsLoggedIn(true);
      checkUserInfo();
    }
  }, []);

  const checkUserInfo = async () => {
    try {
      const response = await api.get('/api/user/profile/');
      setUserInfo(response.data);
    } catch (error) {
      console.log('Failed to get user info:', error);
    }
  };

  const handleLogin = async (e) => {
    e.preventDefault();
    try {
      const response = await api.post('/api/auth/login/', credentials);
      const { access, refresh, user } = response.data;
      
      localStorage.setItem('access_token', access);
      localStorage.setItem('refresh_token', refresh);
      
      setIsLoggedIn(true);
      setUserInfo(user);
      toast.success('Logged in successfully!');
    } catch (error) {
      console.error('Login error:', error.response?.data);
      toast.error(error.response?.data?.error || 'Login failed');
    }
  };

  const handleLogout = () => {
    localStorage.removeItem('access_token');
    localStorage.removeItem('refresh_token');
    setIsLoggedIn(false);
    setUserInfo(null);
    toast.success('Logged out');
  };

  const testQuizUpdate = async () => {
    try {
      const response = await api.put('/api/quizzes/api/quiz/1/update/', {
        is_active: true
      });
      toast.success('Quiz updated successfully!');
      console.log('Update response:', response.data);
    } catch (error) {
      console.error('Update error:', error.response?.data);
      toast.error(error.response?.data?.error || 'Update failed');
    }
  };

  if (isLoggedIn) {
    return (
      <div className="max-w-md mx-auto mt-10 p-6 bg-white rounded-lg shadow-md">
        <h2 className="text-2xl font-bold mb-4 text-green-600">Logged In</h2>
        {userInfo && (
          <div className="mb-4">
            <p><strong>Username:</strong> {userInfo.username}</p>
            <p><strong>Email:</strong> {userInfo.email}</p>
            <p><strong>Role:</strong> {userInfo.role || 'N/A'}</p>
          </div>
        )}
        <div className="space-y-2">
          <button
            onClick={testQuizUpdate}
            className="w-full bg-blue-500 text-white py-2 px-4 rounded hover:bg-blue-600"
          >
            Test Quiz Update
          </button>
          <button
            onClick={handleLogout}
            className="w-full bg-red-500 text-white py-2 px-4 rounded hover:bg-red-600"
          >
            Logout
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="max-w-md mx-auto mt-10 p-6 bg-white rounded-lg shadow-md">
      <h2 className="text-2xl font-bold mb-4">Test Login</h2>
      <form onSubmit={handleLogin} className="space-y-4">
        <div>
          <label className="block text-sm font-medium text-gray-700">Username</label>
          <input
            type="text"
            value={credentials.username}
            onChange={(e) => setCredentials({...credentials, username: e.target.value})}
            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500"
            required
          />
        </div>
        <div>
          <label className="block text-sm font-medium text-gray-700">Password</label>
          <input
            type="password"
            value={credentials.password}
            onChange={(e) => setCredentials({...credentials, password: e.target.value})}
            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500"
            required
          />
        </div>
        <button
          type="submit"
          className="w-full bg-blue-500 text-white py-2 px-4 rounded hover:bg-blue-600"
        >
          Login
        </button>
      </form>
      <div className="mt-4 p-3 bg-gray-100 rounded text-sm">
        <p><strong>Default credentials:</strong></p>
        <p>Username: instructor1</p>
        <p>Password: instructor123</p>
      </div>
    </div>
  );
};

export default TestLogin;
