import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import api from '../services/api';
import { toast } from 'react-hot-toast';

const MyQuizzes = () => {
  const navigate = useNavigate();
  const [quizzes, setQuizzes] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [filter, setFilter] = useState('all');
  const [search, setSearch] = useState('');

  useEffect(() => {
    fetchMyQuizzes();
  }, []);

  const fetchMyQuizzes = async () => {
    try {
      setLoading(true);
      const response = await api.get('/api/quizzes/api/quiz/my-quizzes/');
      setQuizzes(response.data.quizzes);
    } catch (error) {
      setError(error.response?.data?.error || 'Failed to fetch quizzes');
      toast.error('Failed to load your quizzes');
    } finally {
      setLoading(false);
    }
  };

  const deleteQuiz = async (quizId, quizTitle) => {
    if (!window.confirm(`Are you sure you want to delete "${quizTitle}"? This action cannot be undone.`)) {
      return;
    }

    try {
      await api.delete(`/api/quizzes/api/quiz/${quizId}/delete/`);
      toast.success('Quiz deleted successfully');
      setQuizzes(prev => prev.filter(quiz => quiz.id !== quizId));
    } catch (error) {
      toast.error(error.response?.data?.error || 'Failed to delete quiz');
    }
  };

  const toggleQuizStatus = async (quizId, currentStatus) => {
    try {
      await api.put(`/api/quizzes/api/quiz/${quizId}/update/`, {
        is_active: !currentStatus
      });
      
      setQuizzes(prev => prev.map(quiz => 
        quiz.id === quizId 
          ? { ...quiz, is_active: !currentStatus }
          : quiz
      ));
      
      toast.success(`Quiz ${!currentStatus ? 'activated' : 'deactivated'} successfully`);
    } catch (error) {
      toast.error(error.response?.data?.error || 'Failed to update quiz status');
    }
  };

  const filteredQuizzes = quizzes.filter(quiz => {
    const matchesSearch = quiz.title.toLowerCase().includes(search.toLowerCase()) ||
                         quiz.description.toLowerCase().includes(search.toLowerCase());
    
    if (filter === 'all') return matchesSearch;
    if (filter === 'active') return matchesSearch && quiz.is_active;
    if (filter === 'inactive') return matchesSearch && !quiz.is_active;
    if (filter === 'assessment') return matchesSearch && quiz.quiz_type === 'assessment';
    if (filter === 'practice') return matchesSearch && quiz.quiz_type === 'practice';
    
    return matchesSearch;
  });

  const getQuizTypeColor = (type) => {
    const colors = {
      assessment: 'bg-blue-100 text-blue-800',
      practice: 'bg-green-100 text-green-800',
      exam: 'bg-red-100 text-red-800',
      survey: 'bg-purple-100 text-purple-800'
    };
    return colors[type] || 'bg-gray-100 text-gray-800';
  };

  const getStatusColor = (isActive) => {
    return isActive 
      ? 'bg-green-100 text-green-800' 
      : 'bg-gray-100 text-gray-800';
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-500 mx-auto"></div>
          <p className="mt-4 text-gray-600">Loading your quizzes...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="bg-red-100 border border-red-400 text-red-700 px-6 py-4 rounded max-w-md">
          <strong className="font-bold">Error!</strong>
          <span className="block sm:inline"> {error}</span>
          <button 
            onClick={fetchMyQuizzes}
            className="mt-4 bg-red-500 text-white px-4 py-2 rounded hover:bg-red-600"
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
        <div className="flex justify-between items-center mb-8">
          <div>
            <h1 className="text-3xl font-bold text-gray-900">My Quizzes</h1>
            <p className="mt-2 text-gray-600">
              Manage your {filteredQuizzes.length} quizzes
            </p>
          </div>
          <button
            onClick={() => navigate('/create-quiz')}
            className="bg-blue-600 text-white px-6 py-2 rounded-md hover:bg-blue-700 transition-colors font-medium"
          >
            + Create New Quiz
          </button>
        </div>

        {/* Filters and Search */}
        <div className="bg-white rounded-lg shadow-sm p-6 mb-8">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Search Quizzes
              </label>
              <input
                type="text"
                value={search}
                onChange={(e) => setSearch(e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500"
                placeholder="Search by title or description..."
              />
            </div>
            
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Filter Quizzes
              </label>
              <select
                value={filter}
                onChange={(e) => setFilter(e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500"
              >
                <option value="all">All Quizzes</option>
                <option value="active">Active Only</option>
                <option value="inactive">Inactive Only</option>
                <option value="assessment">Assessments</option>
                <option value="practice">Practice</option>
              </select>
            </div>
          </div>
        </div>

        {/* Quizzes Table */}
        {filteredQuizzes.length === 0 ? (
          <div className="text-center py-12">
            <div className="text-6xl mb-4">📝</div>
            <h3 className="text-lg font-medium text-gray-900 mb-2">
              {search || filter !== 'all' ? 'No quizzes found' : 'No quizzes created yet'}
            </h3>
            <p className="text-gray-600 mb-4">
              {search || filter !== 'all' 
                ? 'Try adjusting your search or filter criteria.' 
                : 'Create your first quiz to get started!'
              }
            </p>
            {(!search && filter === 'all') && (
              <button
                onClick={() => navigate('/create-quiz')}
                className="bg-blue-600 text-white px-6 py-2 rounded-md hover:bg-blue-700 transition-colors"
              >
                Create Your First Quiz
              </button>
            )}
          </div>
        ) : (
          <div className="bg-white shadow-sm rounded-lg overflow-hidden">
            <div className="overflow-x-auto">
              <table className="min-w-full divide-y divide-gray-200">
                <thead className="bg-gray-50">
                  <tr>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Quiz Details
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Stats
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Status
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Created
                    </th>
                    <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Actions
                    </th>
                  </tr>
                </thead>
                <tbody className="bg-white divide-y divide-gray-200">
                  {filteredQuizzes.map((quiz) => (
                    <tr key={quiz.id} className="hover:bg-gray-50">
                      <td className="px-6 py-4">
                        <div className="flex items-start">
                          <div className="flex-1 min-w-0">
                            <h4 className="text-sm font-medium text-gray-900 truncate">
                              {quiz.title}
                            </h4>
                            <p className="text-sm text-gray-600 mt-1 line-clamp-2">
                              {quiz.description || 'No description'}
                            </p>
                            <div className="mt-2">
                              <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${getQuizTypeColor(quiz.quiz_type)}`}>
                                {quiz.quiz_type.charAt(0).toUpperCase() + quiz.quiz_type.slice(1)}
                              </span>
                            </div>
                          </div>
                        </div>
                      </td>
                      
                      <td className="px-6 py-4 whitespace-nowrap">
                        <div className="text-sm text-gray-900">
                          <div>📝 {quiz.question_count} questions</div>
                          <div>👥 {quiz.attempt_count} attempts</div>
                          <div>⏱️ {quiz.duration_minutes ? `${quiz.duration_minutes}m` : 'No limit'}</div>
                          <div>📊 {quiz.passing_score}% to pass</div>
                        </div>
                      </td>
                      
                      <td className="px-6 py-4 whitespace-nowrap">
                        <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${getStatusColor(quiz.is_active)}`}>
                          {quiz.is_active ? 'Active' : 'Inactive'}
                        </span>
                        <div className="text-xs text-gray-500 mt-1">
                          {quiz.visibility}
                        </div>
                      </td>
                      
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-600">
                        {new Date(quiz.created_at).toLocaleDateString()}
                      </td>
                      
                      <td className="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                        <div className="flex justify-end space-x-2">
                          <button
                            onClick={() => navigate(`/quiz-preview/${quiz.id}`)}
                            className="text-blue-600 hover:text-blue-900 bg-blue-50 hover:bg-blue-100 px-2 py-1 rounded text-xs"
                            title="Preview"
                          >
                            👁️
                          </button>
                          
                          <button
                            onClick={() => navigate(`/edit-quiz/${quiz.id}`)}
                            className="text-indigo-600 hover:text-indigo-900 bg-indigo-50 hover:bg-indigo-100 px-2 py-1 rounded text-xs"
                            title="Edit"
                          >
                            ✏️
                          </button>
                          
                          <button
                            onClick={() => toggleQuizStatus(quiz.id, quiz.is_active)}
                            className={`px-2 py-1 rounded text-xs ${
                              quiz.is_active 
                                ? 'text-yellow-600 hover:text-yellow-900 bg-yellow-50 hover:bg-yellow-100'
                                : 'text-green-600 hover:text-green-900 bg-green-50 hover:bg-green-100'
                            }`}
                            title={quiz.is_active ? 'Deactivate' : 'Activate'}
                          >
                            {quiz.is_active ? '🔒' : '✅'}
                          </button>
                          
                          <button
                            onClick={() => navigate(`/quiz-results/${quiz.id}`)}
                            className="text-purple-600 hover:text-purple-900 bg-purple-50 hover:bg-purple-100 px-2 py-1 rounded text-xs"
                            title="View Results"
                          >
                            📊
                          </button>
                          
                          <button
                            onClick={() => deleteQuiz(quiz.id, quiz.title)}
                            className="text-red-600 hover:text-red-900 bg-red-50 hover:bg-red-100 px-2 py-1 rounded text-xs"
                            title="Delete"
                          >
                            🗑️
                          </button>
                        </div>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        )}

        {/* Back to Dashboard */}
        <div className="mt-8 text-center">
          <button
            onClick={() => navigate('/dashboard')}
            className="px-6 py-2 bg-gray-600 text-white rounded-md hover:bg-gray-700 transition-colors"
          >
            Back to Dashboard
          </button>
        </div>
      </div>
    </div>
  );
};

export default MyQuizzes;
