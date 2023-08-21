import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import Navbar from '../components/Navbar';
import api from '../services/api';
import toast from 'react-hot-toast';

const GroupDetail = () => {
  const { id } = useParams();
  const navigate = useNavigate();
  const { user } = useAuth();
  
  const [group, setGroup] = useState(null);
  const [quizzes, setQuizzes] = useState([]);
  const [analytics, setAnalytics] = useState(null);
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState('overview');
  const [showAssignModal, setShowAssignModal] = useState(false);
  const [availableQuizzes, setAvailableQuizzes] = useState([]);
  const [assignFormData, setAssignFormData] = useState({
    quiz_id: '',
    due_date: '',
    is_mandatory: true,
    instructions: ''
  });

  useEffect(() => {
    fetchGroupDetails();
    fetchGroupQuizzes();
    if (user?.role === 'instructor' || user?.role === 'admin') {
      fetchAnalytics();
      fetchAvailableQuizzes();
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [id]);

  const fetchGroupDetails = async () => {
    try {
      const response = await api.get(`/api/groups/${id}/`);
      setGroup(response.data);
    } catch (error) {
      console.error('Error fetching group details:', error);
      toast.error('Failed to fetch group details');
      navigate('/groups');
    } finally {
      setLoading(false);
    }
  };

  const fetchGroupQuizzes = async () => {
    try {
      const response = await api.get(`/api/groups/${id}/quizzes/`);
      setQuizzes(response.data.quizzes);
    } catch (error) {
      console.error('Error fetching group quizzes:', error);
      toast.error('Failed to fetch group quizzes');
    }
  };

  const fetchAnalytics = async () => {
    try {
      const response = await api.get(`/api/groups/${id}/analytics/`);
      setAnalytics(response.data.analytics);
    } catch (error) {
      console.error('Error fetching analytics:', error);
      // Don't show error toast for analytics as it's not critical
    }
  };

  const fetchAvailableQuizzes = async () => {
    try {
      const response = await api.get('/api/quiz/my-quizzes/');
      setAvailableQuizzes(response.data.quizzes || []);
    } catch (error) {
      console.error('Error fetching available quizzes:', error);
    }
  };

  const handleAssignQuiz = async (e) => {
    e.preventDefault();
    try {
      await api.post(`/api/groups/${id}/assign-quiz/`, assignFormData);
      toast.success('Quiz assigned successfully!');
      setShowAssignModal(false);
      setAssignFormData({
        quiz_id: '',
        due_date: '',
        is_mandatory: true,
        instructions: ''
      });
      fetchGroupQuizzes();
    } catch (error) {
      console.error('Error assigning quiz:', error);
      toast.error(error.response?.data?.message || 'Failed to assign quiz');
    }
  };

  const handleLeaveGroup = async () => {
    if (window.confirm('Are you sure you want to leave this group?')) {
      try {
        await api.post(`/api/groups/${id}/leave/`);
        toast.success('Successfully left the group');
        navigate('/groups');
      } catch (error) {
        console.error('Error leaving group:', error);
        toast.error(error.response?.data?.message || 'Failed to leave group');
      }
    }
  };

  const handleTakeQuiz = async (quiz) => {
    try {
      const response = await api.post(`/api/quiz/${quiz.id}/start/`);
      if (response.data.success) {
        navigate(`/take-quiz/${response.data.attempt_id}`);
      } else {
        toast.error(response.data.message || 'Failed to start quiz');
      }
    } catch (error) {
      console.error('Error starting quiz:', error);
      toast.error(error.response?.data?.message || 'Failed to start quiz');
    }
  };

  const getGroupTypeIcon = (type) => {
    const icons = {
      course: '🏫',
      study: '📚',
      public: '🌍',
      self: '🎯'
    };
    return icons[type] || '📁';
  };

  const getRoleColor = (role) => {
    const colors = {
      admin: 'bg-red-100 text-red-800',
      instructor: 'bg-blue-100 text-blue-800',
      member: 'bg-gray-100 text-gray-800'
    };
    return colors[role] || 'bg-gray-100 text-gray-800';
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50">
        <Navbar />
        <div className="max-w-7xl mx-auto py-6 sm:px-6 lg:px-8">
          <div className="animate-pulse">
            <div className="h-8 bg-gray-200 rounded w-1/4 mb-4"></div>
            <div className="h-4 bg-gray-200 rounded w-1/2 mb-8"></div>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
              {[1, 2, 3].map((i) => (
                <div key={i} className="bg-white rounded-lg shadow p-6">
                  <div className="h-4 bg-gray-200 rounded w-3/4 mb-4"></div>
                  <div className="h-4 bg-gray-200 rounded w-1/2"></div>
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>
    );
  }

  if (!group) {
    return (
      <div className="min-h-screen bg-gray-50">
        <Navbar />
        <div className="max-w-7xl mx-auto py-6 sm:px-6 lg:px-8">
          <div className="text-center">
            <h1 className="text-2xl font-bold text-gray-900">Group Not Found</h1>
            <p className="mt-2 text-gray-600">The group you're looking for doesn't exist.</p>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <Navbar />
      
      <main className="max-w-7xl mx-auto py-6 sm:px-6 lg:px-8">
        <div className="px-4 py-6 sm:px-0">
          {/* Header */}
          <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6 mb-8">
            <div className="flex items-start justify-between">
              <div className="flex items-center space-x-4">
                <span className="text-4xl">{getGroupTypeIcon(group.group_type)}</span>
                <div>
                  <h1 className="text-3xl font-bold text-gray-900">{group.name}</h1>
                  <p className="text-gray-600 mt-1">{group.description || 'No description available'}</p>
                  <div className="flex items-center space-x-4 mt-2">
                    {group.course_code && (
                      <span className="text-sm font-medium text-blue-600">
                        Course: {group.course_code}
                      </span>
                    )}
                    {group.subject && (
                      <span className="text-sm font-medium text-green-600">
                        Subject: {group.subject}
                      </span>
                    )}
                    <span className={`inline-flex px-2 py-1 text-xs font-semibold rounded-full ${getRoleColor(group.user_role)}`}>
                      {group.user_role || 'Non-member'}
                    </span>
                  </div>
                </div>
              </div>
              
              <div className="flex space-x-3">
                {group.can_manage && (
                  <button
                    onClick={() => setShowAssignModal(true)}
                    className="bg-blue-600 text-white px-4 py-2 rounded-md hover:bg-blue-700 transition-colors"
                  >
                    Assign Quiz
                  </button>
                )}
                {group.user_role && group.user_role !== 'creator' && (
                  <button
                    onClick={handleLeaveGroup}
                    className="bg-red-600 text-white px-4 py-2 rounded-md hover:bg-red-700 transition-colors"
                  >
                    Leave Group
                  </button>
                )}
                {group.join_code && (
                  <div className="text-sm">
                    <span className="text-gray-500">Join Code:</span>
                    <span className="ml-2 font-mono bg-gray-100 px-2 py-1 rounded">
                      {group.join_code}
                    </span>
                  </div>
                )}
              </div>
            </div>
          </div>

          {/* Stats */}
          <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
            <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
              <div className="flex items-center">
                <div className="text-2xl text-blue-600 mr-3">👥</div>
                <div>
                  <p className="text-2xl font-bold text-gray-900">{group.member_count}</p>
                  <p className="text-sm text-gray-600">Members</p>
                </div>
              </div>
            </div>
            
            <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
              <div className="flex items-center">
                <div className="text-2xl text-green-600 mr-3">📝</div>
                <div>
                  <p className="text-2xl font-bold text-gray-900">{group.quiz_count}</p>
                  <p className="text-sm text-gray-600">Quizzes</p>
                </div>
              </div>
            </div>
            
            <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
              <div className="flex items-center">
                <div className="text-2xl text-purple-600 mr-3">⚡</div>
                <div>
                  <p className="text-2xl font-bold text-gray-900">{group.active_assignments}</p>
                  <p className="text-sm text-gray-600">Active Assignments</p>
                </div>
              </div>
            </div>
            
            {analytics && (
              <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
                <div className="flex items-center">
                  <div className="text-2xl text-orange-600 mr-3">📊</div>
                  <div>
                    <p className="text-2xl font-bold text-gray-900">
                      {Math.round(analytics.completion_rate)}%
                    </p>
                    <p className="text-sm text-gray-600">Completion Rate</p>
                  </div>
                </div>
              </div>
            )}
          </div>

          {/* Tabs */}
          <div className="border-b border-gray-200 mb-6">
            <nav className="-mb-px flex space-x-8">
              <button
                onClick={() => setActiveTab('overview')}
                className={`py-2 px-1 border-b-2 font-medium text-sm ${
                  activeTab === 'overview'
                    ? 'border-blue-500 text-blue-600'
                    : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                }`}
              >
                Overview
              </button>
              <button
                onClick={() => setActiveTab('quizzes')}
                className={`py-2 px-1 border-b-2 font-medium text-sm ${
                  activeTab === 'quizzes'
                    ? 'border-blue-500 text-blue-600'
                    : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                }`}
              >
                Quizzes ({quizzes.length})
              </button>
              <button
                onClick={() => setActiveTab('members')}
                className={`py-2 px-1 border-b-2 font-medium text-sm ${
                  activeTab === 'members'
                    ? 'border-blue-500 text-blue-600'
                    : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                }`}
              >
                Members ({group.member_count})
              </button>
              {analytics && (
                <button
                  onClick={() => setActiveTab('analytics')}
                  className={`py-2 px-1 border-b-2 font-medium text-sm ${
                    activeTab === 'analytics'
                      ? 'border-blue-500 text-blue-600'
                      : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                  }`}
                >
                  Analytics
                </button>
              )}
            </nav>
          </div>

          {/* Tab Content */}
          {activeTab === 'overview' && (
            <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
              <h2 className="text-xl font-semibold text-gray-900 mb-4">Group Information</h2>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div>
                  <h3 className="text-sm font-medium text-gray-500 uppercase tracking-wide mb-2">
                    Basic Details
                  </h3>
                  <dl className="space-y-3">
                    <div>
                      <dt className="text-sm font-medium text-gray-900">Type</dt>
                      <dd className="text-sm text-gray-600 capitalize">{group.group_type}</dd>
                    </div>
                    <div>
                      <dt className="text-sm font-medium text-gray-900">Created By</dt>
                      <dd className="text-sm text-gray-600">
                        {group.created_by?.first_name} {group.created_by?.last_name}
                      </dd>
                    </div>
                    <div>
                      <dt className="text-sm font-medium text-gray-900">Created At</dt>
                      <dd className="text-sm text-gray-600">
                        {new Date(group.created_at).toLocaleDateString()}
                      </dd>
                    </div>
                    <div>
                      <dt className="text-sm font-medium text-gray-900">Visibility</dt>
                      <dd className="text-sm text-gray-600">
                        {group.is_public ? 'Public' : 'Private'}
                      </dd>
                    </div>
                  </dl>
                </div>
                
                <div>
                  <h3 className="text-sm font-medium text-gray-500 uppercase tracking-wide mb-2">
                    Activity
                  </h3>
                  <dl className="space-y-3">
                    <div>
                      <dt className="text-sm font-medium text-gray-900">Total Members</dt>
                      <dd className="text-sm text-gray-600">{group.member_count} / {group.max_members}</dd>
                    </div>
                    <div>
                      <dt className="text-sm font-medium text-gray-900">Available Quizzes</dt>
                      <dd className="text-sm text-gray-600">{group.quiz_count}</dd>
                    </div>
                    <div>
                      <dt className="text-sm font-medium text-gray-900">Your Role</dt>
                      <dd className="text-sm text-gray-600 capitalize">{group.user_role || 'Not a member'}</dd>
                    </div>
                  </dl>
                </div>
              </div>
            </div>
          )}

          {activeTab === 'quizzes' && (
            <div>
              {quizzes.length > 0 ? (
                <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                  {quizzes.map((quiz) => (
                    <div key={quiz.id} className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
                      <div className="flex items-start justify-between mb-4">
                        <div className="flex-1">
                          <h3 className="text-lg font-semibold text-gray-900 mb-2">{quiz.title}</h3>
                          <p className="text-sm text-gray-600 mb-3">{quiz.description || 'No description'}</p>
                          
                          <div className="flex items-center space-x-4 text-sm text-gray-500 mb-3">
                            <span>⏱️ {quiz.duration_minutes} min</span>
                            <span>📝 {quiz.total_questions} questions</span>
                            <span>🎯 Pass: {quiz.passing_score}%</span>
                          </div>
                          
                          {quiz.assignment && (
                            <div className="bg-blue-50 border border-blue-200 rounded p-3 mb-3">
                              <p className="text-sm font-medium text-blue-900">Assignment Details</p>
                              {quiz.assignment.due_date && (
                                <p className="text-sm text-blue-700">
                                  Due: {new Date(quiz.assignment.due_date).toLocaleDateString()}
                                </p>
                              )}
                              {quiz.assignment.instructions && (
                                <p className="text-sm text-blue-700 mt-1">{quiz.assignment.instructions}</p>
                              )}
                            </div>
                          )}
                        </div>
                      </div>
                      
                      <div className="flex items-center justify-between">
                        <div className="text-sm">
                          <span className="text-gray-500">Attempts: </span>
                          <span className="font-medium">{quiz.user_attempts} / {quiz.max_attempts}</span>
                        </div>
                        
                        <div className="flex space-x-2">
                          {quiz.can_attempt && (
                            <button
                              onClick={() => handleTakeQuiz(quiz)}
                              className="bg-blue-600 text-white px-4 py-2 rounded-md hover:bg-blue-700 transition-colors"
                            >
                              Take Quiz
                            </button>
                          )}
                          
                          <button
                            onClick={() => navigate(`/quiz-preview/${quiz.id}`)}
                            className="text-blue-600 border border-blue-600 px-4 py-2 rounded-md hover:bg-blue-50 transition-colors"
                          >
                            Preview
                          </button>
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              ) : (
                <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-12 text-center">
                  <div className="text-gray-400 text-6xl mb-4">📝</div>
                  <h3 className="text-lg font-medium text-gray-900 mb-2">No Quizzes Available</h3>
                  <p className="text-gray-600 mb-4">
                    This group doesn't have any quizzes yet. 
                    {group.can_manage && " You can assign quizzes to this group."}
                  </p>
                  {group.can_manage && (
                    <button
                      onClick={() => setShowAssignModal(true)}
                      className="bg-blue-600 text-white px-6 py-2 rounded-md hover:bg-blue-700 transition-colors"
                    >
                      Assign Quiz
                    </button>
                  )}
                </div>
              )}
            </div>
          )}

          {activeTab === 'members' && (
            <div className="bg-white rounded-lg shadow-sm border border-gray-200">
              <div className="p-6">
                <h2 className="text-xl font-semibold text-gray-900 mb-4">Group Members</h2>
                {group.memberships && group.memberships.length > 0 ? (
                  <div className="space-y-4">
                    {group.memberships.map((membership) => (
                      <div key={membership.id} className="flex items-center justify-between p-4 border border-gray-200 rounded-lg">
                        <div className="flex items-center space-x-3">
                          <div className="w-10 h-10 bg-gray-300 rounded-full flex items-center justify-center">
                            <span className="text-sm font-medium text-gray-700">
                              {membership.user.first_name?.[0]}{membership.user.last_name?.[0]}
                            </span>
                          </div>
                          <div>
                            <p className="font-medium text-gray-900">
                              {membership.user.first_name} {membership.user.last_name}
                            </p>
                            <p className="text-sm text-gray-600">{membership.user.email}</p>
                          </div>
                        </div>
                        
                        <div className="flex items-center space-x-3">
                          <span className={`inline-flex px-2 py-1 text-xs font-semibold rounded-full ${getRoleColor(membership.role_in_group)}`}>
                            {membership.role_in_group}
                          </span>
                          <span className="text-sm text-gray-500">
                            Joined {new Date(membership.joined_at).toLocaleDateString()}
                          </span>
                        </div>
                      </div>
                    ))}
                  </div>
                ) : (
                  <p className="text-gray-600">No members found.</p>
                )}
              </div>
            </div>
          )}

          {activeTab === 'analytics' && analytics && (
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
                <h3 className="text-lg font-semibold text-gray-900 mb-4">Overall Statistics</h3>
                <div className="space-y-4">
                  <div className="flex justify-between">
                    <span className="text-gray-600">Total Members:</span>
                    <span className="font-medium">{analytics.total_members}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-600">Total Quizzes:</span>
                    <span className="font-medium">{analytics.total_quizzes}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-600">Total Assignments:</span>
                    <span className="font-medium">{analytics.total_assignments}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-600">Completion Rate:</span>
                    <span className="font-medium">{analytics.completion_rate}%</span>
                  </div>
                </div>
              </div>
              
              <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
                <h3 className="text-lg font-semibold text-gray-900 mb-4">Member Activity</h3>
                <div className="space-y-3 max-h-64 overflow-y-auto">
                  {analytics.member_activity?.map((member, index) => (
                    <div key={index} className="flex items-center justify-between">
                      <div className="flex items-center space-x-3">
                        <div className="w-8 h-8 bg-gray-300 rounded-full flex items-center justify-center">
                          <span className="text-xs font-medium text-gray-700">
                            {member.user.first_name?.[0]}{member.user.last_name?.[0]}
                          </span>
                        </div>
                        <span className="text-sm font-medium text-gray-900">
                          {member.user.first_name} {member.user.last_name}
                        </span>
                      </div>
                      <div className="text-right">
                        <div className="text-sm font-medium text-gray-900">
                          {member.completed_quizzes} quizzes
                        </div>
                        <div className={`text-xs px-2 py-1 rounded-full ${getRoleColor(member.role)}`}>
                          {member.role}
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          )}
        </div>
      </main>

      {/* Assign Quiz Modal */}
      {showAssignModal && (
        <div className="fixed inset-0 bg-gray-600 bg-opacity-50 overflow-y-auto h-full w-full z-50">
          <div className="relative top-20 mx-auto p-5 border w-96 shadow-lg rounded-md bg-white">
            <div className="mt-3">
              <h3 className="text-lg font-medium text-gray-900 mb-4">Assign Quiz to Group</h3>
              <form onSubmit={handleAssignQuiz} className="space-y-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700">Select Quiz</label>
                  <select
                    value={assignFormData.quiz_id}
                    onChange={(e) => setAssignFormData({...assignFormData, quiz_id: e.target.value})}
                    className="mt-1 block w-full border border-gray-300 rounded-md px-3 py-2"
                    required
                  >
                    <option value="">Choose a quiz...</option>
                    {availableQuizzes.map((quiz) => (
                      <option key={quiz.id} value={quiz.id}>{quiz.title}</option>
                    ))}
                  </select>
                </div>
                
                <div>
                  <label className="block text-sm font-medium text-gray-700">Due Date (Optional)</label>
                  <input
                    type="datetime-local"
                    value={assignFormData.due_date}
                    onChange={(e) => setAssignFormData({...assignFormData, due_date: e.target.value})}
                    className="mt-1 block w-full border border-gray-300 rounded-md px-3 py-2"
                  />
                </div>
                
                <div>
                  <label className="block text-sm font-medium text-gray-700">Instructions (Optional)</label>
                  <textarea
                    value={assignFormData.instructions}
                    onChange={(e) => setAssignFormData({...assignFormData, instructions: e.target.value})}
                    className="mt-1 block w-full border border-gray-300 rounded-md px-3 py-2"
                    rows="3"
                    placeholder="Additional instructions for students..."
                  />
                </div>
                
                <div className="flex items-center">
                  <input
                    type="checkbox"
                    checked={assignFormData.is_mandatory}
                    onChange={(e) => setAssignFormData({...assignFormData, is_mandatory: e.target.checked})}
                    className="mr-2"
                  />
                  <label className="text-sm font-medium text-gray-700">Mandatory assignment</label>
                </div>
                
                <div className="flex justify-end space-x-2 pt-4">
                  <button
                    type="button"
                    onClick={() => setShowAssignModal(false)}
                    className="px-4 py-2 text-sm font-medium text-gray-700 bg-gray-200 rounded-md hover:bg-gray-300"
                  >
                    Cancel
                  </button>
                  <button
                    type="submit"
                    className="px-4 py-2 text-sm font-medium text-white bg-blue-600 rounded-md hover:bg-blue-700"
                  >
                    Assign Quiz
                  </button>
                </div>
              </form>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default GroupDetail;
