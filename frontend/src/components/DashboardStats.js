import React, { useState, useEffect } from 'react';
import { useAuth } from '../context/AuthContext';
import api from '../services/api';

const DashboardStats = () => {
  const { user } = useAuth();
  const [stats, setStats] = useState({
    totalQuizzes: 0,
    totalAttempts: 0,
    averageScore: 0,
    activeUsers: 0,
  });
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchStats = async () => {
      try {
        setLoading(true);
        let response;
        
        if (user?.role === 'admin') {
          // Fetch admin dashboard stats
          response = await api.get('/api/quizzes/api/dashboard/stats/');
          setStats({
            totalQuizzes: response.data.total_quizzes || 0,
            totalAttempts: response.data.total_students || 0,
            averageScore: response.data.total_questions || 0,
            activeUsers: response.data.active_users || 0,
          });
        } else if (user?.role === 'instructor') {
          // Fetch instructor stats
          const [quizzesRes, attemptsRes] = await Promise.all([
            api.get('/api/quizzes/api/quiz/my-quizzes/'),
            api.get('/api/quizzes/api/instructor/stats/')
          ]);
          
          setStats({
            totalQuizzes: quizzesRes.data.quizzes?.length || 0,
            totalAttempts: attemptsRes.data?.total_attempts || 0,
            averageScore: attemptsRes.data?.average_score || 0,
            activeUsers: attemptsRes.data?.active_students || 0,
          });
        } else {
          // Fetch student stats
          const [quizzesRes, resultsRes] = await Promise.all([
            api.get('/api/quizzes/all/'),
            api.get('/api/quizzes/api/my-results/')
          ]);
          
          const attempts = resultsRes.data.attempts || [];
          const totalScore = attempts.reduce((sum, attempt) => sum + (attempt.score || 0), 0);
          const avgScore = attempts.length > 0 ? totalScore / attempts.length : 0;
          
          setStats({
            totalQuizzes: quizzesRes.data.quizzes?.length || 0,
            totalAttempts: attempts.length,
            averageScore: Math.round(avgScore * 100) / 100,
            activeUsers: 1,
          });
        }
      } catch (error) {
        console.error('Error fetching dashboard stats:', error);
        // Fallback to mock data on error
        const mockStats = {
          admin: { totalQuizzes: 0, totalAttempts: 0, averageScore: 0, activeUsers: 0 },
          instructor: { totalQuizzes: 0, totalAttempts: 0, averageScore: 0, activeUsers: 0 },
          student: { totalQuizzes: 0, totalAttempts: 0, averageScore: 0, activeUsers: 1 },
        };
        setStats(mockStats[user?.role] || mockStats.student);
      } finally {
        setLoading(false);
      }
    };

    if (user) {
      fetchStats();
    }
  }, [user]);

  const getStatCards = () => {
    if (user?.role === 'admin') {
      return [
        {
          title: 'Total Quizzes',
          value: stats.totalQuizzes,
          icon: '📊',
          color: 'blue',
          description: 'System-wide quizzes',
        },
        {
          title: 'Total Attempts',
          value: stats.totalAttempts.toLocaleString(),
          icon: '🎯',
          color: 'green',
          description: 'All quiz attempts',
        },
        {
          title: 'Average Score',
          value: `${stats.averageScore}%`,
          icon: '📈',
          color: 'purple',
          description: 'Platform average',
        },
        {
          title: 'Active Users',
          value: stats.activeUsers,
          icon: '👥',
          color: 'indigo',
          description: 'This month',
        },
      ];
    } else if (user?.role === 'instructor') {
      return [
        {
          title: 'My Quizzes',
          value: stats.totalQuizzes,
          icon: '📝',
          color: 'blue',
          description: 'Created by you',
        },
        {
          title: 'Student Attempts',
          value: stats.totalAttempts,
          icon: '🎯',
          color: 'green',
          description: 'Total submissions',
        },
        {
          title: 'Class Average',
          value: `${stats.averageScore}%`,
          icon: '📊',
          color: 'purple',
          description: 'Your students',
        },
        {
          title: 'Active Students',
          value: stats.activeUsers,
          icon: '🎓',
          color: 'indigo',
          description: 'This month',
        },
      ];
    } else {
      return [
        {
          title: 'Available Quizzes',
          value: stats.totalQuizzes,
          icon: '📚',
          color: 'blue',
          description: 'Ready to take',
        },
        {
          title: 'Quiz Attempts',
          value: stats.totalAttempts,
          icon: '✍️',
          color: 'green',
          description: 'Your submissions',
        },
        {
          title: 'Your Average',
          value: `${stats.averageScore}%`,
          icon: '🌟',
          color: 'purple',
          description: 'Keep improving!',
        },
        {
          title: 'Rank',
          value: '#12',
          icon: '🏆',
          color: 'indigo',
          description: 'In your class',
        },
      ];
    }
  };

  const getColorClasses = (color) => {
    const colors = {
      blue: 'bg-blue-50 text-blue-600',
      green: 'bg-green-50 text-green-600',
      purple: 'bg-purple-50 text-purple-600',
      indigo: 'bg-indigo-50 text-indigo-600',
    };
    return colors[color] || colors.blue;
  };

  if (loading) {
    return (
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        {[1, 2, 3, 4].map((index) => (
          <div key={index} className="bg-white rounded-lg shadow-sm border border-gray-200 p-6 animate-pulse">
            <div className="flex items-center justify-between">
              <div className="flex-1">
                <div className="h-4 bg-gray-200 rounded w-24 mb-2"></div>
                <div className="h-8 bg-gray-200 rounded w-16 mb-1"></div>
                <div className="h-3 bg-gray-200 rounded w-20"></div>
              </div>
              <div className="w-12 h-12 bg-gray-200 rounded-full"></div>
            </div>
          </div>
        ))}
      </div>
    );
  }

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
      {getStatCards().map((stat, index) => (
        <div key={index} className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">{stat.title}</p>
              <p className="text-2xl font-bold text-gray-900 mt-1">{stat.value}</p>
              <p className="text-xs text-gray-500 mt-1">{stat.description}</p>
            </div>
            <div className={`p-3 rounded-full text-2xl ${getColorClasses(stat.color)}`}>
              {stat.icon}
            </div>
          </div>
        </div>
      ))}
    </div>
  );
};

export default DashboardStats;
