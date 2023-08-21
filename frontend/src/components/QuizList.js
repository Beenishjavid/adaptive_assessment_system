import React, { useState, useEffect } from 'react';
import api from '../services/api';

const QuizList = () => {
  const [quizzes, setQuizzes] = useState([]);
  const [stats, setStats] = useState({});
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    fetchData();
  }, []);

  const fetchData = async () => {
    try {
      setLoading(true);
      
      // Fetch dashboard stats
      const statsResponse = await api.get('/api/quizzes/api/dashboard/stats/');
      setStats(statsResponse.data);
      
      // Fetch all quizzes
      const quizzesResponse = await api.get('/api/quizzes/api/quizzes/all/');
      setQuizzes(quizzesResponse.data.quizzes);
      
    } catch (err) {
      setError('Failed to fetch data: ' + (err.response?.data?.error || err.message));
      console.error('Error fetching data:', err);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-500 mx-auto"></div>
          <p className="mt-4 text-gray-600">Loading quizzes from database...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded max-w-md">
          <strong className="font-bold">Error!</strong>
          <span className="block sm:inline"> {error}</span>
          <button 
            onClick={fetchData}
            className="mt-2 bg-red-500 text-white px-4 py-2 rounded hover:bg-red-600"
          >
            Retry
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50 py-8">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900">Smart Quiz System</h1>
          <p className="mt-2 text-gray-600">Real data from SQL Server database</p>
        </div>

        {/* Stats Cards */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
          <div className="bg-white overflow-hidden shadow rounded-lg">
            <div className="p-5">
              <div className="flex items-center">
                <div className="flex-shrink-0">
                  <div className="w-8 h-8 bg-blue-500 rounded-md flex items-center justify-center">
                    <span className="text-white font-bold">Q</span>
                  </div>
                </div>
                <div className="ml-5 w-0 flex-1">
                  <dl>
                    <dt className="text-sm font-medium text-gray-500 truncate">
                      Total Quizzes
                    </dt>
                    <dd className="text-lg font-medium text-gray-900">
                      {stats.total_quizzes || 0}
                    </dd>
                  </dl>
                </div>
              </div>
            </div>
          </div>

          <div className="bg-white overflow-hidden shadow rounded-lg">
            <div className="p-5">
              <div className="flex items-center">
                <div className="flex-shrink-0">
                  <div className="w-8 h-8 bg-green-500 rounded-md flex items-center justify-center">
                    <span className="text-white font-bold">U</span>
                  </div>
                </div>
                <div className="ml-5 w-0 flex-1">
                  <dl>
                    <dt className="text-sm font-medium text-gray-500 truncate">
                      Total Users
                    </dt>
                    <dd className="text-lg font-medium text-gray-900">
                      {stats.total_students || 0}
                    </dd>
                  </dl>
                </div>
              </div>
            </div>
          </div>

          <div className="bg-white overflow-hidden shadow rounded-lg">
            <div className="p-5">
              <div className="flex items-center">
                <div className="flex-shrink-0">
                  <div className="w-8 h-8 bg-purple-500 rounded-md flex items-center justify-center">
                    <span className="text-white font-bold">?</span>
                  </div>
                </div>
                <div className="ml-5 w-0 flex-1">
                  <dl>
                    <dt className="text-sm font-medium text-gray-500 truncate">
                      Questions
                    </dt>
                    <dd className="text-lg font-medium text-gray-900">
                      {stats.total_questions || 0}
                    </dd>
                  </dl>
                </div>
              </div>
            </div>
          </div>

          <div className="bg-white overflow-hidden shadow rounded-lg">
            <div className="p-5">
              <div className="flex items-center">
                <div className="flex-shrink-0">
                  <div className="w-8 h-8 bg-orange-500 rounded-md flex items-center justify-center">
                    <span className="text-white font-bold">O</span>
                  </div>
                </div>
                <div className="ml-5 w-0 flex-1">
                  <dl>
                    <dt className="text-sm font-medium text-gray-500 truncate">
                      Organizations
                    </dt>
                    <dd className="text-lg font-medium text-gray-900">
                      {stats.total_organizations || 0}
                    </dd>
                  </dl>
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* Quizzes List */}
        <div className="bg-white shadow overflow-hidden sm:rounded-md">
          <div className="px-4 py-5 sm:px-6">
            <h3 className="text-lg leading-6 font-medium text-gray-900">
              Available Quizzes
            </h3>
            <p className="mt-1 max-w-2xl text-sm text-gray-500">
              {quizzes.length} active quizzes from the database
            </p>
          </div>
          
          {quizzes.length === 0 ? (
            <div className="px-4 py-5 sm:px-6 text-center">
              <p className="text-gray-500">No quizzes available</p>
            </div>
          ) : (
            <ul className="divide-y divide-gray-200">
              {quizzes.map((quiz) => (
                <li key={quiz.id}>
                  <div className="px-4 py-4 sm:px-6">
                    <div className="flex items-center justify-between">
                      <div className="flex-1 min-w-0">
                        <h4 className="text-lg font-medium text-blue-600 truncate">
                          {quiz.title}
                        </h4>
                        <p className="mt-1 text-sm text-gray-600">
                          {quiz.description}
                        </p>
                        <div className="mt-2 flex items-center text-sm text-gray-500">
                          <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-blue-100 text-blue-800 mr-2">
                            {quiz.quiz_type}
                          </span>
                          <span className="mr-4">
                            📝 {quiz.question_count} questions
                          </span>
                          <span className="mr-4">
                            ⏱️ {quiz.duration_minutes} minutes
                          </span>
                          <span>
                            📊 Pass: {quiz.passing_score}%
                          </span>
                        </div>
                        <p className="mt-1 text-xs text-gray-400">
                          Created by: {quiz.created_by}
                        </p>
                      </div>
                      <div className="flex-shrink-0">
                        <button 
                          onClick={() => window.open(`/api/quizzes/api/quizzes/${quiz.id}/`, '_blank')}
                          className="inline-flex items-center px-3 py-2 border border-transparent text-sm leading-4 font-medium rounded-md text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
                        >
                          View Details
                        </button>
                      </div>
                    </div>
                  </div>
                </li>
              ))}
            </ul>
          )}
        </div>

        {/* Debug Info */}
        <div className="mt-8 bg-gray-100 rounded-lg p-4">
          <h4 className="font-medium text-gray-900 mb-2">🔍 Database Connection Status</h4>
          <div className="grid grid-cols-2 gap-4 text-sm">
            <div>
              <span className="font-medium">Backend API:</span> 
              <span className="text-green-600 ml-1">✅ Connected</span>
            </div>
            <div>
              <span className="font-medium">Database:</span> 
              <span className="text-green-600 ml-1">✅ SQL Server</span>
            </div>
            <div>
              <span className="font-medium">Data Source:</span> 
              <span className="text-blue-600 ml-1">Real Database Tables</span>
            </div>
            <div>
              <span className="font-medium">Last Updated:</span> 
              <span className="text-gray-600 ml-1">{new Date().toLocaleTimeString()}</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default QuizList;
