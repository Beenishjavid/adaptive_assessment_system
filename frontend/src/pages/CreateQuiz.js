import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import api from '../services/api';
import { toast } from 'react-hot-toast';

const CreateQuiz = () => {
  const navigate = useNavigate();
  const [loading, setLoading] = useState(false);
  const [quiz, setQuiz] = useState({
    title: '',
    description: '',
    duration_minutes: 60,
    max_attempts: 1,
    passing_score: 70,
    quiz_type: 'assessment',
    visibility: 'public',
    randomize_questions: false,
    allow_review: false,
    show_results_immediately: true,
    allow_review_answers: true
  });

  const [questions, setQuestions] = useState([
    {
      question_text: '',
      question_type: 'multiple_choice',
      marks: 1,
      explanation: '',
      choices: [
        { choice_text: '', is_correct: false },
        { choice_text: '', is_correct: false },
        { choice_text: '', is_correct: false },
        { choice_text: '', is_correct: false }
      ]
    }
  ]);

  const handleQuizChange = (field, value) => {
    setQuiz(prev => ({ ...prev, [field]: value }));
  };

  const handleQuestionChange = (questionIndex, field, value) => {
    setQuestions(prev => {
      const updated = [...prev];
      updated[questionIndex] = { ...updated[questionIndex], [field]: value };
      return updated;
    });
  };

  const handleChoiceChange = (questionIndex, choiceIndex, field, value) => {
    setQuestions(prev => {
      const updated = [...prev];
      updated[questionIndex].choices[choiceIndex] = {
        ...updated[questionIndex].choices[choiceIndex],
        [field]: value
      };
      return updated;
    });
  };

  const addQuestion = () => {
    setQuestions(prev => [...prev, {
      question_text: '',
      question_type: 'multiple_choice',
      marks: 1,
      explanation: '',
      choices: [
        { choice_text: '', is_correct: false },
        { choice_text: '', is_correct: false },
        { choice_text: '', is_correct: false },
        { choice_text: '', is_correct: false }
      ]
    }]);
  };

  const removeQuestion = (index) => {
    setQuestions(prev => prev.filter((_, i) => i !== index));
  };

  const addChoice = (questionIndex) => {
    setQuestions(prev => {
      const updated = [...prev];
      updated[questionIndex].choices.push({ choice_text: '', is_correct: false });
      return updated;
    });
  };

  const removeChoice = (questionIndex, choiceIndex) => {
    setQuestions(prev => {
      const updated = [...prev];
      updated[questionIndex].choices = updated[questionIndex].choices.filter((_, i) => i !== choiceIndex);
      return updated;
    });
  };

  const validateForm = () => {
    if (!quiz.title.trim()) {
      toast.error('Quiz title is required');
      return false;
    }

    for (let i = 0; i < questions.length; i++) {
      const question = questions[i];
      if (!question.question_text.trim()) {
        toast.error(`Question ${i + 1} text is required`);
        return false;
      }

      if (question.question_type === 'multiple_choice') {
        const hasCorrectAnswer = question.choices.some(choice => choice.is_correct);
        if (!hasCorrectAnswer) {
          toast.error(`Question ${i + 1} must have at least one correct answer`);
          return false;
        }

        const validChoices = question.choices.filter(choice => choice.choice_text.trim());
        if (validChoices.length < 2) {
          toast.error(`Question ${i + 1} must have at least 2 choices`);
          return false;
        }
      }
    }

    return true;
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    if (!validateForm()) return;

    setLoading(true);
    try {
      const quizData = {
        ...quiz,
        questions: questions.map(q => ({
          ...q,
          choices: q.question_type === 'multiple_choice' ? 
            q.choices.filter(choice => choice.choice_text.trim()) : []
        }))
      };

      const response = await api.post('/api/quizzes/api/quiz/create/', quizData);
      
      toast.success('Quiz created successfully!');
      navigate('/my-quizzes');
      
    } catch (error) {
      toast.error(error.response?.data?.error || 'Failed to create quiz');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gray-50 py-8">
      <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="bg-white shadow-lg rounded-lg overflow-hidden">
          {/* Header */}
          <div className="bg-blue-600 px-6 py-4">
            <h1 className="text-2xl font-bold text-white">Create New Quiz</h1>
            <p className="text-blue-100 mt-1">Design an engaging assessment for your students</p>
          </div>

          <form onSubmit={handleSubmit} className="p-6 space-y-8">
            {/* Quiz Details */}
            <div className="space-y-6">
              <h2 className="text-lg font-semibold text-gray-900 border-b border-gray-200 pb-2">
                Quiz Information
              </h2>
              
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Quiz Title *
                  </label>
                  <input
                    type="text"
                    value={quiz.title}
                    onChange={(e) => handleQuizChange('title', e.target.value)}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500"
                    placeholder="Enter quiz title"
                    required
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Quiz Type
                  </label>
                  <select
                    value={quiz.quiz_type}
                    onChange={(e) => handleQuizChange('quiz_type', e.target.value)}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500"
                  >
                    <option value="assessment">Assessment</option>
                    <option value="practice">Practice</option>
                    <option value="exam">Exam</option>
                    <option value="survey">Survey</option>
                  </select>
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Duration (minutes)
                  </label>
                  <input
                    type="number"
                    value={quiz.duration_minutes}
                    onChange={(e) => handleQuizChange('duration_minutes', parseInt(e.target.value))}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500"
                    min="1"
                    max="300"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Passing Score (%)
                  </label>
                  <input
                    type="number"
                    value={quiz.passing_score}
                    onChange={(e) => handleQuizChange('passing_score', parseInt(e.target.value))}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500"
                    min="0"
                    max="100"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Max Attempts
                  </label>
                  <input
                    type="number"
                    value={quiz.max_attempts}
                    onChange={(e) => handleQuizChange('max_attempts', parseInt(e.target.value))}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500"
                    min="1"
                    max="10"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Visibility
                  </label>
                  <select
                    value={quiz.visibility}
                    onChange={(e) => handleQuizChange('visibility', e.target.value)}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500"
                  >
                    <option value="public">Public</option>
                    <option value="private">Private</option>
                    <option value="group">Group Only</option>
                  </select>
                </div>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Description
                </label>
                <textarea
                  value={quiz.description}
                  onChange={(e) => handleQuizChange('description', e.target.value)}
                  rows={3}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500"
                  placeholder="Describe what this quiz covers..."
                />
              </div>

              {/* Quiz Settings */}
              <div className="space-y-3">
                <h3 className="text-md font-medium text-gray-900">Quiz Settings</h3>
                <div className="space-y-2">
                  <label className="flex items-center">
                    <input
                      type="checkbox"
                      checked={quiz.randomize_questions}
                      onChange={(e) => handleQuizChange('randomize_questions', e.target.checked)}
                      className="mr-2"
                    />
                    <span className="text-sm text-gray-700">Randomize question order</span>
                  </label>
                  <label className="flex items-center">
                    <input
                      type="checkbox"
                      checked={quiz.allow_review}
                      onChange={(e) => handleQuizChange('allow_review', e.target.checked)}
                      className="mr-2"
                    />
                    <span className="text-sm text-gray-700">Allow answer review</span>
                  </label>
                  <label className="flex items-center">
                    <input
                      type="checkbox"
                      checked={quiz.show_results_immediately}
                      onChange={(e) => handleQuizChange('show_results_immediately', e.target.checked)}
                      className="mr-2"
                    />
                    <span className="text-sm text-gray-700">Show results immediately after submission</span>
                  </label>
                  <label className="flex items-center">
                    <input
                      type="checkbox"
                      checked={quiz.allow_review_answers}
                      onChange={(e) => handleQuizChange('allow_review_answers', e.target.checked)}
                      className="mr-2"
                    />
                    <span className="text-sm text-gray-700">Allow students to review answers</span>
                  </label>
                </div>
              </div>
            </div>

            {/* Questions */}
            <div className="space-y-6">
              <div className="flex justify-between items-center border-b border-gray-200 pb-2">
                <h2 className="text-lg font-semibold text-gray-900">Questions</h2>
                <button
                  type="button"
                  onClick={addQuestion}
                  className="bg-green-500 text-white px-4 py-2 rounded-md hover:bg-green-600 transition-colors"
                >
                  + Add Question
                </button>
              </div>

              {questions.map((question, questionIndex) => (
                <div key={questionIndex} className="border border-gray-200 rounded-lg p-6 space-y-4">
                  <div className="flex justify-between items-start">
                    <h3 className="text-md font-medium text-gray-900">
                      Question {questionIndex + 1}
                    </h3>
                    {questions.length > 1 && (
                      <button
                        type="button"
                        onClick={() => removeQuestion(questionIndex)}
                        className="text-red-500 hover:text-red-700"
                      >
                        ✕ Remove
                      </button>
                    )}
                  </div>

                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <div className="md:col-span-2">
                      <label className="block text-sm font-medium text-gray-700 mb-2">
                        Question Text *
                      </label>
                      <textarea
                        value={question.question_text}
                        onChange={(e) => handleQuestionChange(questionIndex, 'question_text', e.target.value)}
                        rows={2}
                        className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500"
                        placeholder="Enter your question here..."
                        required
                      />
                    </div>

                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-2">
                        Question Type
                      </label>
                      <select
                        value={question.question_type}
                        onChange={(e) => handleQuestionChange(questionIndex, 'question_type', e.target.value)}
                        className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500"
                      >
                        <option value="multiple_choice">Multiple Choice</option>
                        <option value="true_false">True/False</option>
                        <option value="short_answer">Short Answer</option>
                        <option value="essay">Essay</option>
                      </select>
                    </div>

                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-2">
                        Points
                      </label>
                      <input
                        type="number"
                        value={question.marks}
                        onChange={(e) => handleQuestionChange(questionIndex, 'marks', parseInt(e.target.value))}
                        className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500"
                        min="1"
                        max="100"
                      />
                    </div>
                  </div>

                  {/* Choices for multiple choice questions */}
                  {question.question_type === 'multiple_choice' && (
                    <div className="space-y-3">
                      <div className="flex justify-between items-center">
                        <label className="block text-sm font-medium text-gray-700">
                          Answer Choices
                        </label>
                        <button
                          type="button"
                          onClick={() => addChoice(questionIndex)}
                          className="text-blue-500 hover:text-blue-700 text-sm"
                        >
                          + Add Choice
                        </button>
                      </div>
                      
                      {question.choices.map((choice, choiceIndex) => (
                        <div key={choiceIndex} className="flex items-center space-x-3">
                          <input
                            type="checkbox"
                            checked={choice.is_correct}
                            onChange={(e) => handleChoiceChange(questionIndex, choiceIndex, 'is_correct', e.target.checked)}
                            className="h-4 w-4 text-blue-600"
                          />
                          <input
                            type="text"
                            value={choice.choice_text}
                            onChange={(e) => handleChoiceChange(questionIndex, choiceIndex, 'choice_text', e.target.value)}
                            className="flex-1 px-3 py-2 border border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500"
                            placeholder={`Choice ${choiceIndex + 1}`}
                          />
                          {question.choices.length > 2 && (
                            <button
                              type="button"
                              onClick={() => removeChoice(questionIndex, choiceIndex)}
                              className="text-red-500 hover:text-red-700"
                            >
                              ✕
                            </button>
                          )}
                        </div>
                      ))}
                    </div>
                  )}

                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Explanation (Optional)
                    </label>
                    <textarea
                      value={question.explanation}
                      onChange={(e) => handleQuestionChange(questionIndex, 'explanation', e.target.value)}
                      rows={2}
                      className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500"
                      placeholder="Explain the correct answer..."
                    />
                  </div>
                </div>
              ))}
            </div>

            {/* Submit Buttons */}
            <div className="flex justify-end space-x-4 pt-6 border-t border-gray-200">
              <button
                type="button"
                onClick={() => navigate('/dashboard')}
                className="px-6 py-2 border border-gray-300 text-gray-700 rounded-md hover:bg-gray-50 transition-colors"
              >
                Cancel
              </button>
              <button
                type="submit"
                disabled={loading}
                className={`px-6 py-2 rounded-md text-white transition-colors ${
                  loading 
                    ? 'bg-gray-400 cursor-not-allowed' 
                    : 'bg-blue-600 hover:bg-blue-700'
                }`}
              >
                {loading ? 'Creating...' : 'Create Quiz'}
              </button>
            </div>
          </form>
        </div>
      </div>
    </div>
  );
};

export default CreateQuiz;
