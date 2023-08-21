import React, { useState, useEffect } from 'react';
import { useAuth } from '../context/AuthContext';
import Navbar from '../components/Navbar';
import api from '../services/api';
import toast from 'react-hot-toast';

const GroupManagement = () => {
  const { user } = useAuth();
  const [groups, setGroups] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showAddModal, setShowAddModal] = useState(false);
  const [editingGroup, setEditingGroup] = useState(null);
  const [formData, setFormData] = useState({
    name: '',
    description: '',
    is_public: false,
    max_members: 50
  });

  useEffect(() => {
    if (user?.role === 'instructor' || user?.role === 'admin') {
      fetchGroups();
    }
  }, [user]);

  const fetchGroups = async () => {
    try {
      setLoading(true);
      const response = await api.get('/api/groups/my-groups/');
      setGroups(response.data.groups || []);
    } catch (error) {
      console.error('Error fetching groups:', error);
      toast.error('Failed to fetch groups');
    } finally {
      setLoading(false);
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      if (editingGroup) {
        await api.put(`/api/groups/${editingGroup.id}/`, formData);
        toast.success('Group updated successfully');
      } else {
        await api.post('/api/groups/create/', formData);
        toast.success('Group created successfully');
      }
      
      setShowAddModal(false);
      setEditingGroup(null);
      setFormData({
        name: '',
        description: '',
        is_public: false,
        max_members: 50
      });
      fetchGroups();
    } catch (error) {
      console.error('Error saving group:', error);
      toast.error('Failed to save group');
    }
  };

  const handleEdit = (group) => {
    setEditingGroup(group);
    setFormData({
      name: group.name,
      description: group.description || '',
      is_public: group.is_public,
      max_members: group.max_members || 50
    });
    setShowAddModal(true);
  };

  const handleDelete = async (groupId) => {
    if (window.confirm('Are you sure you want to delete this group? This action cannot be undone.')) {
      try {
        await api.delete(`/api/groups/${groupId}/`);
        toast.success('Group deleted successfully');
        fetchGroups();
      } catch (error) {
        console.error('Error deleting group:', error);
        toast.error('Failed to delete group');
      }
    }
  };

  const toggleGroupStatus = async (groupId, currentStatus) => {
    try {
      await api.patch(`/api/groups/${groupId}/`, { is_active: !currentStatus });
      toast.success(`Group ${!currentStatus ? 'activated' : 'deactivated'} successfully`);
      fetchGroups();
    } catch (error) {
      console.error('Error updating group status:', error);
      toast.error('Failed to update group status');
    }
  };

  if (user?.role === 'student') {
    return (
      <div className="min-h-screen bg-gray-50">
        <Navbar />
        <div className="max-w-7xl mx-auto py-6 sm:px-6 lg:px-8">
          <div className="text-center">
            <h1 className="text-2xl font-bold text-gray-900">Access Denied</h1>
            <p className="mt-2 text-gray-600">You don't have permission to manage groups.</p>
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
          <div className="flex justify-between items-center mb-8">
            <div>
              <h1 className="text-3xl font-bold text-gray-900">Group Management</h1>
              <p className="mt-2 text-gray-600">Create and manage study groups</p>
            </div>
            <button
              onClick={() => {
                setEditingGroup(null);
                setFormData({
                  name: '',
                  description: '',
                  is_public: false,
                  max_members: 50
                });
                setShowAddModal(true);
              }}
              className="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 transition-colors"
            >
              Create New Group
            </button>
          </div>

          {/* Groups Grid */}
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
                    <div className="h-8 bg-gray-200 rounded w-16"></div>
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
              {groups.map((group) => (
                <div key={group.id} className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
                  <div className="flex items-start justify-between mb-4">
                    <h3 className="text-lg font-semibold text-gray-900">{group.name}</h3>
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
                  
                  <div className="mb-4">
                    <p className="text-sm text-gray-600 mb-2">{group.description || 'No description'}</p>
                    <div className="flex items-center justify-between text-sm text-gray-500">
                      <span>👥 {group.member_count || 0} / {group.max_members || 50} members</span>
                      <span>📚 {group.quiz_count || 0} quizzes</span>
                    </div>
                  </div>
                  
                  <div className="flex space-x-2">
                    <button
                      onClick={() => handleEdit(group)}
                      className="text-xs px-3 py-1 text-blue-600 border border-blue-600 rounded hover:bg-blue-50"
                    >
                      Edit
                    </button>
                    <button
                      onClick={() => toggleGroupStatus(group.id, group.is_active)}
                      className={`text-xs px-3 py-1 border rounded hover:bg-opacity-50 ${
                        group.is_active 
                          ? 'text-red-600 border-red-600 hover:bg-red-50'
                          : 'text-green-600 border-green-600 hover:bg-green-50'
                      }`}
                    >
                      {group.is_active ? 'Deactivate' : 'Activate'}
                    </button>
                    <button
                      onClick={() => handleDelete(group.id)}
                      className="text-xs px-3 py-1 text-red-600 border border-red-600 rounded hover:bg-red-50"
                    >
                      Delete
                    </button>
                  </div>
                </div>
              ))}
            </div>
          )}
          
          {!loading && groups.length === 0 && (
            <div className="text-center py-12">
              <div className="mx-auto h-24 w-24 text-gray-400 mb-4">
                👥
              </div>
              <h3 className="text-lg font-medium text-gray-900 mb-2">No Groups</h3>
              <p className="text-gray-500 mb-4">Get started by creating your first study group.</p>
              <button
                onClick={() => setShowAddModal(true)}
                className="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 transition-colors"
              >
                Create Group
              </button>
            </div>
          )}
        </div>
      </main>

      {/* Add/Edit Group Modal */}
      {showAddModal && (
        <div className="fixed inset-0 bg-gray-600 bg-opacity-50 overflow-y-auto h-full w-full z-50">
          <div className="relative top-20 mx-auto p-5 border w-96 shadow-lg rounded-md bg-white">
            <div className="mt-3">
              <h3 className="text-lg font-medium text-gray-900 mb-4">
                {editingGroup ? 'Edit Group' : 'Create New Group'}
              </h3>
              <form onSubmit={handleSubmit} className="space-y-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700">Group Name</label>
                  <input
                    type="text"
                    value={formData.name}
                    onChange={(e) => setFormData({...formData, name: e.target.value})}
                    className="mt-1 block w-full border border-gray-300 rounded-md px-3 py-2"
                    required
                  />
                </div>
                
                <div>
                  <label className="block text-sm font-medium text-gray-700">Description</label>
                  <textarea
                    value={formData.description}
                    onChange={(e) => setFormData({...formData, description: e.target.value})}
                    className="mt-1 block w-full border border-gray-300 rounded-md px-3 py-2"
                    rows="3"
                  />
                </div>
                
                <div>
                  <label className="block text-sm font-medium text-gray-700">Maximum Members</label>
                  <input
                    type="number"
                    min="1"
                    max="200"
                    value={formData.max_members}
                    onChange={(e) => setFormData({...formData, max_members: parseInt(e.target.value)})}
                    className="mt-1 block w-full border border-gray-300 rounded-md px-3 py-2"
                  />
                </div>
                
                <div className="flex items-center">
                  <input
                    type="checkbox"
                    checked={formData.is_public}
                    onChange={(e) => setFormData({...formData, is_public: e.target.checked})}
                    className="mr-2"
                  />
                  <label className="text-sm font-medium text-gray-700">Public Group (anyone can join)</label>
                </div>
                
                <div className="flex justify-end space-x-2">
                  <button
                    type="button"
                    onClick={() => setShowAddModal(false)}
                    className="px-4 py-2 text-sm font-medium text-gray-700 bg-gray-200 rounded-md hover:bg-gray-300"
                  >
                    Cancel
                  </button>
                  <button
                    type="submit"
                    className="px-4 py-2 text-sm font-medium text-white bg-blue-600 rounded-md hover:bg-blue-700"
                  >
                    {editingGroup ? 'Update' : 'Create'}
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

export default GroupManagement;
