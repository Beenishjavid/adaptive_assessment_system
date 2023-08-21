import React, { useState, useEffect } from 'react';
import { useParams, useNavigate, useLocation } from 'react-router-dom';
import api from '../services/api';
import { toast } from 'react-hot-toast';

const QuizResult = () => {
  const { attemptId } = useParams();
  const navigate = useNavigate();
  const location = useLocation();
  
  const [result, setResult] = useState(location.state?.result || null);
  const [detailedResult, setDetailedResult] = useState(null);
  const [loading, setLoading] = useState(!result);
  const [error, setError] = useState(null);
  const [showAnswers, setShowAnswers] = useState(false);

  useEffect(() => {
    fetchDetailedResult();
  }, [attemptId]);

  const fetchDetailedResult = async () => {
    try {
      setLoading(true);
      const response = await api.get(`/api/quizzes/api/attempt/${attemptId}/result/`);
      setDetailedResult(response.data);
      
      if (!result) {
        setResult(response.data.attempt);
      }
      
    } catch (error) {
      setError(error.response?.data?.error || 'Failed to load quiz result');
      toast.error('Failed to load quiz result');
    } finally {
      setLoading(false);
    }
  };

  const getScoreColor = (score, passingScore) => {
    if (score >= passingScore) {
      return 'text-green-600';
    } else if (score >= passingScore * 0.7) {
      return 'text-yellow-600';
    } else {
      return 'text-red-600';
    }
  };

  const getGradeIcon = (score, passingScore) => {
    if (score >= passingScore) {
      return '🎉';
    } else if (score >= passingScore * 0.7) {
      return '⚠️';
    } else {
      return '❌';
    }
  };

  const formatDuration = (startTime, endTime) => {
    if (!startTime || !endTime) return 'N/A';
    
    const start = new Date(startTime);
    const end = new Date(endTime);
    const durationMs = end - start;
    const minutes = Math.floor(durationMs / (1000 * 60));
    const seconds = Math.floor((durationMs % (1000 * 60)) / 1000);
    
    return `${minutes}m ${seconds}s`;
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-500 mx-auto"></div>
          <p className="mt-4 text-gray-600">Loading results...</p>
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
            onClick={() => navigate('/dashboard')}
            className="mt-4 bg-red-500 text-white px-4 py-2 rounded hover:bg-red-600"
          >
            Back to Dashboard
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50 py-8">
      <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8">
        
        {/* Header */}
        <div className="text-center mb-8">
          <div className="text-6xl mb-4">
            {getGradeIcon(result?.score || 0, result?.passing_score || 70)}
          </div>
          <h1 className="text-3xl font-bold text-gray-900">Quiz Complete!</h1>
          <p className="text-gray-600 mt-2">{detailedResult?.attempt?.quiz_title}</p>
        </div>

        {/* Score Card */}
        <div className="bg-white rounded-lg shadow-lg p-8 mb-8">
          <div className="text-center">
            <div className={`text-6xl font-bold mb-4 ${getScoreColor(result?.score || 0, result?.passing_score || 70)}`}>
              {Math.round(result?.score || 0)}%
            </div>
            
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mt-8">
              <div className="text-center">
                <div className="text-2xl font-bold text-gray-900">
                  {result?.earned_points || 0}
                </div>
                <div className="text-sm text-gray-600">Points Earned</div>
              </div>
              
              <div className="text-center">
                <div className="text-2xl font-bold text-gray-900">
                  {result?.total_points || 0}
                </div>
                <div className="text-sm text-gray-600">Total Points</div>
              </div>
              
              <div className="text-center">
                <div className={`text-2xl font-bold ${result?.passed ? 'text-green-600' : 'text-red-600'}`}>
                  {result?.passed ? 'PASSED' : 'FAILED'}
                </div>
                <div className="text-sm text-gray-600">
                  Passing Score: {result?.passing_score || 70}%
                </div>
              </div>
            </div>

            {/* Status Message */}
            <div className={`mt-6 p-4 rounded-lg ${
              result?.passed 
                ? 'bg-green-50 border border-green-200' 
                : 'bg-red-50 border border-red-200'
            }`}>
              <p className={`font-medium ${
                result?.passed ? 'text-green-800' : 'text-red-800'
              }`}>
                {result?.passed 
                  ? '🎉 Congratulations! You passed the quiz!' 
                  : '😔 You did not meet the passing requirements this time.'
                }
              </p>
              {!result?.passed && (
                <p className="text-sm text-gray-600 mt-1">
                  Don't worry! You can review the answers below and try again if attempts are remaining.
                </p>
              )}
            </div>
          </div>
        </div>

        {/* Quiz Details */}
        <div className="bg-white rounded-lg shadow-sm p-6 mb-8">
          <h2 className="text-lg font-semibold text-gray-900 mb-4">Quiz Details</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-sm">
            <div>
              <span className="font-medium text-gray-700">Started:</span>
              <span className="ml-2 text-gray-600">
                {detailedResult?.attempt?.started_at 
                  ? new Date(detailedResult.attempt.started_at).toLocaleString()
                  : 'N/A'
                }
              </span>
            </div>
            <div>
              <span className="font-medium text-gray-700">Completed:</span>
              <span className="ml-2 text-gray-600">
                {detailedResult?.attempt?.finished_at 
                  ? new Date(detailedResult.attempt.finished_at).toLocaleString()
                  : 'N/A'
                }
              </span>
            </div>
            <div>
              <span className="font-medium text-gray-700">Duration:</span>
              <span className="ml-2 text-gray-600">
                {formatDuration(
                  detailedResult?.attempt?.started_at,
                  detailedResult?.attempt?.finished_at
                )}
              </span>
            </div>
            <div>
              <span className="font-medium text-gray-700">Time Limit:</span>
              <span className="ml-2 text-gray-600">
                {detailedResult?.attempt?.duration_minutes 
                  ? `${detailedResult.attempt.duration_minutes} minutes`
                  : 'No limit'
                }
              </span>
            </div>
          </div>
        </div>

        {/* Answer Review */}
        {detailedResult?.answers && (
          <div className="bg-white rounded-lg shadow-sm p-6 mb-8">
            <div className="flex justify-between items-center mb-6">
              <h2 className="text-lg font-semibold text-gray-900">Answer Review</h2>
              <button
                onClick={() => setShowAnswers(!showAnswers)}
                className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 transition-colors"
              >
                {showAnswers ? 'Hide Answers' : 'Show Answers'}
              </button>
            </div>

            {showAnswers && (
              <div className="space-y-6">
                {detailedResult.answers.map((answer, index) => (
                  <div 
                    key={answer.question.id}
                    className={`border rounded-lg p-4 ${
                      answer.is_correct 
                        ? 'border-green-200 bg-green-50' 
                        : 'border-red-200 bg-red-50'
                    }`}
                  >
                    <div className="flex justify-between items-start mb-3">
                      <h3 className="font-medium text-gray-900">
                        Question {index + 1}
                      </h3>
                      <div className="flex items-center space-x-2">
                        <span className={`text-sm font-medium ${
                          answer.is_correct ? 'text-green-600' : 'text-red-600'
                        }`}>
                          {answer.is_correct ? '✓ Correct' : '✗ Incorrect'}
                        </span>
                        <span className="text-sm text-gray-600">
                          {answer.points_earned || 0}/{answer.question.marks} pts
                        </span>
                      </div>
                    </div>

                    <p className="text-gray-800 mb-4 whitespace-pre-wrap">
                      {answer.question.question_text}
                    </p>

                    {/* User's Answer */}
                    <div className="mb-3">
                      <p className="text-sm font-medium text-gray-700 mb-1">Your Answer:</p>
                      <div className={`p-2 rounded ${
                        answer.is_correct ? 'bg-green-100' : 'bg-red-100'
                      }`}>
                        {answer.selected_choice ? (
                          <p className="text-gray-800">{answer.selected_choice.choice_text}</p>
                        ) : (
                          <p className="text-gray-800">{answer.user_answer || 'No answer provided'}</p>
                        )}
                      </div>
                    </div>

                    {/* Correct Answer (for MCQ) */}
                    {answer.correct_choices && answer.correct_choices.length > 0 && (
                      <div className="mb-3">
                        <p className="text-sm font-medium text-gray-700 mb-1">Correct Answer:</p>
                        <div className="p-2 bg-green-100 rounded">
                          {answer.correct_choices.map((choice, idx) => (
                            <p key={choice.id} className="text-green-800">
                              {choice.choice_text}
                            </p>
                          ))}
                        </div>
                      </div>
                    )}

                    {/* Explanation */}
                    {answer.question.explanation && (
                      <div>
                        <p className="text-sm font-medium text-gray-700 mb-1">Explanation:</p>
                        <div className="p-2 bg-blue-50 rounded">
                          <p className="text-gray-800 text-sm">{answer.question.explanation}</p>
                        </div>
                      </div>
                    )}
                  </div>
                ))}
              </div>
            )}
          </div>
        )}

        {/* Action Buttons */}
        <div className="flex justify-center space-x-4">
          <button
            onClick={() => navigate('/dashboard')}
            className="px-6 py-2 bg-gray-600 text-white rounded-md hover:bg-gray-700 transition-colors"
          >
            Back to Dashboard
          </button>
          
          <button
            onClick={() => navigate('/my-results')}
            className="px-6 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 transition-colors"
          >
            View All Results
          </button>
          
          {!result?.passed && (
            <button
              onClick={() => navigate(`/quiz/${detailedResult?.attempt?.quiz?.id}`)}
              className="px-6 py-2 bg-green-600 text-white rounded-md hover:bg-green-700 transition-colors"
            >
              Try Again
            </button>
          )}
        </div>
      </div>
    </div>
  );
};

export default QuizResult;
