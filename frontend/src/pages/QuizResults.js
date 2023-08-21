import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { toast } from 'react-hot-toast';
import api from '../services/api';

const QuizResults = () => {
  const { id } = useParams();
  const navigate = useNavigate();
  const [analytics, setAnalytics] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [activeTab, setActiveTab] = useState('overview');

  useEffect(() => {
    const loadAnalytics = async () => {
      try {
        setLoading(true);
        const response = await api.get(`/api/quizzes/api/quiz/${id}/results/`);
        setAnalytics(response.data);
      } catch (error) {
        setError(error.response?.data?.error || 'Failed to load quiz analytics');
        toast.error('Failed to load quiz analytics');
      } finally {
        setLoading(false);
      }
    };

    loadAnalytics();
  }, [id]);

  const formatDuration = (seconds) => {
    if (!seconds) return 'N/A';
    const minutes = Math.floor(seconds / 60);
    const remainingSeconds = seconds % 60;
    return `${minutes}m ${remainingSeconds}s`;
  };

  const getScoreColor = (score, passingScore) => {
    if (score >= passingScore) return 'text-green-600';
    if (score >= passingScore * 0.8) return 'text-yellow-600';
    return 'text-red-600';
  };

  const getAccuracyColor = (accuracy) => {
    if (accuracy >= 80) return 'bg-green-100 text-green-800';
    if (accuracy >= 60) return 'bg-yellow-100 text-yellow-800';
    return 'bg-red-100 text-red-800';
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-500 mx-auto"></div>
          <p className="mt-4 text-gray-600">Loading quiz analytics...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="bg-red-100 border border-red-400 text-red-700 px-6 py-4 rounded max-w-md text-center">
          <strong className="font-bold">Error!</strong>
          <span className="block sm:inline"> {error}</span>
          <div className="mt-4 space-x-2">
            <button 
              onClick={() => window.location.reload()}
              className="bg-red-500 text-white px-4 py-2 rounded hover:bg-red-600"
            >
              Retry
            </button>
            <button 
              onClick={() => navigate('/my-quizzes')}
              className="bg-gray-500 text-white px-4 py-2 rounded hover:bg-gray-600"
            >
              Back to My Quizzes
            </button>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50 py-8">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* Header */}
        <div className="bg-white rounded-lg shadow-sm mb-8 p-6">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-2xl font-bold text-gray-900">Quiz Results & Analytics</h1>
              <p className="text-gray-600 mt-1">{analytics.quiz.title}</p>
            </div>
            <div className="flex space-x-3">
              <button
                onClick={() => navigate(`/quiz-preview/${id}`)}
                className="bg-blue-600 text-white px-4 py-2 rounded-md hover:bg-blue-700 transition-colors"
              >
                Preview Quiz
              </button>
              <button
                onClick={() => navigate(`/edit-quiz/${id}`)}
                className="bg-green-600 text-white px-4 py-2 rounded-md hover:bg-green-700 transition-colors"
              >
                Edit Quiz
              </button>
              <button
                onClick={() => navigate('/my-quizzes')}
                className="bg-gray-600 text-white px-4 py-2 rounded-md hover:bg-gray-700 transition-colors"
              >
                Back to My Quizzes
              </button>
            </div>
          </div>
        </div>

        {/* Tab Navigation */}
        <div className="bg-white rounded-lg shadow-sm mb-8">
          <div className="border-b border-gray-200">
            <nav className="-mb-px flex space-x-8 px-6">
              {[
                { id: 'overview', name: 'Overview', icon: '📊' },
                { id: 'attempts', name: 'Recent Attempts', icon: '👥' },
                { id: 'questions', name: 'Question Analytics', icon: '📝' },
                { id: 'distribution', name: 'Score Distribution', icon: '📈' }
              ].map((tab) => (
                <button
                  key={tab.id}
                  onClick={() => setActiveTab(tab.id)}
                  className={`${
                    activeTab === tab.id
                      ? 'border-blue-500 text-blue-600'
                      : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                  } whitespace-nowrap py-4 px-1 border-b-2 font-medium text-sm flex items-center space-x-2`}
                >
                  <span>{tab.icon}</span>
                  <span>{tab.name}</span>
                </button>
              ))}
            </nav>
          </div>

          <div className="p-6">
            {/* Overview Tab */}
            {activeTab === 'overview' && (
              <div className="space-y-6">
                {/* Key Statistics */}
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
                  <div className="bg-blue-50 p-4 rounded-lg">
                    <div className="flex items-center justify-between">
                      <div>
                        <p className="text-blue-600 text-sm font-medium">Total Attempts</p>
                        <p className="text-2xl font-bold text-blue-900">{analytics.statistics.total_attempts}</p>
                      </div>
                      <div className="text-blue-400 text-2xl">📝</div>
                    </div>
                  </div>

                  <div className="bg-green-50 p-4 rounded-lg">
                    <div className="flex items-center justify-between">
                      <div>
                        <p className="text-green-600 text-sm font-medium">Pass Rate</p>
                        <p className="text-2xl font-bold text-green-900">{analytics.statistics.pass_rate}%</p>
                      </div>
                      <div className="text-green-400 text-2xl">✅</div>
                    </div>
                  </div>

                  <div className="bg-purple-50 p-4 rounded-lg">
                    <div className="flex items-center justify-between">
                      <div>
                        <p className="text-purple-600 text-sm font-medium">Average Score</p>
                        <p className="text-2xl font-bold text-purple-900">{analytics.statistics.average_score}%</p>
                      </div>
                      <div className="text-purple-400 text-2xl">📊</div>
                    </div>
                  </div>

                  <div className="bg-orange-50 p-4 rounded-lg">
                    <div className="flex items-center justify-between">
                      <div>
                        <p className="text-orange-600 text-sm font-medium">Completed</p>
                        <p className="text-2xl font-bold text-orange-900">{analytics.statistics.completed_attempts}</p>
                      </div>
                      <div className="text-orange-400 text-2xl">🏁</div>
                    </div>
                  </div>
                </div>

                {/* Detailed Statistics */}
                <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                  <div className="bg-gray-50 p-4 rounded-lg">
                    <h3 className="text-lg font-semibold text-gray-900 mb-4">Quiz Information</h3>
                    <div className="space-y-2 text-sm">
                      <div className="flex justify-between">
                        <span className="text-gray-600">Total Questions:</span>
                        <span className="font-medium">{analytics.quiz.total_questions}</span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-gray-600">Passing Score:</span>
                        <span className="font-medium">{analytics.quiz.passing_score}%</span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-gray-600">Highest Score:</span>
                        <span className="font-medium text-green-600">{analytics.statistics.highest_score}%</span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-gray-600">Lowest Score:</span>
                        <span className="font-medium text-red-600">{analytics.statistics.lowest_score}%</span>
                      </div>
                    </div>
                  </div>

                  <div className="bg-gray-50 p-4 rounded-lg">
                    <h3 className="text-lg font-semibold text-gray-900 mb-4">Performance Summary</h3>
                    <div className="space-y-2 text-sm">
                      <div className="flex justify-between">
                        <span className="text-gray-600">Students Passed:</span>
                        <span className="font-medium text-green-600">{analytics.statistics.passed_attempts}</span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-gray-600">Students Failed:</span>
                        <span className="font-medium text-red-600">
                          {analytics.statistics.completed_attempts - analytics.statistics.passed_attempts}
                        </span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-gray-600">Completion Rate:</span>
                        <span className="font-medium">
                          {analytics.statistics.total_attempts > 0 
                            ? Math.round((analytics.statistics.completed_attempts / analytics.statistics.total_attempts) * 100)
                            : 0}%
                        </span>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            )}

            {/* Recent Attempts Tab */}
            {activeTab === 'attempts' && (
              <div>
                <h3 className="text-lg font-semibold text-gray-900 mb-4">Recent Quiz Attempts</h3>
                {analytics.recent_attempts && analytics.recent_attempts.length > 0 ? (
                  <div className="overflow-x-auto">
                    <table className="min-w-full divide-y divide-gray-200">
                      <thead className="bg-gray-50">
                        <tr>
                          <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                            Student
                          </th>
                          <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                            Score
                          </th>
                          <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                            Result
                          </th>
                          <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                            Duration
                          </th>
                          <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                            Completed At
                          </th>
                        </tr>
                      </thead>
                      <tbody className="bg-white divide-y divide-gray-200">
                        {analytics.recent_attempts.map((attempt, index) => (
                          <tr key={index} className="hover:bg-gray-50">
                            <td className="px-6 py-4 whitespace-nowrap">
                              <div className="text-sm font-medium text-gray-900">{attempt.user}</div>
                            </td>
                            <td className="px-6 py-4 whitespace-nowrap">
                              <div className={`text-sm font-medium ${getScoreColor(attempt.score, analytics.quiz.passing_score)}`}>
                                {attempt.score}%
                              </div>
                            </td>
                            <td className="px-6 py-4 whitespace-nowrap">
                              <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${
                                attempt.passed ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'
                              }`}>
                                {attempt.passed ? 'Passed' : 'Failed'}
                              </span>
                            </td>
                            <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                              {formatDuration(attempt.duration)}
                            </td>
                            <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                              {new Date(attempt.completed_at).toLocaleDateString()} {new Date(attempt.completed_at).toLocaleTimeString()}
                            </td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                ) : (
                  <div className="text-center py-8">
                    <div className="text-4xl mb-4">📋</div>
                    <h4 className="text-lg font-medium text-gray-900 mb-2">No attempts yet</h4>
                    <p className="text-gray-600">Students haven't taken this quiz yet</p>
                  </div>
                )}
              </div>
            )}

            {/* Question Analytics Tab */}
            {activeTab === 'questions' && (
              <div>
                <h3 className="text-lg font-semibold text-gray-900 mb-4">Question Performance Analytics</h3>
                {analytics.questions_analytics && analytics.questions_analytics.length > 0 ? (
                  <div className="space-y-4">
                    {analytics.questions_analytics.map((question, index) => (
                      <div key={question.question_id} className="bg-gray-50 rounded-lg p-4">
                        <div className="flex items-start justify-between">
                          <div className="flex-1">
                            <div className="flex items-center space-x-2 mb-2">
                              <span className="bg-blue-100 text-blue-800 text-xs font-medium px-2 py-1 rounded">
                                Question {index + 1}
                              </span>
                              <span className="text-xs text-gray-500">
                                {question.points} points
                              </span>
                            </div>
                            <h4 className="text-sm font-medium text-gray-900 mb-2">
                              {question.question_text}
                            </h4>
                            <div className="flex items-center space-x-4 text-sm text-gray-600">
                              <span>Total Answers: {question.total_answers}</span>
                              <span>Accuracy: {question.accuracy}%</span>
                            </div>
                          </div>
                          <div className="ml-4">
                            <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${getAccuracyColor(question.accuracy)}`}>
                              {question.accuracy}% Correct
                            </span>
                          </div>
                        </div>
                        
                        {/* Accuracy Bar */}
                        <div className="mt-3">
                          <div className="bg-gray-200 rounded-full h-2">
                            <div 
                              className={`h-2 rounded-full ${
                                question.accuracy >= 80 ? 'bg-green-500' :
                                question.accuracy >= 60 ? 'bg-yellow-500' : 'bg-red-500'
                              }`}
                              style={{ width: `${question.accuracy}%` }}
                            ></div>
                          </div>
                        </div>
                      </div>
                    ))}
                  </div>
                ) : (
                  <div className="text-center py-8">
                    <div className="text-4xl mb-4">📊</div>
                    <h4 className="text-lg font-medium text-gray-900 mb-2">No question data available</h4>
                    <p className="text-gray-600">Question analytics will appear after students complete the quiz</p>
                  </div>
                )}
              </div>
            )}

            {/* Score Distribution Tab */}
            {activeTab === 'distribution' && (
              <div>
                <h3 className="text-lg font-semibold text-gray-900 mb-4">Score Distribution</h3>
                <div className="grid grid-cols-1 md:grid-cols-5 gap-4">
                  {Object.entries(analytics.score_distribution).map(([range, count]) => {
                    const total = analytics.statistics.completed_attempts;
                    const percentage = total > 0 ? Math.round((count / total) * 100) : 0;
                    
                    return (
                      <div key={range} className="bg-gray-50 rounded-lg p-4 text-center">
                        <div className="text-2xl font-bold text-gray-900">{count}</div>
                        <div className="text-sm text-gray-600">{range}%</div>
                        <div className="text-xs text-gray-500">{percentage}% of total</div>
                        <div className="mt-2 bg-gray-200 rounded-full h-2">
                          <div 
                            className="bg-blue-500 h-2 rounded-full"
                            style={{ width: `${percentage}%` }}
                          ></div>
                        </div>
                      </div>
                    );
                  })}
                </div>
                
                {analytics.statistics.completed_attempts === 0 && (
                  <div className="text-center py-8">
                    <div className="text-4xl mb-4">📈</div>
                    <h4 className="text-lg font-medium text-gray-900 mb-2">No score data available</h4>
                    <p className="text-gray-600">Score distribution will appear after students complete the quiz</p>
                  </div>
                )}
              </div>
            )}
          </div>
        </div>

        {/* Footer Actions */}
        <div className="text-center space-x-4">
          <button
            onClick={() => navigate(`/edit-quiz/${id}`)}
            className="bg-blue-600 text-white px-6 py-2 rounded-md hover:bg-blue-700 transition-colors"
          >
            Edit Quiz
          </button>
          <button
            onClick={() => navigate(`/quiz-preview/${id}`)}
            className="bg-green-600 text-white px-6 py-2 rounded-md hover:bg-green-700 transition-colors"
          >
            Preview Quiz
          </button>
          <button
            onClick={() => navigate('/my-quizzes')}
            className="bg-gray-600 text-white px-6 py-2 rounded-md hover:bg-gray-700 transition-colors"
          >
            Back to My Quizzes
          </button>
        </div>
      </div>
    </div>
  );
};

export default QuizResults;
