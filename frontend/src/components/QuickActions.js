import React from 'react';
import { useAuth } from '../context/AuthContext';
import { useNavigate } from 'react-router-dom';

const QuickActions = () => {
  const { user } = useAuth();
  const navigate = useNavigate();

  const getActions = () => {
    if (user?.role === 'admin') {
      return [
        {
          title: 'Manage Users',
          description: 'Add, edit, or remove users',
          icon: '👥',
          color: 'blue',
          action: () => navigate('/admin/users'),
        },
        {
          title: 'System Settings',
          description: 'Configure platform settings',
          icon: '⚙️',
          color: 'gray',
          action: () => navigate('/admin/settings'),
        },
        {
          title: 'View Reports',
          description: 'Access analytics and reports',
          icon: '📊',
          color: 'purple',
          action: () => navigate('/admin/reports'),
        },
        {
          title: 'Manage Organizations',
          description: 'Add or modify organizations',
          icon: '🏢',
          color: 'green',
          action: () => navigate('/admin/organizations'),
        },
      ];
    } else if (user?.role === 'instructor') {
      return [
        {
          title: 'Create Quiz',
          description: 'Design a new assessment',
          icon: '➕',
          color: 'blue',
          action: () => navigate('/create-quiz'),
        },
        {
          title: 'My Quizzes',
          description: 'Manage existing quizzes',
          icon: '📝',
          color: 'green',
          action: () => navigate('/my-quizzes'),
        },
        {
          title: 'Student Results',
          description: 'Review quiz submissions',
          icon: '📊',
          color: 'purple',
          action: () => navigate('/student-results'),
        },
        {
          title: 'Create Group',
          description: 'Set up a new study group',
          icon: '👥',
          color: 'indigo',
          action: () => navigate('/groups'),
        },
      ];
    } else {
      return [
        {
          title: 'Take Quiz',
          description: 'Start a new assessment',
          icon: '🎯',
          color: 'blue',
          action: () => navigate('/available-quizzes'),
        },
        {
          title: 'My Results',
          description: 'View your quiz history',
          icon: '📈',
          color: 'green',
          action: () => navigate('/my-results'),
        },
        {
          title: 'My Groups',
          description: 'View and manage your groups',
          icon: '👥',
          color: 'purple',
          action: () => navigate('/groups'),
        },
        {
          title: 'Search Topics',
          description: 'Find quizzes by topic',
          icon: '🔍',
          color: 'indigo',
          action: () => navigate('/topic-search'),
        },
      ];
    }
  };

  const getColorClasses = (color) => {
    const colors = {
      blue: 'bg-blue-500 hover:bg-blue-600',
      green: 'bg-green-500 hover:bg-green-600',
      purple: 'bg-purple-500 hover:bg-purple-600',
      indigo: 'bg-indigo-500 hover:bg-indigo-600',
      gray: 'bg-gray-500 hover:bg-gray-600',
    };
    return colors[color] || colors.blue;
  };

  return (
    <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
      <h3 className="text-lg font-semibold text-gray-900 mb-4">Quick Actions</h3>
      <div className="space-y-3">
        {getActions().map((action, index) => (
          <button
            key={index}
            onClick={action.action}
            className="w-full text-left p-4 rounded-lg border border-gray-200 hover:border-gray-300 transition-colors duration-200 group"
          >
            <div className="flex items-start space-x-3">
              <div className={`flex-shrink-0 w-8 h-8 rounded-lg flex items-center justify-center text-white ${getColorClasses(action.color)}`}>
                <span className="text-sm">{action.icon}</span>
              </div>
              <div className="flex-1 min-w-0">
                <p className="text-sm font-medium text-gray-900 group-hover:text-primary-600">
                  {action.title}
                </p>
                <p className="text-xs text-gray-500 mt-1">{action.description}</p>
              </div>
              <div className="flex-shrink-0">
                <svg
                  className="w-4 h-4 text-gray-400 group-hover:text-primary-600"
                  fill="none"
                  stroke="currentColor"
                  viewBox="0 0 24 24"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M9 5l7 7-7 7"
                  />
                </svg>
              </div>
            </div>
          </button>
        ))}
      </div>
    </div>
  );
};

export default QuickActions;
