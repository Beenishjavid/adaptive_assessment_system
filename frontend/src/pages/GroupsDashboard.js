import React, { useState, useEffect, useCallback } from 'react';
import { useAuth } from '../context/AuthContext';
import Navbar from '../components/Navbar';
import GroupSystemValidator from '../components/GroupSystemValidator';
import api from '../services/api';
import toast from 'react-hot-toast';

const GroupsDashboard = () => {
  const { user } = useAuth();
  const [groupsByType, setGroupsByType] = useState({
    course: [],
    study: [],
    public: [],
    self: []
  });
  const [publicGroups, setPublicGroups] = useState([]);
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState('my-groups');
  const [searchQuery, setSearchQuery] = useState('');
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [showJoinModal, setShowJoinModal] = useState(false);
  const [createFormData, setCreateFormData] = useState({
    name: '',
    description: '',
    group_type: 'study',
    course_code: '',
    subject: '',
    is_public: false,
    max_members: 50
  });
  const [joinCode, setJoinCode] = useState('');

  const fetchUserGroups = async () => {
    try {
      setLoading(true);
      const response = await api.get('/api/groups/by-type/');
      setGroupsByType(response.data.groups_by_type);
    } catch (error) {
      console.error('Error fetching user groups:', error);
      toast.error('Failed to fetch your groups');
    } finally {
      setLoading(false);
    }
  };

  const fetchPublicGroups = useCallback(async () => {
    try {
      const response = await api.get('/api/groups/discover/', {
        params: { query: searchQuery }
      });
      setPublicGroups(response.data.public_groups);
    } catch (error) {
      console.error('Error fetching public groups:', error);
      toast.error('Failed to fetch public groups');
    }
  }, [searchQuery]);

  useEffect(() => {
    fetchUserGroups();
  }, []);

  useEffect(() => {
    if (activeTab === 'discover') {
      fetchPublicGroups();
    }
  }, [activeTab, fetchPublicGroups]);

  const handleCreateGroup = async (e) => {
    e.preventDefault();
    try {
      await api.post('/api/groups/', createFormData);
      toast.success('Group created successfully!');
      setShowCreateModal(false);
      setCreateFormData({
        name: '',
        description: '',
        group_type: 'study',
        course_code: '',
        subject: '',
        is_public: false,
        max_members: 50
      });
      fetchUserGroups();
    } catch (error) {
      console.error('Error creating group:', error);
      const errorMessage = error.response?.data?.message || 
                          error.response?.data?.errors || 
                          'Failed to create group';
      toast.error(typeof errorMessage === 'object' ? 
                 Object.values(errorMessage).join(', ') : 
                 errorMessage);
    }
  };

  const handleJoinGroup = async (e) => {
    e.preventDefault();
    try {
      await api.post('/api/groups/join/', { join_code: joinCode });
      toast.success('Successfully joined the group!');
      setShowJoinModal(false);
      setJoinCode('');
      fetchUserGroups();
    } catch (error) {
      console.error('Error joining group:', error);
      const errorMessage = error.response?.data?.message || 
                          error.response?.data?.errors || 
                          'Failed to join group';
      toast.error(typeof errorMessage === 'object' ? 
                 Object.values(errorMessage).join(', ') : 
                 errorMessage);
    }
  };

  const handleJoinPublicGroup = async (groupId) => {
    try {
      await api.post('/api/groups/join/', { group_id: groupId });
      toast.success('Successfully joined the group!');
      fetchUserGroups();
      fetchPublicGroups();
    } catch (error) {
      console.error('Error joining group:', error);
      toast.error(error.response?.data?.message || 'Failed to join group');
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

  const getGroupTypeDescription = (type) => {
    const descriptions = {
      course: 'Faculty-led course groups for formal assessments',
      study: 'Student-created collaborative study groups',
      public: 'Open groups for community learning',
      self: 'Personal practice and self-assessment'
    };
    return descriptions[type] || '';
  };

  const renderGroupCard = (group, showJoinButton = false) => (
    <div key={group.id} className="bg-white rounded-lg shadow-sm border border-gray-200 p-6 hover:shadow-md transition-shadow">
      <div className="flex items-start justify-between mb-4">
        <div className="flex items-center space-x-3">
          <span className="text-2xl">{getGroupTypeIcon(group.group_type)}</span>
          <div>
            <h3 className="text-lg font-semibold text-gray-900">{group.name}</h3>
            <p className="text-sm text-gray-500">{group.course_code || 'No course code'}</p>
          </div>
        </div>
        <div className="flex space-x-2">
          <span className={`inline-flex px-2 py-1 text-xs font-semibold rounded-full ${
            group.is_active 
              ? 'bg-green-100 text-green-800'
              : 'bg-red-100 text-red-800'
          }`}>
            {group.is_active ? 'Active' : 'Inactive'}
          </span>
          <span className={`inline-flex px-2 py-1 text-xs font-semibold rounded-full ${
            group.is_public 
              ? 'bg-blue-100 text-blue-800'
              : 'bg-gray-100 text-gray-800'
          }`}>
            {group.is_public ? 'Public' : 'Private'}
          </span>
        </div>
      </div>
      
      <p className="text-sm text-gray-600 mb-4">{group.description || 'No description available'}</p>
      
      <div className="flex items-center justify-between text-sm text-gray-500 mb-4">
        <div className="flex space-x-4">
          <span>👥 {group.member_count}/{group.max_members} members</span>
          <span>📝 {group.quiz_count} quizzes</span>
          {group.user_role && (
            <span className="text-blue-600 font-medium">Role: {group.user_role}</span>
          )}
        </div>
      </div>
      
      <div className="flex space-x-2">
        {showJoinButton ? (
          <button
            onClick={() => handleJoinPublicGroup(group.id)}
            className="text-sm px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700 transition-colors"
          >
            Join Group
          </button>
        ) : (
          <>
            <button
              onClick={() => window.location.href = `/groups/${group.id}`}
              className="text-sm px-3 py-1 text-blue-600 border border-blue-600 rounded hover:bg-blue-50 transition-colors"
            >
              View Details
            </button>
            {group.can_manage && (
              <button
                onClick={() => window.location.href = `/groups/${group.id}/manage`}
                className="text-sm px-3 py-1 text-green-600 border border-green-600 rounded hover:bg-green-50 transition-colors"
              >
                Manage
              </button>
            )}
          </>
        )}
      </div>
    </div>
  );

  const renderGroupSection = (type, groups) => {
    if (groups.length === 0) return null;
    
    return (
      <div className="mb-8">
        <div className="flex items-center space-x-3 mb-4">
          <span className="text-2xl">{getGroupTypeIcon(type)}</span>
          <div>
            <h2 className="text-xl font-semibold text-gray-900 capitalize">{type} Groups</h2>
            <p className="text-sm text-gray-600">{getGroupTypeDescription(type)}</p>
          </div>
        </div>
        
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {groups.map(group => renderGroupCard(group))}
        </div>
      </div>
    );
  };

  return (
    <div className="min-h-screen bg-gray-50">
      <Navbar />
      
      <main className="max-w-7xl mx-auto py-6 sm:px-6 lg:px-8">
        <div className="px-4 py-6 sm:px-0">
          {/* Header */}
          <div className="flex justify-between items-center mb-8">
            <div>
              <h1 className="text-3xl font-bold text-gray-900">Groups</h1>
              <p className="mt-2 text-gray-600">
                {user?.role === 'instructor' && 'Manage course groups and collaborate with students'}
                {user?.role === 'student' && 'Join study groups and participate in collaborative learning'}
                {user?.role === 'admin' && 'Oversee all groups and manage the platform'}
              </p>
            </div>
            <div className="flex space-x-3">
              <button
                onClick={() => setShowJoinModal(true)}
                className="bg-green-600 text-white px-4 py-2 rounded-lg hover:bg-green-700 transition-colors"
              >
                Join Group
              </button>
              <button
                onClick={() => setShowCreateModal(true)}
                className="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 transition-colors"
              >
                Create Group
              </button>
            </div>
          </div>

          {/* Tabs */}
          <div className="border-b border-gray-200 mb-6">
            <nav className="-mb-px flex space-x-8">
              <button
                onClick={() => setActiveTab('my-groups')}
                className={`py-2 px-1 border-b-2 font-medium text-sm ${
                  activeTab === 'my-groups'
                    ? 'border-blue-500 text-blue-600'
                    : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                }`}
              >
                My Groups
              </button>
              <button
                onClick={() => setActiveTab('discover')}
                className={`py-2 px-1 border-b-2 font-medium text-sm ${
                  activeTab === 'discover'
                    ? 'border-blue-500 text-blue-600'
                    : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                }`}
              >
                Discover Groups
              </button>
              {user?.role === 'admin' && (
                <button
                  onClick={() => setActiveTab('validator')}
                  className={`py-2 px-1 border-b-2 font-medium text-sm ${
                    activeTab === 'validator'
                      ? 'border-blue-500 text-blue-600'
                      : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                  }`}
                >
                  System Check
                </button>
              )}
            </nav>
          </div>

          {/* Content */}
          {activeTab === 'my-groups' && (
            <div>
              {loading ? (
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                  {[1, 2, 3, 4, 5, 6].map((index) => (
                    <div key={index} className="bg-white rounded-lg shadow-sm border border-gray-200 p-6 animate-pulse">
                      <div className="h-6 bg-gray-200 rounded w-3/4 mb-4"></div>
                      <div className="h-4 bg-gray-200 rounded w-full mb-2"></div>
                      <div className="h-4 bg-gray-200 rounded w-2/3 mb-4"></div>
                      <div className="flex space-x-2">
                        <div className="h-8 bg-gray-200 rounded w-16"></div>
                        <div className="h-8 bg-gray-200 rounded w-16"></div>
                      </div>
                    </div>
                  ))}
                </div>
              ) : (
                <>
                  {renderGroupSection('course', groupsByType.course)}
                  {renderGroupSection('study', groupsByType.study)}
                  {renderGroupSection('public', groupsByType.public)}
                  {renderGroupSection('self', groupsByType.self)}
                  
                  {Object.values(groupsByType).every(groups => groups.length === 0) && (
                    <div className="text-center py-12">
                      <div className="mx-auto h-24 w-24 text-gray-400 mb-4 text-6xl">
                        👥
                      </div>
                      <h3 className="text-lg font-medium text-gray-900 mb-2">No Groups Yet</h3>
                      <p className="text-gray-500 mb-4">
                        Get started by creating a group or joining an existing one.
                      </p>
                      <div className="flex justify-center space-x-3">
                        <button
                          onClick={() => setShowCreateModal(true)}
                          className="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 transition-colors"
                        >
                          Create Group
                        </button>
                        <button
                          onClick={() => setShowJoinModal(true)}
                          className="bg-green-600 text-white px-4 py-2 rounded-lg hover:bg-green-700 transition-colors"
                        >
                          Join Group
                        </button>
                      </div>
                    </div>
                  )}
                </>
              )}
            </div>
          )}

          {activeTab === 'discover' && (
            <div>
              {/* Search */}
              <div className="mb-6">
                <div className="flex space-x-4">
                  <div className="flex-1">
                    <input
                      type="text"
                      placeholder="Search public groups..."
                      value={searchQuery}
                      onChange={(e) => setSearchQuery(e.target.value)}
                      className="w-full border border-gray-300 rounded-md px-4 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
                    />
                  </div>
                  <button
                    onClick={fetchPublicGroups}
                    className="bg-blue-600 text-white px-6 py-2 rounded-md hover:bg-blue-700 transition-colors"
                  >
                    Search
                  </button>
                </div>
              </div>

              {/* Public Groups */}
              <div>
                <h2 className="text-xl font-semibold text-gray-900 mb-4">Public Groups</h2>
                {publicGroups.length > 0 ? (
                  <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                    {publicGroups.map(group => renderGroupCard(group, true))}
                  </div>
                ) : (
                  <div className="text-center py-8">
                    <p className="text-gray-500">No public groups found. Try adjusting your search.</p>
                  </div>
                )}
              </div>
            </div>
          )}

          {/* System Validator Tab */}
          {activeTab === 'validator' && (
            <div className="space-y-6">
              <div>
                <h2 className="text-xl font-semibold text-gray-900 mb-4">Groups System Validation</h2>
                <p className="text-gray-600 mb-6">
                  This tool validates the Groups system functionality and backend integration.
                </p>
              </div>
              <GroupSystemValidator />
            </div>
          )}
        </div>
      </main>

      {/* Create Group Modal */}
      {showCreateModal && (
        <div className="fixed inset-0 bg-gray-600 bg-opacity-50 overflow-y-auto h-full w-full z-50">
          <div className="relative top-20 mx-auto p-5 border w-96 shadow-lg rounded-md bg-white">
            <div className="mt-3">
              <h3 className="text-lg font-medium text-gray-900 mb-4">Create New Group</h3>
              <form onSubmit={handleCreateGroup} className="space-y-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700">Group Name</label>
                  <input
                    type="text"
                    value={createFormData.name}
                    onChange={(e) => setCreateFormData({...createFormData, name: e.target.value})}
                    className="mt-1 block w-full border border-gray-300 rounded-md px-3 py-2"
                    required
                  />
                </div>
                
                <div>
                  <label className="block text-sm font-medium text-gray-700">Group Type</label>
                  <select
                    value={createFormData.group_type}
                    onChange={(e) => setCreateFormData({...createFormData, group_type: e.target.value})}
                    className="mt-1 block w-full border border-gray-300 rounded-md px-3 py-2"
                  >
                    {user?.role === 'instructor' && <option value="course">Course Group</option>}
                    <option value="study">Study Group</option>
                    <option value="public">Public Group</option>
                    <option value="self">Self Assessment</option>
                  </select>
                </div>
                
                {createFormData.group_type === 'course' && (
                  <div>
                    <label className="block text-sm font-medium text-gray-700">Course Code</label>
                    <input
                      type="text"
                      value={createFormData.course_code}
                      onChange={(e) => setCreateFormData({...createFormData, course_code: e.target.value})}
                      className="mt-1 block w-full border border-gray-300 rounded-md px-3 py-2"
                    />
                  </div>
                )}
                
                <div>
                  <label className="block text-sm font-medium text-gray-700">Subject</label>
                  <input
                    type="text"
                    value={createFormData.subject}
                    onChange={(e) => setCreateFormData({...createFormData, subject: e.target.value})}
                    className="mt-1 block w-full border border-gray-300 rounded-md px-3 py-2"
                  />
                </div>
                
                <div>
                  <label className="block text-sm font-medium text-gray-700">Description</label>
                  <textarea
                    value={createFormData.description}
                    onChange={(e) => setCreateFormData({...createFormData, description: e.target.value})}
                    className="mt-1 block w-full border border-gray-300 rounded-md px-3 py-2"
                    rows="3"
                  />
                </div>
                
                {createFormData.group_type !== 'self' && (
                  <div>
                    <label className="block text-sm font-medium text-gray-700">Maximum Members</label>
                    <input
                      type="number"
                      min="1"
                      max="200"
                      value={createFormData.max_members}
                      onChange={(e) => setCreateFormData({...createFormData, max_members: parseInt(e.target.value)})}
                      className="mt-1 block w-full border border-gray-300 rounded-md px-3 py-2"
                    />
                  </div>
                )}
                
                {createFormData.group_type !== 'self' && createFormData.group_type !== 'public' && (
                  <div className="flex items-center">
                    <input
                      type="checkbox"
                      checked={createFormData.is_public}
                      onChange={(e) => setCreateFormData({...createFormData, is_public: e.target.checked})}
                      className="mr-2"
                    />
                    <label className="text-sm font-medium text-gray-700">Make group public</label>
                  </div>
                )}
                
                <div className="flex justify-end space-x-2 pt-4">
                  <button
                    type="button"
                    onClick={() => setShowCreateModal(false)}
                    className="px-4 py-2 text-sm font-medium text-gray-700 bg-gray-200 rounded-md hover:bg-gray-300"
                  >
                    Cancel
                  </button>
                  <button
                    type="submit"
                    className="px-4 py-2 text-sm font-medium text-white bg-blue-600 rounded-md hover:bg-blue-700"
                  >
                    Create Group
                  </button>
                </div>
              </form>
            </div>
          </div>
        </div>
      )}

      {/* Join Group Modal */}
      {showJoinModal && (
        <div className="fixed inset-0 bg-gray-600 bg-opacity-50 overflow-y-auto h-full w-full z-50">
          <div className="relative top-20 mx-auto p-5 border w-96 shadow-lg rounded-md bg-white">
            <div className="mt-3">
              <h3 className="text-lg font-medium text-gray-900 mb-4">Join Group</h3>
              <form onSubmit={handleJoinGroup} className="space-y-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700">Join Code</label>
                  <input
                    type="text"
                    value={joinCode}
                    onChange={(e) => setJoinCode(e.target.value)}
                    className="mt-1 block w-full border border-gray-300 rounded-md px-3 py-2"
                    placeholder="Enter group join code"
                    required
                  />
                </div>
                
                <div className="flex justify-end space-x-2 pt-4">
                  <button
                    type="button"
                    onClick={() => setShowJoinModal(false)}
                    className="px-4 py-2 text-sm font-medium text-gray-700 bg-gray-200 rounded-md hover:bg-gray-300"
                  >
                    Cancel
                  </button>
                  <button
                    type="submit"
                    className="px-4 py-2 text-sm font-medium text-white bg-green-600 rounded-md hover:bg-green-700"
                  >
                    Join Group
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

export default GroupsDashboard;
