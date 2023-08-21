import React, { useState, useEffect } from 'react';
import { useAuth } from '../../context/AuthContext';
import Navbar from '../../components/Navbar';
import api from '../../services/api';

const ReportsAnalytics = () => {
  const { user } = useAuth();
  const [stats, setStats] = useState({
    quiz_stats: {},
    user_stats: {},
    organization_stats: {},
    recent_activity: []
  });
  const [loading, setLoading] = useState(true);
  const [timeRange, setTimeRange] = useState('30'); // days

  const fetchAnalytics = async () => {
    try {
      setLoading(true);
      const [quizStats, userStats, orgStats, activity] = await Promise.all([
        api.get('/api/quizzes/admin/quiz-stats/'),
        api.get('/api/authentication/api/admin/user-stats/'),
        api.get('/api/organizations/admin/organization-stats/'),
        api.get(`/api/admin/recent-activity/?days=${timeRange}`)
      ]);
      
      setStats({
        quiz_stats: quizStats.data,
        user_stats: userStats.data,
        organization_stats: orgStats.data,
        recent_activity: activity.data.activities || []
      });
    } catch (error) {
      console.error('Error fetching analytics:', error);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (user?.role === 'admin') {
      fetchAnalytics();
    }
  }, [user, timeRange]); // eslint-disable-line react-hooks/exhaustive-deps

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

  const StatCard = ({ title, value, subtitle, icon, color = 'blue' }) => {
    const colorClasses = {
      blue: 'bg-blue-50 text-blue-600',
      green: 'bg-green-50 text-green-600',
      purple: 'bg-purple-50 text-purple-600',
      orange: 'bg-orange-50 text-orange-600',
      red: 'bg-red-50 text-red-600'
    };

    return (
      <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
        <div className="flex items-center justify-between">
          <div>
            <p className="text-sm font-medium text-gray-600">{title}</p>
            <p className="text-2xl font-bold text-gray-900 mt-1">{value}</p>
            {subtitle && <p className="text-xs text-gray-500 mt-1">{subtitle}</p>}
          </div>
          <div className={`p-3 rounded-full ${colorClasses[color]}`}>
            <span className="text-2xl">{icon}</span>
          </div>
        </div>
      </div>
    );
  };

  const LoadingSkeleton = () => (
    <div className="animate-pulse">
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
        {[1, 2, 3, 4].map((i) => (
          <div key={i} className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
            <div className="h-4 bg-gray-200 rounded w-24 mb-2"></div>
            <div className="h-8 bg-gray-200 rounded w-16 mb-1"></div>
            <div className="h-3 bg-gray-200 rounded w-20"></div>
          </div>
        ))}
      </div>
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
          <div className="h-6 bg-gray-200 rounded w-32 mb-4"></div>
          <div className="space-y-3">
            {[1, 2, 3, 4, 5].map((i) => (
              <div key={i} className="h-4 bg-gray-200 rounded"></div>
            ))}
          </div>
        </div>
        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
          <div className="h-6 bg-gray-200 rounded w-32 mb-4"></div>
          <div className="space-y-3">
            {[1, 2, 3, 4, 5].map((i) => (
              <div key={i} className="h-4 bg-gray-200 rounded"></div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );

  return (
    <div className="min-h-screen bg-gray-50">
      <Navbar />
      
      <main className="max-w-7xl mx-auto py-6 sm:px-6 lg:px-8">
        <div className="px-4 py-6 sm:px-0">
          {/* Header */}
          <div className="flex justify-between items-center mb-8">
            <div>
              <h1 className="text-3xl font-bold text-gray-900">Reports & Analytics</h1>
              <p className="mt-2 text-gray-600">System performance and usage insights</p>
            </div>
            <div className="flex items-center space-x-4">
              <label className="text-sm font-medium text-gray-700">Time Range:</label>
              <select
                value={timeRange}
                onChange={(e) => setTimeRange(e.target.value)}
                className="border border-gray-300 rounded-md px-3 py-2 text-sm"
              >
                <option value="7">Last 7 days</option>
                <option value="30">Last 30 days</option>
                <option value="90">Last 90 days</option>
                <option value="365">Last year</option>
              </select>
              <button
                onClick={fetchAnalytics}
                className="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 transition-colors text-sm"
              >
                Refresh
              </button>
            </div>
          </div>

          {loading ? (
            <LoadingSkeleton />
          ) : (
            <>
              {/* Overview Stats */}
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
                <StatCard
                  title="Total Quizzes"
                  value={stats.quiz_stats.total_quizzes || 0}
                  subtitle="Active quizzes"
                  icon="📊"
                  color="blue"
                />
                <StatCard
                  title="Total Users"
                  value={stats.user_stats.total_users || 0}
                  subtitle={`${stats.user_stats.active_users || 0} active`}
                  icon="👥"
                  color="green"
                />
                <StatCard
                  title="Organizations"
                  value={stats.organization_stats.total_organizations || 0}
                  subtitle={`${stats.organization_stats.active_organizations || 0} active`}
                  icon="🏢"
                  color="purple"
                />
                <StatCard
                  title="Recent Activity"
                  value={stats.recent_activity.length || 0}
                  subtitle={`Last ${timeRange} days`}
                  icon="⚡"
                  color="orange"
                />
              </div>

              <div className="grid grid-cols-1 lg:grid-cols-2 gap-8 mb-8">
                {/* User Role Distribution */}
                <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
                  <h3 className="text-lg font-semibold text-gray-900 mb-4">User Distribution by Role</h3>
                  <div className="space-y-4">
                    {stats.user_stats.role_distribution && Object.entries(stats.user_stats.role_distribution).map(([role, count]) => (
                      <div key={role} className="flex items-center justify-between">
                        <div className="flex items-center">
                          <span className={`inline-block w-3 h-3 rounded-full mr-3 ${
                            role === 'admin' ? 'bg-red-500' :
                            role === 'instructor' ? 'bg-blue-500' : 'bg-green-500'
                          }`}></span>
                          <span className="text-sm font-medium text-gray-700 capitalize">{role}</span>
                        </div>
                        <span className="text-sm text-gray-900 font-semibold">{count}</span>
                      </div>
                    ))}
                  </div>
                </div>

                {/* Top Organizations */}
                <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
                  <h3 className="text-lg font-semibold text-gray-900 mb-4">Top Organizations by Users</h3>
                  <div className="space-y-4">
                    {stats.organization_stats.top_organizations?.slice(0, 5).map((org, index) => (
                      <div key={index} className="flex items-center justify-between">
                        <div className="flex items-center">
                          <span className="flex w-6 h-6 rounded-full bg-gray-200 text-gray-600 text-xs items-center justify-center mr-3">
                            {index + 1}
                          </span>
                          <div>
                            <span className="text-sm font-medium text-gray-700">{org.name}</span>
                            <span className={`ml-2 inline-flex px-2 py-1 text-xs font-semibold rounded-full ${
                              org.is_active ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'
                            }`}>
                              {org.is_active ? 'Active' : 'Inactive'}
                            </span>
                          </div>
                        </div>
                        <span className="text-sm text-gray-900 font-semibold">{org.user_count} users</span>
                      </div>
                    )) || (
                      <p className="text-gray-500 text-sm">No organization data available</p>
                    )}
                  </div>
                </div>
              </div>

              {/* Recent Activity */}
              <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
                <h3 className="text-lg font-semibold text-gray-900 mb-4">Recent System Activity</h3>
                {stats.recent_activity.length > 0 ? (
                  <div className="space-y-4">
                    {stats.recent_activity.slice(0, 10).map((activity, index) => (
                      <div key={index} className="flex items-start space-x-3 p-3 bg-gray-50 rounded-lg">
                        <div className="flex-shrink-0">
                          <span className="flex w-8 h-8 rounded-full bg-blue-100 text-blue-600 text-sm items-center justify-center">
                            {activity.icon || '📋'}
                          </span>
                        </div>
                        <div className="flex-1 min-w-0">
                          <p className="text-sm text-gray-900">
                            <span className="font-medium">{activity.user}</span> {activity.action}
                          </p>
                          <p className="text-xs text-gray-500">{activity.timestamp}</p>
                        </div>
                        {activity.status && (
                          <span className={`inline-flex px-2 py-1 text-xs font-semibold rounded-full ${
                            activity.status === 'success' ? 'bg-green-100 text-green-800' :
                            activity.status === 'warning' ? 'bg-yellow-100 text-yellow-800' :
                            'bg-red-100 text-red-800'
                          }`}>
                            {activity.status}
                          </span>
                        )}
                      </div>
                    ))}
                  </div>
                ) : (
                  <div className="text-center py-8">
                    <p className="text-gray-500">No recent activity to display</p>
                  </div>
                )}
              </div>

              {/* Export Options */}
              <div className="mt-8 bg-white rounded-lg shadow-sm border border-gray-200 p-6">
                <h3 className="text-lg font-semibold text-gray-900 mb-4">Export Reports</h3>
                <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                  <button className="flex items-center justify-center px-4 py-3 border border-gray-300 rounded-lg hover:bg-gray-50 transition-colors">
                    <span className="mr-2">📊</span>
                    <span className="text-sm font-medium">Quiz Analytics</span>
                  </button>
                  <button className="flex items-center justify-center px-4 py-3 border border-gray-300 rounded-lg hover:bg-gray-50 transition-colors">
                    <span className="mr-2">👥</span>
                    <span className="text-sm font-medium">User Report</span>
                  </button>
                  <button className="flex items-center justify-center px-4 py-3 border border-gray-300 rounded-lg hover:bg-gray-50 transition-colors">
                    <span className="mr-2">🏢</span>
                    <span className="text-sm font-medium">Organization Report</span>
                  </button>
                </div>
              </div>
            </>
          )}
        </div>
      </main>
    </div>
  );
};

export default ReportsAnalytics;
