import React, { useState, useEffect } from 'react';
import { useAuth } from '../../context/AuthContext';
import Navbar from '../../components/Navbar';
import api from '../../services/api';
import toast from 'react-hot-toast';
import { 
  Chart as ChartJS, 
  CategoryScale, 
  LinearScale, 
  BarElement, 
  LineElement,
  PointElement,
  Title, 
  Tooltip, 
  Legend,
  ArcElement 
} from 'chart.js';
import { Bar, Line, Pie } from 'react-chartjs-2';

ChartJS.register(
  CategoryScale,
  LinearScale,
  BarElement,
  LineElement,
  PointElement,
  Title,
  Tooltip,
  Legend,
  ArcElement
);

const Reports = () => {
  const { user } = useAuth();
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState('quiz');
  const [quizAnalytics, setQuizAnalytics] = useState(null);
  const [userAnalytics, setUserAnalytics] = useState(null);
  const [orgAnalytics, setOrgAnalytics] = useState(null);
  const [recentActivity, setRecentActivity] = useState([]);
  const [dateRange, setDateRange] = useState('30'); // days

  useEffect(() => {
    if (user?.role === 'admin') {
      fetchAllAnalytics();
    }
  }, [user, dateRange]); // eslint-disable-line react-hooks/exhaustive-deps

  const fetchAllAnalytics = async () => {
    try {
      setLoading(true);
      const [quizRes, userRes, orgRes, activityRes] = await Promise.all([
        api.get('/api/admin/analytics/quiz/'),
        api.get('/api/admin/analytics/user/'),
        api.get('/api/admin/analytics/organization/'),
        api.get(`/api/admin/activity/recent/?days=${dateRange}`)
      ]);

      setQuizAnalytics(quizRes.data);
      setUserAnalytics(userRes.data);
      setOrgAnalytics(orgRes.data);
      setRecentActivity(activityRes.data.activities || []);
    } catch (error) {
      console.error('Error fetching analytics:', error);
      toast.error('Failed to load analytics data');
    } finally {
      setLoading(false);
    }
  };

  const exportReport = async (type) => {
    try {
      const response = await api.get(`/api/admin/export/${type}/`, {
        responseType: 'blob'
      });
      
      const blob = new Blob([response.data], { type: 'application/vnd.ms-excel' });
      const url = window.URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = url;
      link.download = `${type}_report_${new Date().toISOString().split('T')[0]}.xlsx`;
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      window.URL.revokeObjectURL(url);
      
      toast.success(`${type} report exported successfully`);
    } catch (error) {
      toast.error(`Failed to export ${type} report`);
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

  // Chart configurations
  const chartOptions = {
    responsive: true,
    plugins: {
      legend: {
        position: 'top',
      },
    },
  };

  const quizActivityData = {
    labels: quizAnalytics?.quiz_activity?.map(item => item.date) || [],
    datasets: [
      {
        label: 'Quiz Attempts',
        data: quizAnalytics?.quiz_activity?.map(item => item.count) || [],
        backgroundColor: 'rgba(59, 130, 246, 0.5)',
        borderColor: 'rgba(59, 130, 246, 1)',
        borderWidth: 1,
      },
    ],
  };

  const difficultyData = {
    labels: quizAnalytics?.difficulty_distribution?.map(item => item.difficulty) || [],
    datasets: [
      {
        label: 'Number of Quizzes',
        data: quizAnalytics?.difficulty_distribution?.map(item => item.count) || [],
        backgroundColor: [
          'rgba(34, 197, 94, 0.8)',
          'rgba(251, 191, 36, 0.8)',
          'rgba(239, 68, 68, 0.8)',
        ],
      },
    ],
  };

  const userRegistrationData = {
    labels: userAnalytics?.registration_trend?.map(item => item.date) || [],
    datasets: [
      {
        label: 'New Registrations',
        data: userAnalytics?.registration_trend?.map(item => item.count) || [],
        borderColor: 'rgba(168, 85, 247, 1)',
        backgroundColor: 'rgba(168, 85, 247, 0.1)',
        tension: 0.1,
      },
    ],
  };

  return (
    <div className="min-h-screen bg-gray-50">
      <Navbar />
      
      <main className="max-w-7xl mx-auto py-6 sm:px-6 lg:px-8">
        <div className="px-4 py-6 sm:px-0">
          {/* Header */}
          <div className="mb-8">
            <div className="flex justify-between items-start">
              <div>
                <h1 className="text-3xl font-bold text-gray-900">Reports & Analytics</h1>
                <p className="mt-2 text-gray-600">Comprehensive system analytics and reporting</p>
              </div>
              <div className="flex items-center space-x-4">
                <select
                  value={dateRange}
                  onChange={(e) => setDateRange(e.target.value)}
                  className="border border-gray-300 rounded-md px-3 py-2 text-sm"
                >
                  <option value="7">Last 7 days</option>
                  <option value="30">Last 30 days</option>
                  <option value="90">Last 90 days</option>
                  <option value="365">Last year</option>
                </select>
                <button
                  onClick={() => fetchAllAnalytics()}
                  className="bg-blue-600 text-white px-4 py-2 rounded-lg text-sm hover:bg-blue-700"
                >
                  Refresh
                </button>
              </div>
            </div>
          </div>

          {/* Tab Navigation */}
          <div className="border-b border-gray-200 mb-6">
            <nav className="-mb-px flex space-x-8">
              {[
                { key: 'quiz', label: 'Quiz Analytics' },
                { key: 'user', label: 'User Analytics' },
                { key: 'organization', label: 'Organization Analytics' },
                { key: 'activity', label: 'Recent Activity' }
              ].map((tab) => (
                <button
                  key={tab.key}
                  onClick={() => setActiveTab(tab.key)}
                  className={`whitespace-nowrap py-2 px-1 border-b-2 font-medium text-sm ${
                    activeTab === tab.key
                      ? 'border-blue-500 text-blue-600'
                      : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                  }`}
                >
                  {tab.label}
                </button>
              ))}
            </nav>
          </div>

          {/* Quiz Analytics Tab */}
          {activeTab === 'quiz' && quizAnalytics && (
            <div className="space-y-6">
              {/* Overview Cards */}
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
                <div className="bg-white p-6 rounded-lg shadow-sm border border-gray-200">
                  <h3 className="text-sm font-medium text-gray-900">Total Quizzes</h3>
                  <p className="text-2xl font-bold text-blue-600">{quizAnalytics.overview.total_quizzes}</p>
                </div>
                <div className="bg-white p-6 rounded-lg shadow-sm border border-gray-200">
                  <h3 className="text-sm font-medium text-gray-900">Active Quizzes</h3>
                  <p className="text-2xl font-bold text-green-600">{quizAnalytics.overview.active_quizzes}</p>
                </div>
                <div className="bg-white p-6 rounded-lg shadow-sm border border-gray-200">
                  <h3 className="text-sm font-medium text-gray-900">Total Attempts</h3>
                  <p className="text-2xl font-bold text-purple-600">{quizAnalytics.overview.total_attempts}</p>
                </div>
                <div className="bg-white p-6 rounded-lg shadow-sm border border-gray-200">
                  <h3 className="text-sm font-medium text-gray-900">Completion Rate</h3>
                  <p className="text-2xl font-bold text-orange-600">{quizAnalytics.overview.completion_rate}%</p>
                </div>
              </div>

              {/* Charts */}
              <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                <div className="bg-white p-6 rounded-lg shadow-sm border border-gray-200">
                  <h3 className="text-lg font-semibold mb-4">Quiz Activity Trend</h3>
                  <Bar data={quizActivityData} options={chartOptions} />
                </div>
                <div className="bg-white p-6 rounded-lg shadow-sm border border-gray-200">
                  <h3 className="text-lg font-semibold mb-4">Quiz Difficulty Distribution</h3>
                  <Pie data={difficultyData} options={chartOptions} />
                </div>
              </div>

              {/* Popular Quizzes */}
              <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
                <div className="flex justify-between items-center mb-4">
                  <h3 className="text-lg font-semibold">Most Popular Quizzes</h3>
                  <button
                    onClick={() => exportReport('quiz')}
                    className="bg-green-600 text-white px-4 py-2 rounded-lg text-sm hover:bg-green-700"
                  >
                    Export Report
                  </button>
                </div>
                <div className="overflow-x-auto">
                  <table className="min-w-full divide-y divide-gray-200">
                    <thead className="bg-gray-50">
                      <tr>
                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Quiz Title</th>
                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Attempts</th>
                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Avg Score</th>
                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Difficulty</th>
                      </tr>
                    </thead>
                    <tbody className="divide-y divide-gray-200">
                      {quizAnalytics.popular_quizzes?.map((quiz, index) => (
                        <tr key={quiz.id}>
                          <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                            {quiz.title}
                          </td>
                          <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                            {quiz.attempt_count}
                          </td>
                          <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                            {quiz.average_score}%
                          </td>
                          <td className="px-6 py-4 whitespace-nowrap">
                            <span className={`inline-flex px-2 py-1 text-xs font-semibold rounded-full ${
                              quiz.difficulty === 'Easy' ? 'bg-green-100 text-green-800' :
                              quiz.difficulty === 'Medium' ? 'bg-yellow-100 text-yellow-800' :
                              'bg-red-100 text-red-800'
                            }`}>
                              {quiz.difficulty}
                            </span>
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </div>
            </div>
          )}

          {/* User Analytics Tab */}
          {activeTab === 'user' && userAnalytics && (
            <div className="space-y-6">
              {/* Overview Cards */}
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
                <div className="bg-white p-6 rounded-lg shadow-sm border border-gray-200">
                  <h3 className="text-sm font-medium text-gray-900">Total Users</h3>
                  <p className="text-2xl font-bold text-blue-600">{userAnalytics.overview.total_users}</p>
                </div>
                <div className="bg-white p-6 rounded-lg shadow-sm border border-gray-200">
                  <h3 className="text-sm font-medium text-gray-900">Active Users</h3>
                  <p className="text-2xl font-bold text-green-600">{userAnalytics.overview.active_users}</p>
                </div>
                <div className="bg-white p-6 rounded-lg shadow-sm border border-gray-200">
                  <h3 className="text-sm font-medium text-gray-900">New This Month</h3>
                  <p className="text-2xl font-bold text-purple-600">{userAnalytics.overview.new_users_this_month}</p>
                </div>
                <div className="bg-white p-6 rounded-lg shadow-sm border border-gray-200">
                  <h3 className="text-sm font-medium text-gray-900">Avg Score</h3>
                  <p className="text-2xl font-bold text-orange-600">{userAnalytics.overview.average_score}%</p>
                </div>
              </div>

              {/* Charts */}
              <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                <div className="bg-white p-6 rounded-lg shadow-sm border border-gray-200">
                  <h3 className="text-lg font-semibold mb-4">User Registration Trend</h3>
                  <Line data={userRegistrationData} options={chartOptions} />
                </div>
                <div className="bg-white p-6 rounded-lg shadow-sm border border-gray-200">
                  <h3 className="text-lg font-semibold mb-4">User Role Distribution</h3>
                  <Pie 
                    data={{
                      labels: userAnalytics.role_distribution?.map(item => item.role) || [],
                      datasets: [{
                        data: userAnalytics.role_distribution?.map(item => item.count) || [],
                        backgroundColor: ['#3B82F6', '#10B981', '#F59E0B', '#EF4444'],
                      }]
                    }} 
                    options={chartOptions} 
                  />
                </div>
              </div>

              {/* Export Button */}
              <div className="flex justify-end">
                <button
                  onClick={() => exportReport('user')}
                  className="bg-green-600 text-white px-4 py-2 rounded-lg text-sm hover:bg-green-700"
                >
                  Export User Report
                </button>
              </div>
            </div>
          )}

          {/* Organization Analytics Tab */}
          {activeTab === 'organization' && orgAnalytics && (
            <div className="space-y-6">
              {/* Overview Cards */}
              <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                <div className="bg-white p-6 rounded-lg shadow-sm border border-gray-200">
                  <h3 className="text-sm font-medium text-gray-900">Total Organizations</h3>
                  <p className="text-2xl font-bold text-blue-600">{orgAnalytics.overview.total_organizations}</p>
                </div>
                <div className="bg-white p-6 rounded-lg shadow-sm border border-gray-200">
                  <h3 className="text-sm font-medium text-gray-900">Active Organizations</h3>
                  <p className="text-2xl font-bold text-green-600">{orgAnalytics.overview.active_organizations}</p>
                </div>
                <div className="bg-white p-6 rounded-lg shadow-sm border border-gray-200">
                  <h3 className="text-sm font-medium text-gray-900">Inactive Organizations</h3>
                  <p className="text-2xl font-bold text-red-600">{orgAnalytics.overview.inactive_organizations}</p>
                </div>
              </div>

              {/* Top Organizations */}
              <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
                <div className="flex justify-between items-center mb-4">
                  <h3 className="text-lg font-semibold">Organizations by User Count</h3>
                  <button
                    onClick={() => exportReport('organization')}
                    className="bg-green-600 text-white px-4 py-2 rounded-lg text-sm hover:bg-green-700"
                  >
                    Export Report
                  </button>
                </div>
                <div className="overflow-x-auto">
                  <table className="min-w-full divide-y divide-gray-200">
                    <thead className="bg-gray-50">
                      <tr>
                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Organization</th>
                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Users</th>
                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Status</th>
                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Created</th>
                      </tr>
                    </thead>
                    <tbody className="divide-y divide-gray-200">
                      {orgAnalytics.top_organizations?.map((org, index) => (
                        <tr key={org.id}>
                          <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                            {org.name}
                          </td>
                          <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                            {org.user_count}
                          </td>
                          <td className="px-6 py-4 whitespace-nowrap">
                            <span className={`inline-flex px-2 py-1 text-xs font-semibold rounded-full ${
                              org.is_active ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'
                            }`}>
                              {org.is_active ? 'Active' : 'Inactive'}
                            </span>
                          </td>
                          <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                            {new Date(org.created_at).toLocaleDateString()}
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </div>
            </div>
          )}

          {/* Recent Activity Tab */}
          {activeTab === 'activity' && (
            <div className="space-y-6">
              <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
                <h3 className="text-lg font-semibold mb-4">Recent System Activity</h3>
                <div className="space-y-4">
                  {recentActivity.map((activity, index) => (
                    <div key={index} className="flex items-start space-x-3 p-3 border border-gray-100 rounded-lg">
                      <span className="text-2xl">{activity.icon}</span>
                      <div className="flex-1">
                        <p className="text-sm text-gray-900">
                          <span className="font-medium">{activity.user}</span> {activity.action}
                        </p>
                        <p className="text-xs text-gray-500 mt-1">{activity.timestamp}</p>
                      </div>
                      {activity.status && (
                        <span className={`px-2 py-1 text-xs rounded-full ${
                          activity.status === 'completed' ? 'bg-green-100 text-green-800' :
                          activity.status === 'in_progress' ? 'bg-yellow-100 text-yellow-800' :
                          'bg-gray-100 text-gray-800'
                        }`}>
                          {activity.status.replace('_', ' ')}
                        </span>
                      )}
                    </div>
                  ))}
                  {recentActivity.length === 0 && (
                    <p className="text-center text-gray-500 py-8">No recent activity found.</p>
                  )}
                </div>
              </div>
            </div>
          )}
        </div>
      </main>
    </div>
  );
};

export default Reports;
