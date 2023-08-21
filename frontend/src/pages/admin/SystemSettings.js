import React, { useState, useEffect } from 'react';
import { useAuth } from '../../context/AuthContext';
import Navbar from '../../components/Navbar';
import api from '../../services/api';
import toast from 'react-hot-toast';

const SystemSettings = () => {
  const { user } = useAuth();
  const [settings, setSettings] = useState({
    site_name: 'Smart Quiz System',
    site_description: 'Advanced Quiz Management Platform',
    max_quiz_time: 180, // minutes
    max_questions_per_quiz: 100,
    allow_guest_access: false,
    enable_notifications: true,
    quiz_auto_save_interval: 30, // seconds
    session_timeout: 30, // minutes
    max_login_attempts: 5,
    password_min_length: 8,
    require_email_verification: true,
    enable_proctoring: true,
    backup_frequency: 'daily',
    log_retention_days: 90,
    maintenance_mode: false,
    debug_mode: false
  });
  
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [backupLoading, setBackupLoading] = useState(false);

  useEffect(() => {
    if (user?.role === 'admin') {
      fetchSettings();
    }
  }, [user]); // eslint-disable-line react-hooks/exhaustive-deps

  const fetchSettings = async () => {
    try {
      setLoading(true);
      const response = await api.get('/api/admin/settings/system/');
      setSettings({ ...settings, ...response.data.settings });
    } catch (error) {
      console.error('Error fetching settings:', error);
      toast.error('Failed to load system settings');
    } finally {
      setLoading(false);
    }
  };

  const handleSave = async (e) => {
    e.preventDefault();
    try {
      setSaving(true);
      await api.put('/api/admin/settings/system/update/', { settings });
      toast.success('Settings saved successfully');
    } catch (error) {
      console.error('Error saving settings:', error);
      toast.error('Failed to save settings');
    } finally {
      setSaving(false);
    }
  };

  const handleBackup = async () => {
    try {
      setBackupLoading(true);
      const response = await api.post('/api/admin/system/backup/');
      toast.success('Database backup created successfully');
      
      // Download the backup file
      if (response.data.download_url) {
        window.open(response.data.download_url, '_blank');
      }
    } catch (error) {
      console.error('Error creating backup:', error);
      toast.error('Failed to create backup');
    } finally {
      setBackupLoading(false);
    }
  };

  const handleSystemInfo = async () => {
    try {
      const response = await api.get('/api/admin/system/info/');
      const info = response.data;
      
      const infoText = `
System Information:
==================
Django Version: ${info.django_version}
Python Version: ${info.python_version}
Database: ${info.database_info}
Server Time: ${info.server_time}
Disk Usage: ${info.disk_usage}
Memory Usage: ${info.memory_usage}
Active Users: ${info.active_users}
Total Quizzes: ${info.total_quizzes}
Uptime: ${info.uptime}
      `.trim();
      
      alert(infoText);
    } catch (error) {
      toast.error('Failed to fetch system information');
    }
  };

  const handleClearCache = async () => {
    if (!window.confirm('Are you sure you want to clear the system cache?')) return;
    
    try {
      await api.post('/api/admin/system/cache/clear/');
      toast.success('Cache cleared successfully');
    } catch (error) {
      toast.error('Failed to clear cache');
    }
  };

  if (user?.role !== 'admin') {
    return (
      <div className="min-h-screen bg-gray-50">
        <Navbar />
        <div className="max-w-7xl mx-auto py-6 sm:px-6 lg:px-8">
          <div className="text-center">
            <h1 className="text-2xl font-bold text-gray-900">Access Denied</h1>
            <p className="mt-2 text-gray-600">You don't have permission to access this page.</p>
          </div>
        </div>
      </div>
    );
  }

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50">
        <Navbar />
        <div className="max-w-7xl mx-auto py-6 sm:px-6 lg:px-8">
          <div className="flex items-center justify-center h-64">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <Navbar />
      
      <main className="max-w-7xl mx-auto py-6 sm:px-6 lg:px-8">
        <div className="px-4 py-6 sm:px-0">
          {/* Header */}
          <div className="mb-8">
            <h1 className="text-3xl font-bold text-gray-900">System Settings</h1>
            <p className="mt-2 text-gray-600">Configure system-wide settings and preferences</p>
          </div>

          <form onSubmit={handleSave} className="space-y-8">
            {/* General Settings */}
            <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
              <h3 className="text-lg font-semibold text-gray-900 mb-4">General Settings</h3>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div>
                  <label className="block text-sm font-medium text-gray-700">Site Name</label>
                  <input
                    type="text"
                    value={settings.site_name}
                    onChange={(e) => setSettings({...settings, site_name: e.target.value})}
                    className="mt-1 block w-full border border-gray-300 rounded-md px-3 py-2"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700">Site Description</label>
                  <input
                    type="text"
                    value={settings.site_description}
                    onChange={(e) => setSettings({...settings, site_description: e.target.value})}
                    className="mt-1 block w-full border border-gray-300 rounded-md px-3 py-2"
                  />
                </div>
              </div>
            </div>

            {/* Quiz Settings */}
            <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
              <h3 className="text-lg font-semibold text-gray-900 mb-4">Quiz Settings</h3>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div>
                  <label className="block text-sm font-medium text-gray-700">Max Quiz Time (minutes)</label>
                  <input
                    type="number"
                    min="1"
                    max="1440"
                    value={settings.max_quiz_time}
                    onChange={(e) => setSettings({...settings, max_quiz_time: parseInt(e.target.value)})}
                    className="mt-1 block w-full border border-gray-300 rounded-md px-3 py-2"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700">Max Questions per Quiz</label>
                  <input
                    type="number"
                    min="1"
                    max="500"
                    value={settings.max_questions_per_quiz}
                    onChange={(e) => setSettings({...settings, max_questions_per_quiz: parseInt(e.target.value)})}
                    className="mt-1 block w-full border border-gray-300 rounded-md px-3 py-2"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700">Auto-save Interval (seconds)</label>
                  <input
                    type="number"
                    min="10"
                    max="300"
                    value={settings.quiz_auto_save_interval}
                    onChange={(e) => setSettings({...settings, quiz_auto_save_interval: parseInt(e.target.value)})}
                    className="mt-1 block w-full border border-gray-300 rounded-md px-3 py-2"
                  />
                </div>
              </div>
            </div>

            {/* Security Settings */}
            <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
              <h3 className="text-lg font-semibold text-gray-900 mb-4">Security Settings</h3>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div>
                  <label className="block text-sm font-medium text-gray-700">Session Timeout (minutes)</label>
                  <input
                    type="number"
                    min="5"
                    max="480"
                    value={settings.session_timeout}
                    onChange={(e) => setSettings({...settings, session_timeout: parseInt(e.target.value)})}
                    className="mt-1 block w-full border border-gray-300 rounded-md px-3 py-2"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700">Max Login Attempts</label>
                  <input
                    type="number"
                    min="3"
                    max="10"
                    value={settings.max_login_attempts}
                    onChange={(e) => setSettings({...settings, max_login_attempts: parseInt(e.target.value)})}
                    className="mt-1 block w-full border border-gray-300 rounded-md px-3 py-2"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700">Minimum Password Length</label>
                  <input
                    type="number"
                    min="6"
                    max="20"
                    value={settings.password_min_length}
                    onChange={(e) => setSettings({...settings, password_min_length: parseInt(e.target.value)})}
                    className="mt-1 block w-full border border-gray-300 rounded-md px-3 py-2"
                  />
                </div>
              </div>
            </div>

            {/* Feature Toggles */}
            <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
              <h3 className="text-lg font-semibold text-gray-900 mb-4">Feature Settings</h3>
              <div className="space-y-4">
                <label className="flex items-center">
                  <input
                    type="checkbox"
                    checked={settings.allow_guest_access}
                    onChange={(e) => setSettings({...settings, allow_guest_access: e.target.checked})}
                    className="rounded border-gray-300 text-blue-600 shadow-sm focus:border-blue-300 focus:ring focus:ring-blue-200 focus:ring-opacity-50"
                  />
                  <span className="ml-2 text-sm text-gray-700">Allow Guest Access</span>
                </label>
                <label className="flex items-center">
                  <input
                    type="checkbox"
                    checked={settings.enable_notifications}
                    onChange={(e) => setSettings({...settings, enable_notifications: e.target.checked})}
                    className="rounded border-gray-300 text-blue-600 shadow-sm focus:border-blue-300 focus:ring focus:ring-blue-200 focus:ring-opacity-50"
                  />
                  <span className="ml-2 text-sm text-gray-700">Enable Notifications</span>
                </label>
                <label className="flex items-center">
                  <input
                    type="checkbox"
                    checked={settings.require_email_verification}
                    onChange={(e) => setSettings({...settings, require_email_verification: e.target.checked})}
                    className="rounded border-gray-300 text-blue-600 shadow-sm focus:border-blue-300 focus:ring focus:ring-blue-200 focus:ring-opacity-50"
                  />
                  <span className="ml-2 text-sm text-gray-700">Require Email Verification</span>
                </label>
                <label className="flex items-center">
                  <input
                    type="checkbox"
                    checked={settings.enable_proctoring}
                    onChange={(e) => setSettings({...settings, enable_proctoring: e.target.checked})}
                    className="rounded border-gray-300 text-blue-600 shadow-sm focus:border-blue-300 focus:ring focus:ring-blue-200 focus:ring-opacity-50"
                  />
                  <span className="ml-2 text-sm text-gray-700">Enable Proctoring</span>
                </label>
              </div>
            </div>

            {/* System Maintenance */}
            <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
              <h3 className="text-lg font-semibold text-gray-900 mb-4">System Maintenance</h3>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div>
                  <label className="block text-sm font-medium text-gray-700">Backup Frequency</label>
                  <select
                    value={settings.backup_frequency}
                    onChange={(e) => setSettings({...settings, backup_frequency: e.target.value})}
                    className="mt-1 block w-full border border-gray-300 rounded-md px-3 py-2"
                  >
                    <option value="hourly">Hourly</option>
                    <option value="daily">Daily</option>
                    <option value="weekly">Weekly</option>
                    <option value="monthly">Monthly</option>
                  </select>
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700">Log Retention (days)</label>
                  <input
                    type="number"
                    min="7"
                    max="365"
                    value={settings.log_retention_days}
                    onChange={(e) => setSettings({...settings, log_retention_days: parseInt(e.target.value)})}
                    className="mt-1 block w-full border border-gray-300 rounded-md px-3 py-2"
                  />
                </div>
              </div>
              
              <div className="mt-4 space-y-4">
                <label className="flex items-center">
                  <input
                    type="checkbox"
                    checked={settings.maintenance_mode}
                    onChange={(e) => setSettings({...settings, maintenance_mode: e.target.checked})}
                    className="rounded border-gray-300 text-blue-600 shadow-sm focus:border-blue-300 focus:ring focus:ring-blue-200 focus:ring-opacity-50"
                  />
                  <span className="ml-2 text-sm text-gray-700">Maintenance Mode</span>
                  <span className="ml-2 text-xs text-gray-500">(Disables user access)</span>
                </label>
                <label className="flex items-center">
                  <input
                    type="checkbox"
                    checked={settings.debug_mode}
                    onChange={(e) => setSettings({...settings, debug_mode: e.target.checked})}
                    className="rounded border-gray-300 text-blue-600 shadow-sm focus:border-blue-300 focus:ring focus:ring-blue-200 focus:ring-opacity-50"
                  />
                  <span className="ml-2 text-sm text-gray-700">Debug Mode</span>
                  <span className="ml-2 text-xs text-gray-500">(Shows detailed error messages)</span>
                </label>
              </div>
            </div>

            {/* Action Buttons */}
            <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center space-y-4 sm:space-y-0 space-x-0 sm:space-x-4">
              <div className="flex flex-wrap gap-2">
                <button
                  type="button"
                  onClick={handleBackup}
                  disabled={backupLoading}
                  className="bg-green-600 text-white px-4 py-2 rounded-lg hover:bg-green-700 transition-colors disabled:opacity-50"
                >
                  {backupLoading ? 'Creating...' : 'Create Backup'}
                </button>
                <button
                  type="button"
                  onClick={handleSystemInfo}
                  className="bg-gray-600 text-white px-4 py-2 rounded-lg hover:bg-gray-700 transition-colors"
                >
                  System Info
                </button>
                <button
                  type="button"
                  onClick={handleClearCache}
                  className="bg-orange-600 text-white px-4 py-2 rounded-lg hover:bg-orange-700 transition-colors"
                >
                  Clear Cache
                </button>
              </div>
              
              <button
                type="submit"
                disabled={saving}
                className="bg-blue-600 text-white px-6 py-2 rounded-lg hover:bg-blue-700 transition-colors disabled:opacity-50 flex items-center"
              >
                {saving ? (
                  <>
                    <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2"></div>
                    Saving...
                  </>
                ) : (
                  'Save Settings'
                )}
              </button>
            </div>
          </form>
        </div>
      </main>
    </div>
  );
};

export default SystemSettings;
