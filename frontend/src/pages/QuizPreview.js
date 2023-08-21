import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { toast } from 'react-hot-toast';
import api from '../services/api';

const QuizPreview = () => {
  const { id } = useParams();
  const navigate = useNavigate();
  const [quiz, setQuiz] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const loadQuizPreview = async () => {
      try {
        setLoading(true);
        const response = await api.get(`/api/quizzes/api/quiz/${id}/preview/`);
        setQuiz(response.data);
      } catch (error) {
        setError(error.response?.data?.error || 'Failed to load quiz preview');
        toast.error('Failed to load quiz preview');
      } finally {
        setLoading(false);
      }
    };

    loadQuizPreview();
  }, [id]);

  const getQuestionTypeIcon = (type) => {
    switch (type) {
      case 'multiple_choice':
        return '⚪';
      case 'true_false':
        return '✓/✗';
      default:
        return '❓';
    }
  };

  const getQuestionTypeLabel = (type) => {
    switch (type) {
      case 'multiple_choice':
        return 'Multiple Choice';
      case 'true_false':
        return 'True/False';
      default:
        return 'Unknown';
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-500 mx-auto"></div>
          <p className="mt-4 text-gray-600">Loading quiz preview...</p>
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
      <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* Header */}
        <div className="bg-white rounded-lg shadow-sm mb-8">
          <div className="px-6 py-4 border-b border-gray-200">
            <div className="flex items-center justify-between">
              <div>
                <h1 className="text-2xl font-bold text-gray-900">Quiz Preview</h1>
                <p className="text-gray-600">Preview how your quiz will appear to students</p>
              </div>
              <div className="flex space-x-3">
                <button
                  onClick={() => navigate(`/edit-quiz/${quiz.id}`)}
                  className="bg-blue-600 text-white px-4 py-2 rounded-md hover:bg-blue-700 transition-colors"
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

          {/* Quiz Details */}
          <div className="px-6 py-4">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div>
                <h2 className="text-xl font-semibold text-gray-900 mb-2">{quiz.title}</h2>
                <p className="text-gray-600 mb-4">{quiz.description || 'No description provided'}</p>
                
                <div className="space-y-2 text-sm">
                  <div className="flex items-center">
                    <span className="font-medium text-gray-700 w-24">Type:</span>
                    <span className={`px-2 py-1 rounded-full text-xs font-medium ${
                      quiz.quiz_type === 'assessment' ? 'bg-blue-100 text-blue-800' :
                      quiz.quiz_type === 'practice' ? 'bg-green-100 text-green-800' :
                      'bg-gray-100 text-gray-800'
                    }`}>
                      {quiz.quiz_type.charAt(0).toUpperCase() + quiz.quiz_type.slice(1)}
                    </span>
                  </div>
                  <div className="flex items-center">
                    <span className="font-medium text-gray-700 w-24">Status:</span>
                    <span className={`px-2 py-1 rounded-full text-xs font-medium ${
                      quiz.is_active ? 'bg-green-100 text-green-800' : 'bg-gray-100 text-gray-800'
                    }`}>
                      {quiz.is_active ? 'Active' : 'Inactive'}
                    </span>
                  </div>
                  <div className="flex items-center">
                    <span className="font-medium text-gray-700 w-24">Visibility:</span>
                    <span className="text-gray-600">{quiz.visibility}</span>
                  </div>
                </div>
              </div>

              <div className="space-y-3 text-sm">
                <div className="flex items-center justify-between">
                  <span className="font-medium text-gray-700">⏱️ Duration:</span>
                  <span className="text-gray-600">{quiz.duration_minutes ? `${quiz.duration_minutes} minutes` : 'No limit'}</span>
                </div>
                <div className="flex items-center justify-between">
                  <span className="font-medium text-gray-700">🔄 Max Attempts:</span>
                  <span className="text-gray-600">{quiz.max_attempts || 'Unlimited'}</span>
                </div>
                <div className="flex items-center justify-between">
                  <span className="font-medium text-gray-700">📊 Passing Score:</span>
                  <span className="text-gray-600">{quiz.passing_score}%</span>
                </div>
                <div className="flex items-center justify-between">
                  <span className="font-medium text-gray-700">📝 Questions:</span>
                  <span className="text-gray-600">{quiz.question_count}</span>
                </div>
                <div className="flex items-center justify-between">
                  <span className="font-medium text-gray-700">🎯 Total Points:</span>
                  <span className="text-gray-600">{quiz.total_points}</span>
                </div>
                <div className="flex items-center justify-between">
                  <span className="font-medium text-gray-700">🔀 Randomize:</span>
                  <span className="text-gray-600">{quiz.randomize_questions ? 'Yes' : 'No'}</span>
                </div>
                <div className="flex items-center justify-between">
                  <span className="font-medium text-gray-700">👁️ Allow Review:</span>
                  <span className="text-gray-600">{quiz.allow_review ? 'Yes' : 'No'}</span>
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* Questions Preview */}
        <div className="bg-white rounded-lg shadow-sm">
          <div className="px-6 py-4 border-b border-gray-200">
            <h3 className="text-lg font-semibold text-gray-900">Questions Preview</h3>
            <p className="text-gray-600">This is how questions will appear to students</p>
          </div>

          <div className="px-6 py-4">
            {quiz.questions && quiz.questions.length > 0 ? (
              <div className="space-y-6">
                {quiz.questions.map((question, index) => (
                  <div key={question.id} className="border border-gray-200 rounded-lg p-4">
                    <div className="flex items-start justify-between mb-3">
                      <div className="flex items-center space-x-2">
                        <span className="bg-blue-100 text-blue-800 text-xs font-medium px-2 py-1 rounded">
                          Question {index + 1}
                        </span>
                        <span className="text-xs text-gray-500">
                          {getQuestionTypeIcon(question.question_type)} {getQuestionTypeLabel(question.question_type)}
                        </span>
                      </div>
                      <span className="text-xs text-gray-500 bg-gray-100 px-2 py-1 rounded">
                        {question.points} {question.points === 1 ? 'point' : 'points'}
                      </span>
                    </div>

                    <h4 className="text-base font-medium text-gray-900 mb-3">{question.text}</h4>

                    {question.question_type === 'multiple_choice' && (
                      <div className="space-y-2">
                        {question.choices.map((choice, choiceIndex) => (
                          <div key={choice.id} className="flex items-center space-x-3">
                            <div className={`w-4 h-4 rounded-full border-2 flex items-center justify-center ${
                              choice.is_correct ? 'border-green-500 bg-green-100' : 'border-gray-300'
                            }`}>
                              {choice.is_correct && (
                                <div className="w-2 h-2 rounded-full bg-green-500"></div>
                              )}
                            </div>
                            <span className={`text-sm ${choice.is_correct ? 'text-green-700 font-medium' : 'text-gray-700'}`}>
                              {choice.text}
                            </span>
                            {choice.is_correct && (
                              <span className="text-xs text-green-600 bg-green-100 px-2 py-0.5 rounded">
                                Correct
                              </span>
                            )}
                          </div>
                        ))}
                      </div>
                    )}

                    {question.question_type === 'true_false' && (
                      <div className="space-y-2">
                        {question.choices.map((choice) => (
                          <div key={choice.id} className="flex items-center space-x-3">
                            <div className={`w-4 h-4 rounded border-2 flex items-center justify-center ${
                              choice.is_correct ? 'border-green-500 bg-green-100' : 'border-gray-300'
                            }`}>
                              {choice.is_correct && (
                                <svg className="w-3 h-3 text-green-500" fill="currentColor" viewBox="0 0 20 20">
                                  <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
                                </svg>
                              )}
                            </div>
                            <span className={`text-sm ${choice.is_correct ? 'text-green-700 font-medium' : 'text-gray-700'}`}>
                              {choice.text}
                            </span>
                            {choice.is_correct && (
                              <span className="text-xs text-green-600 bg-green-100 px-2 py-0.5 rounded">
                                Correct
                              </span>
                            )}
                          </div>
                        ))}
                      </div>
                    )}



                    {question.explanation && (
                      <div className="mt-3 p-3 bg-blue-50 rounded-lg">
                        <h5 className="text-sm font-medium text-blue-800 mb-1">Explanation:</h5>
                        <p className="text-sm text-blue-700">{question.explanation}</p>
                      </div>
                    )}
                  </div>
                ))}
              </div>
            ) : (
              <div className="text-center py-8">
                <div className="text-4xl mb-4">📝</div>
                <h4 className="text-lg font-medium text-gray-900 mb-2">No questions added yet</h4>
                <p className="text-gray-600 mb-4">Add questions to this quiz to see the preview</p>
                <button
                  onClick={() => navigate(`/edit-quiz/${quiz.id}`)}
                  className="bg-blue-600 text-white px-4 py-2 rounded-md hover:bg-blue-700 transition-colors"
                >
                  Add Questions
                </button>
              </div>
            )}
          </div>
        </div>

        {/* Footer Actions */}
        <div className="mt-8 text-center space-x-4">
          <button
            onClick={() => navigate(`/edit-quiz/${quiz.id}`)}
            className="bg-blue-600 text-white px-6 py-2 rounded-md hover:bg-blue-700 transition-colors"
          >
            Edit Quiz
          </button>
          <button
            onClick={() => navigate(`/quiz-results/${quiz.id}`)}
            className="bg-purple-600 text-white px-6 py-2 rounded-md hover:bg-purple-700 transition-colors"
          >
            View Results
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

export default QuizPreview;
