import React from 'react';
import { useAuth } from '../context/AuthContext';
import Navbar from '../components/Navbar';
import DashboardStats from '../components/DashboardStats';
import RecentQuizzes from '../components/RecentQuizzes';
import QuickActions from '../components/QuickActions';

const Dashboard = () => {
  const { user } = useAuth();

  return (
    <div className="min-h-screen bg-gray-50">
      <Navbar />
      
      <main className="max-w-7xl mx-auto py-6 sm:px-6 lg:px-8">
        {/* Welcome Section */}
        <div className="px-4 py-6 sm:px-0">
          <div className="mb-8">
            <h1 className="text-3xl font-bold text-gray-900">
              Welcome back, {user?.full_name || user?.username}!
            </h1>
            <p className="mt-2 text-gray-600">
              {user?.role === 'admin' && 'Manage your platform and monitor system performance.'}
              {user?.role === 'instructor' && 'Create quizzes, manage students, and track progress.'}
              {user?.role === 'student' && 'Take quizzes, track your progress, and improve your skills.'}
            </p>
          </div>

          {/* Dashboard Stats */}
          <DashboardStats />

          <div className="mt-8 grid grid-cols-1 lg:grid-cols-3 gap-8">
            {/* Quick Actions */}
            <div className="lg:col-span-1">
              <QuickActions />
            </div>

            {/* Recent Quizzes */}
            <div className="lg:col-span-2">
              <RecentQuizzes />
            </div>
          </div>
        </div>
      </main>
    </div>
  );
};

export default Dashboard;
