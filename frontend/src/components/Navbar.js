import React from 'react';
import { useAuth } from '../context/AuthContext';
import { useNavigate, useLocation } from 'react-router-dom';

const Navbar = () => {
  const { user, logout } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  const navigationItems = [
    { name: 'Dashboard', path: '/dashboard', roles: ['admin', 'instructor', 'student'] },
    { name: 'Available Quizzes', path: '/available-quizzes', roles: ['student'] },
    { name: 'Create Quiz', path: '/create-quiz', roles: ['instructor', 'admin'] },
    { name: 'My Quizzes', path: '/my-quizzes', roles: ['instructor', 'admin'] },
    { name: 'My Results', path: '/my-results', roles: ['student'] },
    { name: 'Groups', path: '/groups', roles: ['admin', 'instructor', 'student'] },
    { name: 'Topic Search', path: '/topic-search', roles: ['student'] },
  ];

  // Filter navigation items based on user role
  const getNavigationItems = () => {
    return navigationItems.filter(item => item.roles.includes(user?.role));
  };

  const navigationNav = getNavigationItems();

  return (
    <nav className="bg-white shadow-sm border-b border-gray-200">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between h-16">
          <div className="flex">
            <div className="flex-shrink-0 flex items-center">
              <div className="h-8 w-8 bg-primary-600 rounded-lg flex items-center justify-center">
                <svg className="h-5 w-5 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.746 0 3.332.477 4.5 1.253v13C19.832 18.477 18.246 18 16.5 18c-1.746 0-3.332.477-4.5 1.253" />
                </svg>
              </div>
              <span className="ml-3 text-xl font-semibold text-gray-900">
                Smart Quiz System
              </span>
            </div>
            <div className="hidden sm:ml-6 sm:flex sm:items-center sm:space-x-6">
              {/* Navigation items */}
              {navigationNav.map((item) => (
                <button
                  key={item.name}
                  onClick={() => navigate(item.path)}
                  className={`${
                    location.pathname === item.path
                      ? 'border-blue-500 text-gray-900'
                      : 'border-transparent text-gray-500 hover:border-gray-300 hover:text-gray-700'
                  } inline-flex items-center px-1 pt-1 border-b-2 text-sm font-medium transition-colors duration-200`}
                >
                  {item.name}
                </button>
              ))}
            </div>
          </div>

          <div className="flex items-center space-x-4">
            {/* User Role Badge */}
            <span className={`px-3 py-1 rounded-full text-xs font-medium ${
              user?.role === 'admin' ? 'bg-red-100 text-red-800' :
              user?.role === 'instructor' ? 'bg-blue-100 text-blue-800' :
              'bg-green-100 text-green-800'
            }`}>
              {user?.role?.charAt(0).toUpperCase() + user?.role?.slice(1)}
            </span>

            {/* User Menu */}
            <div className="relative">
              <div className="flex items-center space-x-3">
                <div className="flex-shrink-0">
                  <div className="h-8 w-8 rounded-full bg-gray-300 flex items-center justify-center">
                    <span className="text-sm font-medium text-gray-700">
                      {user?.full_name?.charAt(0) || user?.username?.charAt(0) || 'U'}
                    </span>
                  </div>
                </div>
                <div className="hidden md:block">
                  <div className="text-sm font-medium text-gray-900">
                    {user?.full_name || user?.username}
                  </div>
                  <div className="text-xs text-gray-500">
                    {user?.email}
                  </div>
                </div>
                <button
                  onClick={handleLogout}
                  className="text-gray-500 hover:text-gray-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500"
                  title="Logout"
                >
                  <svg className="h-5 w-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17 16l4-4m0 0l-4-4m4 4H7m6 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h4a3 3 0 013 3v1" />
                  </svg>
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Mobile menu */}
      <div className="sm:hidden">
        <div className="pt-2 pb-3 space-y-1">
          {/* Navigation items */}
          {navigationNav.map((item) => (
            <button
              key={item.name}
              onClick={() => navigate(item.path)}
              className={`${
                location.pathname === item.path
                  ? 'bg-blue-50 border-blue-500 text-blue-700'
                  : 'border-transparent text-gray-600 hover:bg-gray-50 hover:border-gray-300 hover:text-gray-800'
              } block pl-3 pr-4 py-2 border-l-4 text-base font-medium w-full text-left`}
            >
              {item.name}
            </button>
          ))}
        </div>
      </div>
    </nav>
  );
};

export default Navbar;
