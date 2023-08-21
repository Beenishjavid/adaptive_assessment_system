import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import api from '../services/api';
import { toast } from 'react-hot-toast';

const MyResults = () => {
  const navigate = useNavigate();
  const [results, setResults] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [filter, setFilter] = useState('all');
  const [search, setSearch] = useState('');

  useEffect(() => {
    fetchMyResults();
  }, []);

  const fetchMyResults = async () => {
    try {
      setLoading(true);
      const response = await api.get('/api/quizzes/api/my-results/');
      setResults(response.data.results);
    } catch (error) {
      setError(error.response?.data?.error || 'Failed to fetch results');
      toast.error('Failed to load your results');
    } finally {
      setLoading(false);
    }
  };

  const viewDetailedResult = async (attemptId) => {
    try {
      await api.get(`/api/quizzes/api/attempt/${attemptId}/result/`);
      // Navigate to a detailed results view or show modal
      navigate(`/quiz-result/${attemptId}`);
    } catch (error) {
      toast.error('Failed to load detailed result');
    }
  };

  const getStatusColor = (percentage) => {
    if (percentage >= 80) return 'text-green-600 bg-green-100';
    if (percentage >= 60) return 'text-yellow-600 bg-yellow-100';
    return 'text-red-600 bg-red-100';
  };

  const getStatusText = (percentage, passingScore) => {
    return percentage >= passingScore ? 'Passed' : 'Failed';
  };

  const filteredResults = results.filter(result => {
    const matchesSearch = result.quiz_title.toLowerCase().includes(search.toLowerCase());
    
    if (filter === 'all') return matchesSearch;
    if (filter === 'passed') return matchesSearch && result.percentage >= result.passing_score;
    if (filter === 'failed') return matchesSearch && result.percentage < result.passing_score;
    if (filter === 'recent') return matchesSearch; // Could add date filter logic
    
    return matchesSearch;
  });

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 py-8">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-center items-center h-64">
            <div className="animate-spin rounded-full h-32 w-32 border-b-2 border-blue-600"></div>
          </div>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="min-h-screen bg-gray-50 py-8">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="bg-red-50 border border-red-200 rounded-md p-4">
            <div className="flex">
              <div className="ml-3">
                <h3 className="text-sm font-medium text-red-800">Error</h3>
                <div className="mt-2 text-sm text-red-700">
                  <p>{error}</p>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50 py-8">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* Header */}
        <div className="bg-white shadow-sm rounded-lg border border-gray-200 mb-6 p-6">
          <div className="flex justify-between items-center">
            <div>
              <h1 className="text-2xl font-bold text-gray-900">My Quiz Results</h1>
              <p className="text-gray-600 mt-1">Track your quiz performance and progress</p>
            </div>
            <button
              onClick={() => navigate('/dashboard')}
              className="bg-blue-600 text-white px-4 py-2 rounded-md hover:bg-blue-700 transition-colors"
            >
              Back to Dashboard
            </button>
          </div>
        </div>

        {/* Filters */}
        <div className="bg-white shadow-sm rounded-lg border border-gray-200 mb-6 p-6">
          <div className="flex flex-col sm:flex-row gap-4">
            <div className="flex-1">
              <input
                type="text"
                placeholder="Search quizzes..."
                value={search}
                onChange={(e) => setSearch(e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500"
              />
            </div>
            <select
              value={filter}
              onChange={(e) => setFilter(e.target.value)}
              className="px-3 py-2 border border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500"
            >
              <option value="all">All Results</option>
              <option value="passed">Passed</option>
              <option value="failed">Failed</option>
              <option value="recent">Recent</option>
            </select>
          </div>
        </div>

        {/* Results List */}
        <div className="space-y-4">
          {filteredResults.length === 0 ? (
            <div className="bg-white shadow-sm rounded-lg border border-gray-200 p-8 text-center">
              <div className="text-gray-400 mb-4">
                <svg className="mx-auto h-16 w-16" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                </svg>
              </div>
              <h3 className="text-lg font-medium text-gray-900 mb-2">No Results Found</h3>
              <p className="text-gray-500">
                {search || filter !== 'all' 
                  ? 'No results match your current filters.' 
                  : 'You haven\'t taken any quizzes yet.'}
              </p>
              {!search && filter === 'all' && (
                <button
                  onClick={() => navigate('/available-quizzes')}
                  className="mt-4 bg-blue-600 text-white px-4 py-2 rounded-md hover:bg-blue-700 transition-colors"
                >
                  Browse Available Quizzes
                </button>
              )}
            </div>
          ) : (
            filteredResults.map((result, index) => (
              <div key={index} className="bg-white shadow-sm rounded-lg border border-gray-200 p-6">
                <div className="flex justify-between items-start">
                  <div className="flex-1">
                    <h3 className="text-lg font-semibold text-gray-900 mb-2">
                      {result.quiz_title}
                    </h3>
                    
                    <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-4">
                      <div>
                        <span className="text-sm text-gray-500">Score</span>
                        <div className="flex items-center">
                          <span className="text-2xl font-bold text-gray-900">
                            {result.score}/{result.total_marks}
                          </span>
                          <span className="ml-2 text-lg text-gray-600">
                            ({result.percentage}%)
                          </span>
                        </div>
                      </div>
                      
                      <div>
                        <span className="text-sm text-gray-500">Status</span>
                        <div>
                          <span className={`inline-flex px-2 py-1 text-xs font-semibold rounded-full ${getStatusColor(result.percentage)}`}>
                            {getStatusText(result.percentage, result.passing_score)}
                          </span>
                        </div>
                      </div>
                      
                      <div>
                        <span className="text-sm text-gray-500">Completed</span>
                        <div className="text-sm text-gray-900">
                          {new Date(result.completed_at).toLocaleDateString()} at{' '}
                          {new Date(result.completed_at).toLocaleTimeString()}
                        </div>
                      </div>
                    </div>

                    <div className="flex items-center text-sm text-gray-500">
                      <span>Attempt {result.attempt_number}</span>
                      <span className="mx-2">•</span>
                      <span>{result.total_questions} questions</span>
                      <span className="mx-2">•</span>
                      <span>Passing: {result.passing_score}%</span>
                    </div>
                  </div>

                  <div className="ml-6">
                    <button
                      onClick={() => viewDetailedResult(result.attempt_id)}
                      className="bg-blue-50 text-blue-600 px-4 py-2 rounded-md hover:bg-blue-100 transition-colors"
                    >
                      View Details
                    </button>
                  </div>
                </div>
              </div>
            ))
          )}
        </div>

        {/* Summary Stats */}
        {results.length > 0 && (
          <div className="mt-8 bg-white shadow-sm rounded-lg border border-gray-200 p-6">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">Performance Summary</h3>
            <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
              <div className="text-center">
                <div className="text-2xl font-bold text-blue-600">
                  {results.length}
                </div>
                <div className="text-sm text-gray-500">Total Quizzes</div>
              </div>
              <div className="text-center">
                <div className="text-2xl font-bold text-green-600">
                  {results.filter(r => r.percentage >= r.passing_score).length}
                </div>
                <div className="text-sm text-gray-500">Passed</div>
              </div>
              <div className="text-center">
                <div className="text-2xl font-bold text-red-600">
                  {results.filter(r => r.percentage < r.passing_score).length}
                </div>
                <div className="text-sm text-gray-500">Failed</div>
              </div>
              <div className="text-center">
                <div className="text-2xl font-bold text-purple-600">
                  {results.length > 0 ? Math.round(results.reduce((sum, r) => sum + r.percentage, 0) / results.length) : 0}%
                </div>
                <div className="text-sm text-gray-500">Average Score</div>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default MyResults;
