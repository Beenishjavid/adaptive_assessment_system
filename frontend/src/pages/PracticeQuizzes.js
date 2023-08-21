import React, { useState, useEffect } from 'react';
import { useAuth } from '../context/AuthContext';
import { useNavigate } from 'react-router-dom';
import Navbar from '../components/Navbar';
import api from '../services/api';
import toast from 'react-hot-toast';

const PracticeQuizzes = () => {
  const { user } = useAuth();
  const navigate = useNavigate();
  const [practiceQuizzes, setPracticeQuizzes] = useState([]);
  const [loading, setLoading] = useState(true);
  const [selectedTopic, setSelectedTopic] = useState('all');
  const [topics, setTopics] = useState([]);

  const fetchPracticeQuizzes = async () => {
    try {
      setLoading(true);
      const params = selectedTopic !== 'all' ? `?topic=${selectedTopic}` : '';
      const response = await api.get(`/api/quizzes/practice-quizzes/${params}`);
      setPracticeQuizzes(response.data.quizzes || []);
    } catch (error) {
      console.error('Error fetching practice quizzes:', error);
      toast.error('Failed to fetch practice quizzes');
    } finally {
      setLoading(false);
    }
  };

  const fetchTopics = async () => {
    try {
      const response = await api.get('/api/quizzes/topics/');
      setTopics(response.data.topics || []);
    } catch (error) {
      console.error('Error fetching topics:', error);
    }
  };

  useEffect(() => {
    fetchPracticeQuizzes();
    fetchTopics();
  }, [selectedTopic]); // eslint-disable-line react-hooks/exhaustive-deps

  const startPracticeQuiz = async (quizId) => {
    try {
      const response = await api.post(`/api/quizzes/api/quiz/${quizId}/start/`, {
        practice_mode: true
      });
      const attemptId = response.data.attempt_id;
      navigate(`/take-quiz/${attemptId}?practice=true`);
    } catch (error) {
      console.error('Error starting practice quiz:', error);
      toast.error('Failed to start practice quiz');
    }
  };

  const getDifficultyColor = (difficulty) => {
    switch (difficulty) {
      case 'easy':
        return 'bg-green-100 text-green-800';
      case 'medium':
        return 'bg-yellow-100 text-yellow-800';
      case 'hard':
        return 'bg-red-100 text-red-800';
      default:
        return 'bg-gray-100 text-gray-800';
    }
  };

  return (
    <div className="min-h-screen bg-gray-50">
      <Navbar />
      
      <main className="max-w-7xl mx-auto py-6 sm:px-6 lg:px-8">
        <div className="px-4 py-6 sm:px-0">
          {/* Header */}
          <div className="mb-8">
            <h1 className="text-3xl font-bold text-gray-900">Practice Quizzes</h1>
            <p className="mt-2 text-gray-600">
              Practice with unlimited attempts. No scores are recorded.
            </p>
          </div>

          {/* Filters */}
          <div className="mb-6 flex items-center space-x-4">
            <label className="text-sm font-medium text-gray-700">Filter by topic:</label>
            <select
              value={selectedTopic}
              onChange={(e) => setSelectedTopic(e.target.value)}
              className="border border-gray-300 rounded-md px-3 py-2 text-sm"
            >
              <option value="all">All Topics</option>
              {topics.map((topic) => (
                <option key={topic.id} value={topic.id}>
                  {topic.name}
                </option>
              ))}
            </select>
          </div>

          {/* Practice Quizzes Grid */}
          {loading ? (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
              {[1, 2, 3, 4, 5, 6].map((index) => (
                <div key={index} className="bg-white rounded-lg shadow-sm border border-gray-200 p-6 animate-pulse">
                  <div className="h-6 bg-gray-200 rounded w-3/4 mb-4"></div>
                  <div className="h-4 bg-gray-200 rounded w-full mb-2"></div>
                  <div className="h-4 bg-gray-200 rounded w-2/3 mb-4"></div>
                  <div className="h-10 bg-gray-200 rounded w-full"></div>
                </div>
              ))}
            </div>
          ) : (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
              {practiceQuizzes.map((quiz) => (
                <div key={quiz.id} className="bg-white rounded-lg shadow-sm border border-gray-200 p-6 hover:shadow-md transition-shadow">
                  <div className="flex items-start justify-between mb-4">
                    <h3 className="text-lg font-semibold text-gray-900">{quiz.title}</h3>
                    <span className={`inline-flex px-2 py-1 text-xs font-semibold rounded-full ${getDifficultyColor(quiz.difficulty)}`}>
                      {quiz.difficulty || 'Medium'}
                    </span>
                  </div>
                  
                  <div className="mb-4">
                    <p className="text-sm text-gray-600 mb-3">{quiz.description || 'No description available'}</p>
                    
                    <div className="grid grid-cols-2 gap-4 text-sm text-gray-500">
                      <div className="flex items-center">
                        <span className="mr-2">📝</span>
                        <span>{quiz.question_count || 0} questions</span>
                      </div>
                      <div className="flex items-center">
                        <span className="mr-2">⏱️</span>
                        <span>{quiz.duration_minutes || 'Unlimited'} min</span>
                      </div>
                      <div className="flex items-center">
                        <span className="mr-2">📊</span>
                        <span>{quiz.topic_name || 'General'}</span>
                      </div>
                      <div className="flex items-center">
                        <span className="mr-2">👤</span>
                        <span>{quiz.created_by}</span>
                      </div>
                    </div>
                  </div>
                  
                  <button
                    onClick={() => startPracticeQuiz(quiz.id)}
                    className="w-full bg-blue-600 text-white py-2 px-4 rounded-lg hover:bg-blue-700 transition-colors font-medium"
                  >
                    Start Practice
                  </button>
                </div>
              ))}
            </div>
          )}
          
          {!loading && practiceQuizzes.length === 0 && (
            <div className="text-center py-12">
              <div className="mx-auto h-24 w-24 text-gray-400 mb-4">
                🎓
              </div>
              <h3 className="text-lg font-medium text-gray-900 mb-2">No Practice Quizzes Available</h3>
              <p className="text-gray-500 mb-4">
                {selectedTopic !== 'all' 
                  ? 'No practice quizzes found for the selected topic.' 
                  : 'Check back later for practice quizzes.'}
              </p>
              {selectedTopic !== 'all' && (
                <button
                  onClick={() => setSelectedTopic('all')}
                  className="text-blue-600 hover:text-blue-700 font-medium"
                >
                  View all topics
                </button>
              )}
            </div>
          )}

          {/* Practice Mode Info */}
          <div className="mt-12 bg-blue-50 rounded-lg p-6">
            <h3 className="text-lg font-semibold text-blue-900 mb-3">About Practice Mode</h3>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-sm text-blue-800">
              <div className="flex items-start">
                <span className="mr-2 mt-1">✅</span>
                <span>Unlimited attempts with no scoring</span>
              </div>
              <div className="flex items-start">
                <span className="mr-2 mt-1">📚</span>
                <span>Immediate feedback on answers</span>
              </div>
              <div className="flex items-start">
                <span className="mr-2 mt-1">🔄</span>
                <span>Retake as many times as you want</span>
              </div>
              <div className="flex items-start">
                <span className="mr-2 mt-1">🎯</span>
                <span>Perfect for learning and preparation</span>
              </div>
            </div>
          </div>
        </div>
      </main>
    </div>
  );
};

export default PracticeQuizzes;
