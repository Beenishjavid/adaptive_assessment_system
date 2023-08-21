import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { toast } from 'react-hot-toast';
import api from '../services/api';

const EditQuiz = () => {
  const { id } = useParams();
  const navigate = useNavigate();
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState(null);

  // Form state
  const [formData, setFormData] = useState({
    title: '',
    description: '',
    duration_minutes: '',
    max_attempts: '',
    passing_score: 70,
    quiz_type: 'assessment',
    visibility: 'public',
    randomize_questions: false,
    allow_review: true,
    is_active: true
  });

  const [questions, setQuestions] = useState([]);
  const [showAddQuestion, setShowAddQuestion] = useState(false);
  const [editingQuestion, setEditingQuestion] = useState(null);

  // New question form state
  const [newQuestion, setNewQuestion] = useState({
    text: '',
    question_type: 'multiple_choice',
    points: 1,
    explanation: '',
    choices: [
      { text: '', is_correct: false },
      { text: '', is_correct: false }
    ]
  });

  useEffect(() => {
    const loadQuizData = async () => {
      try {
        setLoading(true);
        const response = await api.get(`/api/quizzes/api/quiz/${id}/edit/`);
        const quizData = response.data;
        
        setFormData({
          title: quizData.title,
          description: quizData.description,
          duration_minutes: quizData.duration_minutes || '',
          max_attempts: quizData.max_attempts || '',
          passing_score: quizData.passing_score,
          quiz_type: quizData.quiz_type,
          visibility: quizData.visibility,
          randomize_questions: quizData.randomize_questions,
          allow_review: quizData.allow_review,
          is_active: quizData.is_active
        });
        
        // Convert backend field names to frontend field names for editing
        const mappedQuestions = (quizData.questions || []).map(question => ({
          ...question,
          text: question.question_text || question.text,
          points: question.marks || question.points,
          choices: question.choices?.map(choice => ({
            ...choice,
            text: choice.choice_text || choice.text
          })) || []
        }));
        
        setQuestions(mappedQuestions);
      } catch (error) {
        setError(error.response?.data?.error || 'Failed to load quiz for editing');
        toast.error('Failed to load quiz for editing');
      } finally {
        setLoading(false);
      }
    };

    loadQuizData();
  }, [id]);

  const handleInputChange = (e) => {
    const { name, value, type, checked } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: type === 'checkbox' ? checked : value
    }));
  };

  const handleSaveQuiz = async () => {
    try {
      setSaving(true);
      
      // Convert frontend field names to backend field names
      const mappedQuestions = questions.map(question => ({
        ...question,
        question_text: question.text || question.question_text,
        marks: question.points || question.marks,
        choices: question.choices?.map(choice => ({
          ...choice,
          choice_text: choice.text || choice.choice_text
        })) || []
      }));
      
      const updateData = {
        ...formData,
        duration_minutes: formData.duration_minutes && formData.duration_minutes !== '' ? parseInt(formData.duration_minutes) : 60,
        max_attempts: formData.max_attempts && formData.max_attempts !== '' ? parseInt(formData.max_attempts) : 1,
        passing_score: formData.passing_score && formData.passing_score !== '' ? parseInt(formData.passing_score) : 60,
        questions: mappedQuestions
      };

      await api.put(`/api/quizzes/api/quiz/${id}/update/`, updateData);
      toast.success('Quiz updated successfully!');
      navigate('/my-quizzes');
    } catch (error) {
      console.error('Update error:', error.response?.data);
      toast.error(error.response?.data?.error || 'Failed to update quiz');
    } finally {
      setSaving(false);
    }
  };

  const handleQuestionChange = (field, value) => {
    setNewQuestion(prev => {
      const updated = { ...prev, [field]: value };
      
      // Initialize correct choices for true/false questions
      if (field === 'question_type' && value === 'true_false') {
        updated.choices = [
          { text: 'True', is_correct: false },
          { text: 'False', is_correct: false }
        ];
      } else if (field === 'question_type' && value === 'multiple_choice') {
        updated.choices = [
          { text: '', is_correct: false },
          { text: '', is_correct: false }
        ];
      }
      
      return updated;
    });
  };

  const handleChoiceChange = (index, field, value) => {
    setNewQuestion(prev => ({
      ...prev,
      choices: prev.choices.map((choice, i) => 
        i === index ? { ...choice, [field]: value } : choice
      )
    }));
  };

  const addChoice = () => {
    setNewQuestion(prev => ({
      ...prev,
      choices: [...prev.choices, { text: '', is_correct: false }]
    }));
  };

  const removeChoice = (index) => {
    if (newQuestion.choices.length > 2) {
      setNewQuestion(prev => ({
        ...prev,
        choices: prev.choices.filter((_, i) => i !== index)
      }));
    }
  };

  const handleAddQuestion = () => {
    if (!newQuestion.text.trim()) {
      toast.error('Question text is required');
      return;
    }

    if (newQuestion.question_type !== 'short_answer' && 
        !newQuestion.choices.some(choice => choice.is_correct)) {
      toast.error('At least one correct answer must be selected');
      return;
    }

    const questionToAdd = {
      ...newQuestion,
      id: editingQuestion ? editingQuestion.id : Date.now(), // Temporary ID for new questions
      choices: newQuestion.question_type === 'short_answer' ? [] : newQuestion.choices.filter(choice => choice.text.trim())
    };

    if (editingQuestion) {
      setQuestions(prev => prev.map(q => q.id === editingQuestion.id ? questionToAdd : q));
      setEditingQuestion(null);
    } else {
      setQuestions(prev => [...prev, questionToAdd]);
    }

    // Reset form
    setNewQuestion({
      text: '',
      question_type: 'multiple_choice',
      points: 1,
      explanation: '',
      choices: [
        { text: '', is_correct: false },
        { text: '', is_correct: false }
      ]
    });
    setShowAddQuestion(false);
  };

  const handleEditQuestion = (question) => {
    setEditingQuestion(question);
    setNewQuestion({
      text: question.text,
      question_type: question.question_type,
      points: question.points,
      explanation: question.explanation || '',
      choices: question.choices.length > 0 ? question.choices : [
        { text: '', is_correct: false },
        { text: '', is_correct: false }
      ]
    });
    setShowAddQuestion(true);
  };

  const handleDeleteQuestion = (questionId) => {
    if (window.confirm('Are you sure you want to delete this question?')) {
      setQuestions(prev => prev.filter(q => q.id !== questionId));
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-500 mx-auto"></div>
          <p className="mt-4 text-gray-600">Loading quiz for editing...</p>
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
        <div className="bg-white rounded-lg shadow-sm mb-8 p-6">
          <div className="flex items-center justify-between mb-4">
            <div>
              <h1 className="text-2xl font-bold text-gray-900">Edit Quiz</h1>
              <p className="text-gray-600">Modify quiz settings and questions</p>
            </div>
            <div className="flex space-x-3">
              <button
                onClick={() => navigate(`/quiz-preview/${id}`)}
                className="bg-gray-600 text-white px-4 py-2 rounded-md hover:bg-gray-700 transition-colors"
              >
                Preview Quiz
              </button>
              <button
                onClick={() => navigate('/my-quizzes')}
                className="bg-gray-600 text-white px-4 py-2 rounded-md hover:bg-gray-700 transition-colors"
              >
                Cancel
              </button>
            </div>
          </div>

          {/* Quiz Settings Form */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Quiz Title *
              </label>
              <input
                type="text"
                name="title"
                value={formData.title}
                onChange={handleInputChange}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500"
                required
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Quiz Type
              </label>
              <select
                name="quiz_type"
                value={formData.quiz_type}
                onChange={handleInputChange}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500"
              >
                <option value="assessment">Assessment</option>
                <option value="practice">Practice</option>
                <option value="exam">Exam</option>
                <option value="survey">Survey</option>
              </select>
            </div>

            <div className="md:col-span-2">
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Description
              </label>
              <textarea
                name="description"
                value={formData.description}
                onChange={handleInputChange}
                rows={3}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500"
                placeholder="Enter quiz description..."
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Duration (minutes)
              </label>
              <input
                type="number"
                name="duration_minutes"
                value={formData.duration_minutes}
                onChange={handleInputChange}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500"
                placeholder="Leave blank for no time limit"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Max Attempts
              </label>
              <input
                type="number"
                name="max_attempts"
                value={formData.max_attempts}
                onChange={handleInputChange}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500"
                placeholder="Leave blank for unlimited"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Passing Score (%)
              </label>
              <input
                type="number"
                name="passing_score"
                value={formData.passing_score}
                onChange={handleInputChange}
                min="0"
                max="100"
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Visibility
              </label>
              <select
                name="visibility"
                value={formData.visibility}
                onChange={handleInputChange}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500"
              >
                <option value="public">Public</option>
                <option value="private">Private</option>
                <option value="group">Group Only</option>
              </select>
            </div>

            <div className="md:col-span-2">
              <div className="flex flex-wrap gap-4">
                <label className="flex items-center">
                  <input
                    type="checkbox"
                    name="randomize_questions"
                    checked={formData.randomize_questions}
                    onChange={handleInputChange}
                    className="rounded border-gray-300 text-blue-600 focus:ring-blue-500"
                  />
                  <span className="ml-2 text-sm text-gray-700">Randomize Questions</span>
                </label>

                <label className="flex items-center">
                  <input
                    type="checkbox"
                    name="allow_review"
                    checked={formData.allow_review}
                    onChange={handleInputChange}
                    className="rounded border-gray-300 text-blue-600 focus:ring-blue-500"
                  />
                  <span className="ml-2 text-sm text-gray-700">Allow Review</span>
                </label>

                <label className="flex items-center">
                  <input
                    type="checkbox"
                    name="is_active"
                    checked={formData.is_active}
                    onChange={handleInputChange}
                    className="rounded border-gray-300 text-blue-600 focus:ring-blue-500"
                  />
                  <span className="ml-2 text-sm text-gray-700">Active</span>
                </label>
              </div>
            </div>
          </div>

          <div className="mt-6 flex justify-end">
            <button
              onClick={handleSaveQuiz}
              disabled={saving}
              className="bg-blue-600 text-white px-6 py-2 rounded-md hover:bg-blue-700 transition-colors disabled:opacity-50"
            >
              {saving ? 'Saving...' : 'Save Quiz Settings'}
            </button>
          </div>
        </div>

        {/* Questions Section */}
        <div className="bg-white rounded-lg shadow-sm p-6">
          <div className="flex items-center justify-between mb-6">
            <h2 className="text-xl font-semibold text-gray-900">Questions ({questions.length})</h2>
            <button
              onClick={() => setShowAddQuestion(true)}
              className="bg-blue-600 text-white px-4 py-2 rounded-md hover:bg-blue-700 transition-colors"
            >
              + Add Question
            </button>
          </div>

          {/* Existing Questions */}
          {questions.length > 0 ? (
            <div className="space-y-4 mb-6">
              {questions.map((question, index) => (
                <div key={question.id} className="border border-gray-200 rounded-lg p-4">
                  <div className="flex items-start justify-between">
                    <div className="flex-1">
                      <div className="flex items-center space-x-2 mb-2">
                        <span className="bg-blue-100 text-blue-800 text-xs font-medium px-2 py-1 rounded">
                          Question {index + 1}
                        </span>
                        <span className="bg-gray-100 text-gray-700 text-xs px-2 py-1 rounded">
                          {question.question_type.replace('_', ' ')} • {question.points} pts
                        </span>
                      </div>
                      <h3 className="font-medium text-gray-900 mb-2">{question.text}</h3>
                      
                      {question.choices && question.choices.length > 0 && (
                        <div className="space-y-1">
                          {question.choices.map((choice, choiceIndex) => (
                            <div key={choiceIndex} className="flex items-center space-x-2 text-sm">
                              <span className={`w-2 h-2 rounded-full ${choice.is_correct ? 'bg-green-500' : 'bg-gray-300'}`}></span>
                              <span className={choice.is_correct ? 'text-green-700 font-medium' : 'text-gray-600'}>
                                {choice.text}
                              </span>
                            </div>
                          ))}
                        </div>
                      )}
                    </div>
                    
                    <div className="flex space-x-2 ml-4">
                      <button
                        onClick={() => handleEditQuestion(question)}
                        className="text-blue-600 hover:text-blue-800 text-sm"
                      >
                        Edit
                      </button>
                      <button
                        onClick={() => handleDeleteQuestion(question.id)}
                        className="text-red-600 hover:text-red-800 text-sm"
                      >
                        Delete
                      </button>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <div className="text-center py-8 border-2 border-dashed border-gray-300 rounded-lg">
              <div className="text-4xl mb-4">📝</div>
              <h3 className="text-lg font-medium text-gray-900 mb-2">No questions added yet</h3>
              <p className="text-gray-600 mb-4">Add your first question to get started</p>
              <button
                onClick={() => setShowAddQuestion(true)}
                className="bg-blue-600 text-white px-4 py-2 rounded-md hover:bg-blue-700 transition-colors"
              >
                Add First Question
              </button>
            </div>
          )}

          {/* Add/Edit Question Form */}
          {showAddQuestion && (
            <div className="border-t border-gray-200 pt-6">
              <h3 className="text-lg font-medium text-gray-900 mb-4">
                {editingQuestion ? 'Edit Question' : 'Add New Question'}
              </h3>
              
              <div className="space-y-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Question Text *
                  </label>
                  <textarea
                    value={newQuestion.text}
                    onChange={(e) => handleQuestionChange('text', e.target.value)}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500"
                    rows={3}
                    placeholder="Enter your question..."
                  />
                </div>

                <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Question Type
                    </label>
                    <select
                      value={newQuestion.question_type}
                      onChange={(e) => handleQuestionChange('question_type', e.target.value)}
                      className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500"
                    >
                      <option value="multiple_choice">Multiple Choice</option>
                      <option value="true_false">True/False</option>
                    </select>
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Points
                    </label>
                    <input
                      type="number"
                      value={newQuestion.points}
                      onChange={(e) => handleQuestionChange('points', parseInt(e.target.value) || 1)}
                      className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500"
                      min="1"
                    />
                  </div>
                </div>

                {/* Choices for multiple choice and true/false */}
                {(newQuestion.question_type === 'multiple_choice' || newQuestion.question_type === 'true_false') && (
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Answer Choices *
                    </label>
                    <div className="space-y-2">
                      {newQuestion.choices.map((choice, index) => (
                        <div key={index} className="flex items-center space-x-3">
                          <input
                            type={newQuestion.question_type === 'true_false' ? 'radio' : 'checkbox'}
                            name={newQuestion.question_type === 'true_false' ? 'correct_answer' : `choice_${index}`}
                            checked={choice.is_correct}
                            onChange={(e) => {
                              if (newQuestion.question_type === 'true_false') {
                                // For true/false, only one can be correct
                                const updatedChoices = newQuestion.choices.map((c, i) => ({
                                  ...c,
                                  is_correct: i === index
                                }));
                                setNewQuestion(prev => ({ ...prev, choices: updatedChoices }));
                              } else {
                                handleChoiceChange(index, 'is_correct', e.target.checked);
                              }
                            }}
                            className="rounded border-gray-300 text-blue-600 focus:ring-blue-500"
                          />
                          <input
                            type="text"
                            value={choice.text}
                            onChange={(e) => handleChoiceChange(index, 'text', e.target.value)}
                            className="flex-1 px-3 py-2 border border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500"
                            placeholder={`Choice ${index + 1}`}
                          />
                          {newQuestion.question_type === 'multiple_choice' && newQuestion.choices.length > 2 && (
                            <button
                              onClick={() => removeChoice(index)}
                              className="text-red-600 hover:text-red-800"
                            >
                              Remove
                            </button>
                          )}
                        </div>
                      ))}
                    </div>
                    
                    {newQuestion.question_type === 'multiple_choice' && (
                      <button
                        onClick={addChoice}
                        className="mt-2 text-blue-600 hover:text-blue-800 text-sm"
                      >
                        + Add Choice
                      </button>
                    )}
                  </div>
                )}

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Explanation (Optional)
                  </label>
                  <textarea
                    value={newQuestion.explanation}
                    onChange={(e) => handleQuestionChange('explanation', e.target.value)}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500"
                    rows={2}
                    placeholder="Provide an explanation for the correct answer..."
                  />
                </div>

                <div className="flex justify-end space-x-3">
                  <button
                    onClick={() => {
                      setShowAddQuestion(false);
                      setEditingQuestion(null);
                      setNewQuestion({
                        text: '',
                        question_type: 'multiple_choice',
                        points: 1,
                        explanation: '',
                        choices: [
                          { text: '', is_correct: false },
                          { text: '', is_correct: false }
                        ]
                      });
                    }}
                    className="px-4 py-2 text-gray-700 bg-gray-200 rounded-md hover:bg-gray-300 transition-colors"
                  >
                    Cancel
                  </button>
                  <button
                    onClick={handleAddQuestion}
                    className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 transition-colors"
                  >
                    {editingQuestion ? 'Update Question' : 'Add Question'}
                  </button>
                </div>
              </div>
            </div>
          )}
        </div>

        {/* Footer Actions */}
        <div className="mt-8 text-center space-x-4">
          <button
            onClick={handleSaveQuiz}
            disabled={saving}
            className="bg-green-600 text-white px-8 py-3 rounded-md hover:bg-green-700 transition-colors disabled:opacity-50 font-medium"
          >
            {saving ? 'Saving Quiz...' : 'Save All Changes'}
          </button>
          <button
            onClick={() => navigate(`/quiz-preview/${id}`)}
            className="bg-blue-600 text-white px-6 py-3 rounded-md hover:bg-blue-700 transition-colors"
          >
            Preview Quiz
          </button>
          <button
            onClick={() => navigate('/my-quizzes')}
            className="bg-gray-600 text-white px-6 py-3 rounded-md hover:bg-gray-700 transition-colors"
          >
            Back to My Quizzes
          </button>
        </div>
      </div>
    </div>
  );
};

export default EditQuiz;
