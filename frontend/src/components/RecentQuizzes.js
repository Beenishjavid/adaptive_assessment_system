import React, { useState, useEffect } from 'react';
import { useAuth } from '../context/AuthContext';
import { useNavigate } from 'react-router-dom';
import api from '../services/api';

const RecentQuizzes = () => {
  const { user } = useAuth();
  const navigate = useNavigate();
  const [quizzes, setQuizzes] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchQuizzes = async () => {
      try {
        setLoading(true);
        let response;
        
        if (user?.role === 'admin' || user?.role === 'instructor') {
          // Fetch instructor's quizzes
          response = await api.get('/api/quizzes/api/quiz/my-quizzes/');
          const quizzesData = response.data.quizzes || [];
          
          // Transform data for display
          const transformedQuizzes = quizzesData.slice(0, 5).map(quiz => ({
            id: quiz.id,
            title: quiz.title,
            creator: quiz.created_by || user.full_name,
            attempts: quiz.attempt_count || 0,
            avgScore: quiz.average_score || 0,
            status: quiz.is_active ? 'active' : 'inactive',
            created: quiz.created_at ? new Date(quiz.created_at).toLocaleDateString() : 'Unknown',
            dueDate: quiz.end_time ? new Date(quiz.end_time).toLocaleDateString() : null
          }));
          
          setQuizzes(transformedQuizzes);
        } else {
          // Fetch available quizzes for students
          const [availableRes, attemptsRes] = await Promise.all([
            api.get('/api/quizzes/all/'),
            api.get('/api/quizzes/api/my-results/')
          ]);
          
          const availableQuizzes = availableRes.data.quizzes || [];
          const myAttempts = attemptsRes.data.results || [];
          
          // Combine data to show student's quiz status
          const transformedQuizzes = availableQuizzes.slice(0, 5).map(quiz => {
            const attempt = myAttempts.find(a => a.quiz_id === quiz.id);
            
            return {
              id: quiz.id,
              title: quiz.title,
              instructor: quiz.created_by,
              score: attempt ? attempt.score : null,
              status: attempt ? 'completed' : 'available',
              takenAt: attempt ? new Date(attempt.completed_at).toLocaleDateString() : null,
              dueDate: quiz.end_time ? new Date(quiz.end_time).toLocaleDateString() : null
            };
          });
          
          setQuizzes(transformedQuizzes);
        }
      } catch (error) {
        console.error('Error fetching quizzes:', error);
        setQuizzes([]);
      } finally {
        setLoading(false);
      }
    };

    if (user) {
      fetchQuizzes();
    }
  }, [user]);

  const getStatusBadge = (status) => {
    const statusStyles = {
      active: 'bg-green-100 text-green-800',
      completed: 'bg-blue-100 text-blue-800',
      draft: 'bg-yellow-100 text-yellow-800',
      available: 'bg-purple-100 text-purple-800',
    };

    return (
      <span className={`px-2 py-1 rounded-full text-xs font-medium ${statusStyles[status] || statusStyles.draft}`}>
        {status.charAt(0).toUpperCase() + status.slice(1)}
      </span>
    );
  };

  const renderQuizCard = (quiz) => {
    if (user?.role === 'admin') {
      return (
        <div key={quiz.id} className="p-4 border border-gray-200 rounded-lg hover:border-gray-300 transition-colors">
          <div className="flex items-start justify-between">
            <div className="flex-1">
              <h4 className="text-sm font-medium text-gray-900">{quiz.title}</h4>
              <p className="text-xs text-gray-500 mt-1">Created by {quiz.creator}</p>
              <div className="flex items-center space-x-4 mt-2 text-xs text-gray-600">
                <span>{quiz.attempts} attempts</span>
                <span>Avg: {quiz.avgScore}%</span>
                <span>{quiz.created}</span>
              </div>
            </div>
            <div className="ml-4">
              {getStatusBadge(quiz.status)}
            </div>
          </div>
        </div>
      );
    } else if (user?.role === 'instructor') {
      return (
        <div key={quiz.id} className="p-4 border border-gray-200 rounded-lg hover:border-gray-300 transition-colors">
          <div className="flex items-start justify-between">
            <div className="flex-1">
              <h4 className="text-sm font-medium text-gray-900">{quiz.title}</h4>
              <div className="flex items-center space-x-4 mt-2 text-xs text-gray-600">
                <span>{quiz.attempts} attempts</span>
                <span>Avg: {quiz.avgScore}%</span>
                <span>Due: {quiz.dueDate}</span>
              </div>
            </div>
            <div className="ml-4">
              {getStatusBadge(quiz.status)}
            </div>
          </div>
        </div>
      );
    } else {
      return (
        <div key={quiz.id} className="p-4 border border-gray-200 rounded-lg hover:border-gray-300 transition-colors">
          <div className="flex items-start justify-between">
            <div className="flex-1">
              <h4 className="text-sm font-medium text-gray-900">{quiz.title}</h4>
              <p className="text-xs text-gray-500 mt-1">by {quiz.instructor}</p>
              <div className="flex items-center space-x-4 mt-2 text-xs text-gray-600">
                {quiz.score !== null ? (
                  <>
                    <span>Score: {quiz.score}%</span>
                    <span>Taken: {quiz.takenAt}</span>
                  </>
                ) : (
                  <span>Due: {quiz.dueDate}</span>
                )}
              </div>
            </div>
            <div className="ml-4 flex flex-col items-end space-y-2">
              {getStatusBadge(quiz.status)}
              {quiz.status === 'available' && (
                <button 
                  onClick={() => handleTakeQuiz(quiz.id)}
                  className="text-xs text-primary-600 hover:text-primary-700 font-medium"
                >
                  Take Quiz
                </button>
              )}
              {(user?.role === 'instructor' || user?.role === 'admin') && (
                <button 
                  onClick={() => handleViewQuiz(quiz.id)}
                  className="text-xs text-blue-600 hover:text-blue-700 font-medium"
                >
                  View
                </button>
              )}
            </div>
          </div>
        </div>
      );
    }
  };

  const getTitle = () => {
    if (user?.role === 'admin') return 'Recent Quiz Activity';
    if (user?.role === 'instructor') return 'My Recent Quizzes';
    return 'My Quizzes';
  };

  const handleTakeQuiz = async (quizId) => {
    try {
      const response = await api.post(`/api/quizzes/api/quiz/${quizId}/start/`);
      const attemptId = response.data.attempt_id;
      navigate(`/take-quiz/${attemptId}`);
    } catch (error) {
      console.error('Error starting quiz:', error);
    }
  };

  const handleViewQuiz = (quizId) => {
    navigate(`/my-quizzes`); // Navigate to quiz management
  };

  if (loading) {
    return (
      <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
        <div className="flex items-center justify-between mb-4">
          <div className="h-6 bg-gray-200 rounded w-32 animate-pulse"></div>
          <div className="h-4 bg-gray-200 rounded w-16 animate-pulse"></div>
        </div>
        <div className="space-y-3">
          {[1, 2, 3].map((index) => (
            <div key={index} className="p-4 border border-gray-200 rounded-lg animate-pulse">
              <div className="flex items-start justify-between">
                <div className="flex-1">
                  <div className="h-4 bg-gray-200 rounded w-48 mb-2"></div>
                  <div className="h-3 bg-gray-200 rounded w-32 mb-2"></div>
                  <div className="h-3 bg-gray-200 rounded w-40"></div>
                </div>
                <div className="h-6 bg-gray-200 rounded w-16"></div>
              </div>
            </div>
          ))}
        </div>
      </div>
    );
  }

  return (
    <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-lg font-semibold text-gray-900">{getTitle()}</h3>
        <button className="text-sm text-primary-600 hover:text-primary-700 font-medium">
          View All
        </button>
      </div>
      
      <div className="space-y-3">
        {quizzes.length > 0 ? (
          quizzes.map(renderQuizCard)
        ) : (
          <div className="text-center py-8 text-gray-500">
            <svg className="mx-auto h-12 w-12 text-gray-400 mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
            </svg>
            <p>No quizzes available</p>
            <p className="text-sm mt-1">
              {user?.role === 'instructor' ? 'Create your first quiz to get started!' : 'Check back later for new quizzes.'}
            </p>
          </div>
        )}
      </div>
    </div>
  );
};

export default RecentQuizzes;
