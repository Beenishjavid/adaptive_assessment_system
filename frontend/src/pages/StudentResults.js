import React, { useState, useEffect, useCallback } from 'react';
import { useAuth } from '../context/AuthContext';
import Navbar from '../components/Navbar';
import api from '../services/api';
import toast from 'react-hot-toast';
import { useNavigate } from 'react-router-dom';

const StudentResults = () => {
  const { user } = useAuth();
  const navigate = useNavigate();
  const [loading, setLoading] = useState(true);
  const [quizzes, setQuizzes] = useState([]);
  const [selectedQuiz, setSelectedQuiz] = useState(null);
  const [attempts, setAttempts] = useState([]);
  const [analytics, setAnalytics] = useState({
    total_attempts: 0,
    total_students: 0,
    average_score: 0,
    completion_rate: 0
  });

  const fetchStudentResults = useCallback(async () => {
    try {
      setLoading(true);
      const params = selectedQuiz ? { quiz_id: selectedQuiz } : {};
      const response = await api.get('/api/quizzes/api/instructor/quiz-attempts/', { params });
      
      const { quizzes: quizData, attempts: attemptData, analytics: analyticsData } = response.data;
      
      setQuizzes(quizData);
      setAttempts(attemptData);
      setAnalytics(analyticsData);
    } catch (error) {
      console.error('Error fetching student results:', error);
      toast.error('Failed to load student results data');
      // Set empty data on error
      setQuizzes([]);
      setAttempts([]);
      setAnalytics({
        total_attempts: 0,
        total_students: 0,
        average_score: 0,
        completion_rate: 0
      });
    } finally {
      setLoading(false);
    }
  }, [selectedQuiz]);

  useEffect(() => {
    if (user?.role === 'instructor' || user?.role === 'admin') {
      fetchStudentResults();
    } else {
      navigate('/dashboard');
    }
  }, [user, navigate, fetchStudentResults]);

  const handleQuizChange = (e) => {
    const quizId = e.target.value ? parseInt(e.target.value) : null;
    setSelectedQuiz(quizId);
  };

  const getScoreColor = (score) => {
    if (score >= 80) return 'text-green-600';
    if (score >= 60) return 'text-blue-600';
    return 'text-red-600';
  };

  const getScoreBadge = (score) => {
    if (score >= 80) return 'bg-green-100 text-green-800';
    if (score >= 60) return 'bg-blue-100 text-blue-800';
    return 'bg-red-100 text-red-800';
  };

  const formatDuration = (timeStr) => {
    if (!timeStr) return 'N/A';
    
    // Parse time string like "0:05:30"
    const parts = timeStr.split(':');
    if (parts.length === 3) {
      const hours = parseInt(parts[0]);
      const minutes = parseInt(parts[1]);
      const seconds = parseInt(parts[2]);
      
      if (hours > 0) {
        return `${hours}h ${minutes}m ${seconds}s`;
      } else if (minutes > 0) {
        return `${minutes}m ${seconds}s`;
      } else {
        return `${seconds}s`;
      }
    }
    
    return timeStr;
  };

  const exportResults = () => {
    if (!attempts || attempts.length === 0) {
      toast.error('No results to export');
      return;
    }

    // Create CSV content
    const csvContent = [
      // Header
      ['Student Name', 'Email', 'Quiz', 'Score (%)', 'Status', 'Correct Answers', 'Total Questions', 'Accuracy (%)', 'Completed At', 'Duration'].join(','),
      // Data rows
      ...attempts.map(attempt => [
        attempt.student.full_name,
        attempt.student.email,
        attempt.quiz.title,
        attempt.score || 'N/A',
        attempt.status,
        attempt.correct_answers || 'N/A',
        attempt.total_answers || 'N/A',
        attempt.accuracy || 'N/A',
        attempt.completed_at ? new Date(attempt.completed_at).toLocaleString() : 'In Progress',
        formatDuration(attempt.time_taken)
      ].join(','))
    ].join('\n');

    // Create and download file
    const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
    const link = document.createElement('a');
    const url = URL.createObjectURL(blob);
    link.setAttribute('href', url);
    
    const filename = selectedQuiz 
      ? `${quizzes.find(q => q.id === selectedQuiz)?.title || 'quiz'}_results.csv`
      : 'all_quiz_results.csv';
    
    link.setAttribute('download', filename);
    link.style.visibility = 'hidden';
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    
    toast.success('Results exported successfully');
  };

  const getScoreDistribution = () => {
    if (!attempts || attempts.length === 0) return {};
    
    const distribution = {
      '90-100%': 0,
      '80-89%': 0,
      '70-79%': 0,
      '60-69%': 0,
      'Below 60%': 0
    };
    
    attempts.forEach(attempt => {
      if (attempt.score !== null && attempt.status === 'completed') {
        if (attempt.score >= 90) distribution['90-100%']++;
        else if (attempt.score >= 80) distribution['80-89%']++;
        else if (attempt.score >= 70) distribution['70-79%']++;
        else if (attempt.score >= 60) distribution['60-69%']++;
        else distribution['Below 60%']++;
      }
    });
    
    return distribution;
  };

  if (!user || (user.role !== 'instructor' && user.role !== 'admin')) {
    return (
      <div className="min-h-screen bg-gray-50">
        <Navbar />
        <div className="max-w-7xl mx-auto py-6 sm:px-6 lg:px-8">
          <div className="text-center">
            <h1 className="text-2xl font-bold text-gray-900">Access Denied</h1>
            <p className="mt-2 text-gray-600">You don't have permission to view student results.</p>
          </div>
        </div>
      </div>
    );
  }

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50">
        <Navbar />
        <div className="max-w-7xl mx-auto py-6 sm:px-6 lg:px-8">
          <div className="flex justify-center items-center h-64">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600"></div>
          </div>
        </div>
      </div>
    );
  }

  const scoreDistribution = getScoreDistribution();

  return (
    <div className="min-h-screen bg-gray-50">
      <Navbar />
      
      <main className="max-w-7xl mx-auto py-6 sm:px-6 lg:px-8">
        <div className="px-4 py-6 sm:px-0">
          {/* Header */}
          <div className="mb-8">
            <h1 className="text-3xl font-bold text-gray-900">Student Results</h1>
            <p className="mt-2 text-gray-600">View and analyze student performance on your quizzes</p>
          </div>

          {/* Quiz Selection and Export */}
          <div className="bg-white shadow rounded-lg p-6 mb-6">
            <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
              <div className="flex-1 max-w-xs">
                <label htmlFor="quiz-select" className="block text-sm font-medium text-gray-700 mb-2">
                  Select Quiz
                </label>
                <select
                  id="quiz-select"
                  value={selectedQuiz || ''}
                  onChange={handleQuizChange}
                  className="block w-full rounded-md border-gray-300 shadow-sm focus:border-primary-500 focus:ring-primary-500"
                >
                  <option value="">All Quizzes</option>
                  {quizzes.map((quiz) => (
                    <option key={quiz.id} value={quiz.id}>
                      {quiz.title} ({quiz.attempt_count} attempts)
                    </option>
                  ))}
                </select>
              </div>
              
              <button
                onClick={exportResults}
                disabled={attempts.length === 0}
                className="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md shadow-sm text-white bg-primary-600 hover:bg-primary-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500 disabled:opacity-50 disabled:cursor-not-allowed"
              >
                <svg className="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 10v6m0 0l-3-3m3 3l3-3m2 8H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                </svg>
                Export Results
              </button>
            </div>
          </div>

          {/* Analytics Overview */}
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-6">
            <div className="bg-white overflow-hidden shadow rounded-lg">
              <div className="p-5">
                <div className="flex items-center">
                  <div className="flex-shrink-0">
                    <div className="w-8 h-8 bg-blue-500 rounded-md flex items-center justify-center">
                      <svg className="w-5 h-5 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5H7a2 2 0 00-2 2v6a2 2 0 002 2h2m0 0h2a2 2 0 002-2V7a2 2 0 00-2-2H9m0 0V3m0 2v2" />
                      </svg>
                    </div>
                  </div>
                  <div className="ml-5 w-0 flex-1">
                    <dl>
                      <dt className="text-sm font-medium text-gray-500 truncate">Total Attempts</dt>
                      <dd className="text-2xl font-bold text-blue-600">{analytics.total_attempts}</dd>
                    </dl>
                  </div>
                </div>
              </div>
            </div>

            <div className="bg-white overflow-hidden shadow rounded-lg">
              <div className="p-5">
                <div className="flex items-center">
                  <div className="flex-shrink-0">
                    <div className="w-8 h-8 bg-green-500 rounded-md flex items-center justify-center">
                      <svg className="w-5 h-5 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z" />
                      </svg>
                    </div>
                  </div>
                  <div className="ml-5 w-0 flex-1">
                    <dl>
                      <dt className="text-sm font-medium text-gray-500 truncate">Total Students</dt>
                      <dd className="text-2xl font-bold text-green-600">{analytics.total_students}</dd>
                    </dl>
                  </div>
                </div>
              </div>
            </div>

            <div className="bg-white overflow-hidden shadow rounded-lg">
              <div className="p-5">
                <div className="flex items-center">
                  <div className="flex-shrink-0">
                    <div className="w-8 h-8 bg-purple-500 rounded-md flex items-center justify-center">
                      <svg className="w-5 h-5 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
                      </svg>
                    </div>
                  </div>
                  <div className="ml-5 w-0 flex-1">
                    <dl>
                      <dt className="text-sm font-medium text-gray-500 truncate">Completion Rate</dt>
                      <dd className="text-2xl font-bold text-purple-600">{analytics.completion_rate}%</dd>
                    </dl>
                  </div>
                </div>
              </div>
            </div>

            <div className="bg-white overflow-hidden shadow rounded-lg">
              <div className="p-5">
                <div className="flex items-center">
                  <div className="flex-shrink-0">
                    <div className="w-8 h-8 bg-orange-500 rounded-md flex items-center justify-center">
                      <svg className="w-5 h-5 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 7h8m0 0v8m0-8l-8 8-4-4-6 6" />
                      </svg>
                    </div>
                  </div>
                  <div className="ml-5 w-0 flex-1">
                    <dl>
                      <dt className="text-sm font-medium text-gray-500 truncate">Average Score</dt>
                      <dd className="text-2xl font-bold text-orange-600">{analytics.average_score}%</dd>
                    </dl>
                  </div>
                </div>
              </div>
            </div>
          </div>

          {/* Score Distribution */}
          <div className="bg-white shadow rounded-lg p-6 mb-6">
            <h3 className="text-lg font-medium text-gray-900 mb-4">Score Distribution</h3>
            <div className="space-y-4">
              {Object.entries(scoreDistribution).map(([range, count]) => (
                <div key={range} className="flex items-center">
                  <div className="w-24 text-sm text-gray-600">{range}</div>
                  <div className="flex-1 mx-4">
                    <div className="bg-gray-200 rounded-full h-4 relative">
                      <div
                        className={`h-4 rounded-full ${
                          range === '90-100%' ? 'bg-green-500' :
                          range === '80-89%' ? 'bg-blue-500' :
                          range === '70-79%' ? 'bg-yellow-500' :
                          range === '60-69%' ? 'bg-orange-500' :
                          'bg-red-500'
                        }`}
                        style={{ 
                          width: `${analytics.total_attempts > 0 ? (count / analytics.total_attempts) * 100 : 0}%` 
                        }}
                      ></div>
                    </div>
                  </div>
                  <div className="w-12 text-right text-sm font-medium text-gray-900">{count}</div>
                </div>
              ))}
            </div>
          </div>

          {/* Recent Attempts Table */}
          <div className="bg-white shadow rounded-lg overflow-hidden">
            <div className="px-6 py-4 border-b border-gray-200">
              <h3 className="text-lg font-medium text-gray-900">Recent Attempts</h3>
            </div>
            <div className="overflow-x-auto">
              <table className="min-w-full divide-y divide-gray-200">
                <thead className="bg-gray-50">
                  <tr>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Student
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Quiz
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Score
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Accuracy
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Status
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Completed
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Duration
                    </th>
                  </tr>
                </thead>
                <tbody className="bg-white divide-y divide-gray-200">
                  {attempts.map((attempt) => (
                    <tr key={attempt.id} className="hover:bg-gray-50">
                      <td className="px-6 py-4 whitespace-nowrap">
                        <div className="flex items-center">
                          <div className="h-8 w-8 rounded-full bg-gray-300 flex items-center justify-center">
                            <span className="text-sm font-medium text-gray-700">
                              {attempt.student.full_name.charAt(0)}
                            </span>
                          </div>
                          <div className="ml-3">
                            <div className="text-sm font-medium text-gray-900">
                              {attempt.student.full_name}
                            </div>
                            <div className="text-sm text-gray-500">
                              {attempt.student.email}
                            </div>
                          </div>
                        </div>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <div className="text-sm font-medium text-gray-900">{attempt.quiz.title}</div>
                        <div className="text-sm text-gray-500">{attempt.quiz.quiz_type}</div>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        {attempt.score !== null ? (
                          <span className={`text-sm font-bold ${getScoreColor(attempt.score)}`}>
                            {attempt.score}%
                          </span>
                        ) : (
                          <span className="text-sm text-gray-500">In Progress</span>
                        )}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <div className="text-sm text-gray-900">
                          {attempt.correct_answers}/{attempt.total_answers} ({attempt.accuracy}%)
                        </div>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <span className={`inline-flex px-2 py-1 text-xs font-semibold rounded-full ${
                          attempt.status === 'completed' ? getScoreBadge(attempt.score || 0) : 'bg-yellow-100 text-yellow-800'
                        }`}>
                          {attempt.status === 'completed' ? 
                            (attempt.score >= 60 ? 'Passed' : 'Failed') : 
                            'In Progress'
                          }
                        </span>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                        {attempt.completed_at ? 
                          new Date(attempt.completed_at).toLocaleString() : 
                          'In Progress'
                        }
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                        {formatDuration(attempt.time_taken)}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
              
              {attempts.length === 0 && (
                <div className="text-center py-12">
                  <svg className="mx-auto h-12 w-12 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                  </svg>
                  <h3 className="mt-2 text-sm font-medium text-gray-900">No quiz attempts</h3>
                  <p className="mt-1 text-sm text-gray-500">
                    {selectedQuiz ? 'No attempts found for the selected quiz.' : 'No quiz attempts have been made yet.'}
                  </p>
                </div>
              )}
            </div>
          </div>
        </div>
      </main>
    </div>
  );
};

export default StudentResults;
