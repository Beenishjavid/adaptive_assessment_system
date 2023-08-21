import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import api from '../services/api';
import { toast } from 'react-hot-toast';

const AvailableQuizzes = () => {
  const navigate = useNavigate();
  const [quizzes, setQuizzes] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [filter, setFilter] = useState('all');
  const [search, setSearch] = useState('');

  useEffect(() => {
    fetchQuizzes();
  }, []);

  const fetchQuizzes = async () => {
    try {
      setLoading(true);
      const response = await api.get('/api/quizzes/api/quizzes/all/');
      setQuizzes(response.data.quizzes);
    } catch (error) {
      setError(error.response?.data?.error || 'Failed to fetch quizzes');
      toast.error('Failed to load quizzes');
    } finally {
      setLoading(false);
    }
  };

  const startQuiz = async (quizId) => {
    try {
      const response = await api.post(`/api/quizzes/api/quiz/${quizId}/start/`);
      const attemptId = response.data.attempt_id;
      
      toast.success('Quiz started successfully!');
      navigate(`/take-quiz/${attemptId}`);
      
    } catch (error) {
      toast.error(error.response?.data?.error || 'Failed to start quiz');
    }
  };

  const filteredQuizzes = quizzes.filter(quiz => {
    const matchesSearch = quiz.title.toLowerCase().includes(search.toLowerCase()) ||
                         quiz.description.toLowerCase().includes(search.toLowerCase());
    
    if (filter === 'all') return matchesSearch;
    if (filter === 'assessment') return matchesSearch && quiz.quiz_type === 'assessment';
    if (filter === 'practice') return matchesSearch && quiz.quiz_type === 'practice';
    if (filter === 'exam') return matchesSearch && quiz.quiz_type === 'exam';
    
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

  const getDifficultyColor = (score) => {
    if (score >= 80) return 'text-red-600';
    if (score >= 60) return 'text-yellow-600';
    return 'text-green-600';
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-500 mx-auto"></div>
          <p className="mt-4 text-gray-600">Loading quizzes...</p>
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
            onClick={fetchQuizzes}
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
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900">Available Quizzes</h1>
          <p className="mt-2 text-gray-600">
            Choose from {filteredQuizzes.length} available quizzes
          </p>
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
                Filter by Type
              </label>
              <select
                value={filter}
                onChange={(e) => setFilter(e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500"
              >
                <option value="all">All Types</option>
                <option value="assessment">Assessment</option>
                <option value="practice">Practice</option>
                <option value="exam">Exam</option>
                <option value="survey">Survey</option>
              </select>
            </div>
          </div>
        </div>

        {/* Quizzes Grid */}
        {filteredQuizzes.length === 0 ? (
          <div className="text-center py-12">
            <div className="text-6xl mb-4">📝</div>
            <h3 className="text-lg font-medium text-gray-900 mb-2">No quizzes found</h3>
            <p className="text-gray-600">
              {search ? 'Try adjusting your search or filter criteria.' : 'No quizzes are currently available.'}
            </p>
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {filteredQuizzes.map((quiz) => (
              <div
                key={quiz.id}
                className="bg-white rounded-lg shadow-sm border border-gray-200 hover:shadow-md transition-shadow duration-200"
              >
                <div className="p-6">
                  {/* Quiz Header */}
                  <div className="flex justify-between items-start mb-4">
                    <div className="flex-1">
                      <h3 className="text-lg font-semibold text-gray-900 mb-2 line-clamp-2">
                        {quiz.title}
                      </h3>
                      <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${getQuizTypeColor(quiz.quiz_type)}`}>
                        {quiz.quiz_type.charAt(0).toUpperCase() + quiz.quiz_type.slice(1)}
                      </span>
                    </div>
                  </div>

                  {/* Quiz Description */}
                  <p className="text-gray-600 text-sm mb-4 line-clamp-3">
                    {quiz.description || 'No description available.'}
                  </p>

                  {/* Quiz Stats */}
                  <div className="space-y-2 mb-6">
                    <div className="flex justify-between text-sm">
                      <span className="text-gray-600">Questions:</span>
                      <span className="font-medium text-gray-900">{quiz.question_count}</span>
                    </div>
                    
                    <div className="flex justify-between text-sm">
                      <span className="text-gray-600">Duration:</span>
                      <span className="font-medium text-gray-900">
                        {quiz.duration_minutes ? `${quiz.duration_minutes} min` : 'No limit'}
                      </span>
                    </div>
                    
                    <div className="flex justify-between text-sm">
                      <span className="text-gray-600">Passing Score:</span>
                      <span className={`font-medium ${getDifficultyColor(quiz.passing_score)}`}>
                        {quiz.passing_score}%
                      </span>
                    </div>
                    
                    <div className="flex justify-between text-sm">
                      <span className="text-gray-600">Created by:</span>
                      <span className="font-medium text-gray-900 truncate ml-2">
                        {quiz.created_by}
                      </span>
                    </div>
                  </div>

                  {/* Actions */}
                  <div className="space-y-2">
                    <button
                      onClick={() => startQuiz(quiz.id)}
                      className="w-full bg-blue-600 text-white py-2 px-4 rounded-md hover:bg-blue-700 transition-colors duration-200 font-medium"
                    >
                      Start Quiz
                    </button>
                    
                    <button
                      onClick={() => navigate(`/quiz-preview/${quiz.id}`)}
                      className="w-full bg-gray-100 text-gray-700 py-2 px-4 rounded-md hover:bg-gray-200 transition-colors duration-200 text-sm"
                    >
                      Preview Details
                    </button>
                  </div>

                  {/* Created Date */}
                  {quiz.created_at && (
                    <div className="mt-4 pt-4 border-t border-gray-100">
                      <p className="text-xs text-gray-500">
                        Created: {new Date(quiz.created_at).toLocaleDateString()}
                      </p>
                    </div>
                  )}
                </div>
              </div>
            ))}
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

export default AvailableQuizzes;
