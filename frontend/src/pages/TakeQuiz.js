import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import api from '../services/api';
import { toast } from 'react-hot-toast';

const TakeQuiz = () => {
  const { attemptId } = useParams();
  const navigate = useNavigate();
  
  const [quiz, setQuiz] = useState(null);
  const [questions, setQuestions] = useState([]);
  const [answers, setAnswers] = useState({});
  const [currentQuestion, setCurrentQuestion] = useState(0);
  const [timeRemaining, setTimeRemaining] = useState(null);
  const [loading, setLoading] = useState(true);
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState(null);

  useEffect(() => {
    fetchQuizData();
  }, [attemptId]);

  useEffect(() => {
    if (timeRemaining !== null && timeRemaining > 0) {
      const timer = setInterval(() => {
        setTimeRemaining(prev => {
          if (prev <= 1) {
            handleAutoSubmit();
            return 0;
          }
          return prev - 1;
        });
      }, 60000); // Update every minute

      return () => clearInterval(timer);
    }
  }, [timeRemaining]);

  const fetchQuizData = async () => {
    try {
      setLoading(true);
      const response = await api.get(`/api/quizzes/api/attempt/${attemptId}/quiz/`);
      const data = response.data;
      
      setQuiz(data.quiz);
      setQuestions(data.questions);
      setTimeRemaining(data.quiz.time_remaining);
      
      // Initialize answers object
      const initialAnswers = {};
      data.questions.forEach(question => {
        initialAnswers[question.id] = {
          question_id: question.id,
          answer: question.question_type === 'multiple_choice' || question.question_type === 'true_false' 
            ? { choice_id: null }
            : { text: '' }
        };
      });
      setAnswers(initialAnswers);
      
    } catch (error) {
      setError(error.response?.data?.error || 'Failed to load quiz');
      toast.error('Failed to load quiz');
    } finally {
      setLoading(false);
    }
  };

  const handleAnswerChange = (questionId, answerData) => {
    setAnswers(prev => ({
      ...prev,
      [questionId]: {
        ...prev[questionId],
        answer: answerData
      }
    }));
  };

  const saveAnswer = async (questionId) => {
    try {
      await api.post(`/api/quizzes/api/attempt/${attemptId}/answer/`, answers[questionId]);
      // Could show a subtle "saved" indicator here
    } catch (error) {
      console.error('Failed to save answer:', error);
      // Don't show error to user for auto-save failures
    }
  };

  const handleNext = () => {
    if (currentQuestion < questions.length - 1) {
      saveAnswer(questions[currentQuestion].id);
      setCurrentQuestion(prev => prev + 1);
    }
  };

  const handlePrevious = () => {
    if (currentQuestion > 0) {
      saveAnswer(questions[currentQuestion].id);
      setCurrentQuestion(prev => prev - 1);
    }
  };

  const handleQuestionJump = (index) => {
    saveAnswer(questions[currentQuestion].id);
    setCurrentQuestion(index);
  };

  const handleAutoSubmit = async () => {
    toast.error('Time limit reached. Quiz is being auto-submitted.');
    await handleSubmit();
  };

  const handleSubmit = async () => {
    if (submitting) return;
    
    setSubmitting(true);
    try {
      // Save current answer first
      if (questions[currentQuestion]) {
        await saveAnswer(questions[currentQuestion].id);
      }

      // Submit the quiz
      const response = await api.post(`/api/quizzes/api/attempt/${attemptId}/submit/`);
      
      toast.success('Quiz submitted successfully!');
      navigate(`/quiz-result/${attemptId}`, { 
        state: { result: response.data.result }
      });
      
    } catch (error) {
      toast.error(error.response?.data?.error || 'Failed to submit quiz');
      setSubmitting(false);
    }
  };

  const formatTime = (minutes) => {
    const hours = Math.floor(minutes / 60);
    const mins = minutes % 60;
    if (hours > 0) {
      return `${hours}h ${mins}m`;
    }
    return `${mins}m`;
  };

  const getAnsweredCount = () => {
    return Object.values(answers).filter(answer => {
      if (answer.answer.choice_id) return true;
      if (answer.answer.text && answer.answer.text.trim()) return true;
      return false;
    }).length;
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-500 mx-auto"></div>
          <p className="mt-4 text-gray-600">Loading quiz...</p>
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

  if (!questions.length) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <p className="text-gray-600">No questions found for this quiz.</p>
        </div>
      </div>
    );
  }

  const currentQ = questions[currentQuestion];

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <div className="bg-white shadow-sm border-b">
        <div className="max-w-6xl mx-auto px-4 py-4">
          <div className="flex justify-between items-center">
            <div>
              <h1 className="text-xl font-bold text-gray-900">{quiz?.title}</h1>
              <p className="text-sm text-gray-600">
                Question {currentQuestion + 1} of {questions.length}
                {timeRemaining !== null && (
                  <span className={`ml-4 font-medium ${timeRemaining < 10 ? 'text-red-600' : 'text-blue-600'}`}>
                    ⏰ Time remaining: {formatTime(timeRemaining)}
                  </span>
                )}
              </p>
            </div>
            <div className="text-right">
              <div className="text-sm text-gray-600">
                Progress: {getAnsweredCount()}/{questions.length} answered
              </div>
              <div className="w-32 bg-gray-200 rounded-full h-2 mt-1">
                <div 
                  className="bg-blue-600 h-2 rounded-full transition-all duration-300"
                  style={{ width: `${(getAnsweredCount() / questions.length) * 100}%` }}
                ></div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <div className="max-w-6xl mx-auto px-4 py-6">
        <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
          
          {/* Question Navigation Sidebar */}
          <div className="lg:col-span-1">
            <div className="bg-white rounded-lg shadow-sm p-4 sticky top-4">
              <h3 className="font-semibold text-gray-900 mb-3">Questions</h3>
              <div className="grid grid-cols-5 lg:grid-cols-4 gap-2">
                {questions.map((_, index) => {
                  const isAnswered = answers[questions[index].id] && (
                    answers[questions[index].id].answer.choice_id ||
                    (answers[questions[index].id].answer.text && answers[questions[index].id].answer.text.trim())
                  );
                  
                  return (
                    <button
                      key={index}
                      onClick={() => handleQuestionJump(index)}
                      className={`w-8 h-8 rounded text-sm font-medium transition-colors ${
                        index === currentQuestion
                          ? 'bg-blue-600 text-white'
                          : isAnswered
                          ? 'bg-green-100 text-green-700 border border-green-300'
                          : 'bg-gray-100 text-gray-700 border border-gray-300 hover:bg-gray-200'
                      }`}
                    >
                      {index + 1}
                    </button>
                  );
                })}
              </div>
              
              <div className="mt-4 space-y-2 text-xs">
                <div className="flex items-center">
                  <div className="w-3 h-3 bg-blue-600 rounded mr-2"></div>
                  <span>Current</span>
                </div>
                <div className="flex items-center">
                  <div className="w-3 h-3 bg-green-100 border border-green-300 rounded mr-2"></div>
                  <span>Answered</span>
                </div>
                <div className="flex items-center">
                  <div className="w-3 h-3 bg-gray-100 border border-gray-300 rounded mr-2"></div>
                  <span>Not answered</span>
                </div>
              </div>

              <button
                onClick={handleSubmit}
                disabled={submitting}
                className={`w-full mt-6 py-2 px-4 rounded-md font-medium transition-colors ${
                  submitting
                    ? 'bg-gray-400 text-gray-200 cursor-not-allowed'
                    : 'bg-green-600 text-white hover:bg-green-700'
                }`}
              >
                {submitting ? 'Submitting...' : 'Submit Quiz'}
              </button>
            </div>
          </div>

          {/* Main Question Area */}
          <div className="lg:col-span-3">
            <div className="bg-white rounded-lg shadow-sm p-6">
              
              {/* Question */}
              <div className="mb-6">
                <div className="flex justify-between items-start mb-4">
                  <h2 className="text-lg font-semibold text-gray-900">
                    Question {currentQuestion + 1}
                  </h2>
                  <span className="bg-blue-100 text-blue-800 text-xs font-medium px-2.5 py-0.5 rounded">
                    {currentQ.points} {currentQ.points === 1 ? 'point' : 'points'}
                  </span>
                </div>
                
                <div className="prose max-w-none">
                  <p className="text-gray-800 leading-relaxed whitespace-pre-wrap">
                    {currentQ.question_text}
                  </p>
                </div>
              </div>

              {/* Answer Options */}
              <div className="mb-8">
                {currentQ.question_type === 'multiple_choice' && (
                  <div className="space-y-3">
                    {currentQ.choices.map((choice) => (
                      <label
                        key={choice.id}
                        className="flex items-start p-3 border border-gray-200 rounded-lg hover:bg-gray-50 cursor-pointer transition-colors"
                      >
                        <input
                          type="radio"
                          name={`question_${currentQ.id}`}
                          value={choice.id}
                          checked={answers[currentQ.id]?.answer.choice_id === choice.id}
                          onChange={() => handleAnswerChange(currentQ.id, { choice_id: choice.id })}
                          className="mt-1 mr-3 h-4 w-4 text-blue-600"
                        />
                        <span className="text-gray-800">{choice.choice_text}</span>
                      </label>
                    ))}
                  </div>
                )}

                {currentQ.question_type === 'true_false' && (
                  <div className="space-y-3">
                    {currentQ.choices.map((choice) => (
                      <label
                        key={choice.id}
                        className="flex items-start p-3 border border-gray-200 rounded-lg hover:bg-gray-50 cursor-pointer transition-colors"
                      >
                        <input
                          type="radio"
                          name={`question_${currentQ.id}`}
                          value={choice.id}
                          checked={answers[currentQ.id]?.answer.choice_id === choice.id}
                          onChange={() => handleAnswerChange(currentQ.id, { choice_id: choice.id })}
                          className="mt-1 mr-3 h-4 w-4 text-blue-600"
                        />
                        <span className="text-gray-800 font-medium">{choice.choice_text}</span>
                      </label>
                    ))}
                  </div>
                )}

                {(currentQ.question_type === 'short_answer' || currentQ.question_type === 'essay') && (
                  <div>
                    <textarea
                      value={answers[currentQ.id]?.answer.text || ''}
                      onChange={(e) => handleAnswerChange(currentQ.id, { text: e.target.value })}
                      rows={currentQ.question_type === 'essay' ? 8 : 3}
                      className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500"
                      placeholder="Type your answer here..."
                    />
                  </div>
                )}
              </div>

              {/* Navigation */}
              <div className="flex justify-between items-center pt-6 border-t border-gray-200">
                <button
                  onClick={handlePrevious}
                  disabled={currentQuestion === 0}
                  className={`px-4 py-2 rounded-md font-medium transition-colors ${
                    currentQuestion === 0
                      ? 'bg-gray-100 text-gray-400 cursor-not-allowed'
                      : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
                  }`}
                >
                  ← Previous
                </button>

                <span className="text-sm text-gray-600">
                  {currentQuestion + 1} of {questions.length}
                </span>

                <button
                  onClick={handleNext}
                  disabled={currentQuestion === questions.length - 1}
                  className={`px-4 py-2 rounded-md font-medium transition-colors ${
                    currentQuestion === questions.length - 1
                      ? 'bg-gray-100 text-gray-400 cursor-not-allowed'
                      : 'bg-blue-600 text-white hover:bg-blue-700'
                  }`}
                >
                  Next →
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default TakeQuiz;
