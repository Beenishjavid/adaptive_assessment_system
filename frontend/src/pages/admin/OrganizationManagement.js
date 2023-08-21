import React, { useState, useEffect } from 'react';
import { useAuth } from '../../context/AuthContext';
import Navbar from '../../components/Navbar';
import api from '../../services/api';
import toast from 'react-hot-toast';

const OrganizationManagement = () => {
  const { user } = useAuth();
  const [organizations, setOrganizations] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showAddModal, setShowAddModal] = useState(false);
  const [editingOrg, setEditingOrg] = useState(null);
  const [formData, setFormData] = useState({
    name: '',
    description: '',
    address: '',
    contact_email: '',
    contact_phone: '',
    is_active: true
  });

  useEffect(() => {
    if (user?.role === 'admin') {
      fetchOrganizations();
    }
  }, [user]);

  const fetchOrganizations = async () => {
    try {
      setLoading(true);
      const response = await api.get('/api/organizations/admin/organizations/');
      setOrganizations(response.data.organizations || []);
    } catch (error) {
      console.error('Error fetching organizations:', error);
      toast.error('Failed to fetch organizations');
    } finally {
      setLoading(false);
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      if (editingOrg) {
        await api.put(`/api/organizations/admin/organizations/${editingOrg.id}/`, formData);
        toast.success('Organization updated successfully');
      } else {
        await api.post('/api/organizations/admin/organizations/create/', formData);
        toast.success('Organization created successfully');
      }
      
      setShowAddModal(false);
      setEditingOrg(null);
      setFormData({
        name: '',
        description: '',
        address: '',
        contact_email: '',
        contact_phone: '',
        is_active: true
      });
      fetchOrganizations();
    } catch (error) {
      console.error('Error saving organization:', error);
      toast.error('Failed to save organization');
    }
  };

  const handleEdit = (org) => {
    setEditingOrg(org);
    setFormData({
      name: org.name,
      description: org.description || '',
      address: org.address || '',
      contact_email: org.contact_email || '',
      contact_phone: org.contact_phone || '',
      is_active: org.is_active
    });
    setShowAddModal(true);
  };

  const handleDelete = async (orgId) => {
    if (window.confirm('Are you sure you want to delete this organization? This will affect all associated users.')) {
      try {
        await api.delete(`/api/organizations/admin/organizations/${orgId}/`);
        toast.success('Organization deleted successfully');
        fetchOrganizations();
      } catch (error) {
        console.error('Error deleting organization:', error);
        toast.error('Failed to delete organization');
      }
    }
  };

  const toggleOrgStatus = async (orgId, currentStatus) => {
    try {
      await api.patch(`/api/organizations/admin/organizations/${orgId}/`, { is_active: !currentStatus });
      toast.success(`Organization ${!currentStatus ? 'activated' : 'deactivated'} successfully`);
      fetchOrganizations();
    } catch (error) {
      console.error('Error updating organization status:', error);
      toast.error('Failed to update organization status');
    }
  };

  if (user?.role !== 'admin') {
    return (
      <div className="min-h-screen bg-gray-50">
        <Navbar />
        <div className="max-w-7xl mx-auto py-6 sm:px-6 lg:px-8">
          <div className="text-center">
            <h1 className="text-2xl font-bold text-gray-900">Access Denied</h1>
            <p className="mt-2 text-gray-600">You don't have permission to access this page.</p>
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
              <h1 className="text-3xl font-bold text-gray-900">Organization Management</h1>
              <p className="mt-2 text-gray-600">Manage organizations and their settings</p>
            </div>
            <button
              onClick={() => {
                setEditingOrg(null);
                setFormData({
                  name: '',
                  description: '',
                  address: '',
                  contact_email: '',
                  contact_phone: '',
                  is_active: true
                });
                setShowAddModal(true);
              }}
              className="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 transition-colors"
            >
              Add New Organization
            </button>
          </div>

          {/* Organizations Grid */}
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
              {organizations.map((org) => (
                <div key={org.id} className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
                  <div className="flex items-start justify-between mb-4">
                    <h3 className="text-lg font-semibold text-gray-900">{org.name}</h3>
                    <span className={`inline-flex px-2 py-1 text-xs font-semibold rounded-full ${
                      org.is_active 
                        ? 'bg-green-100 text-green-800'
                        : 'bg-red-100 text-red-800'
                    }`}>
                      {org.is_active ? 'Active' : 'Inactive'}
                    </span>
                  </div>
                  
                  <div className="mb-4">
                    <p className="text-sm text-gray-600 mb-2">{org.description || 'No description'}</p>
                    {org.address && (
                      <p className="text-sm text-gray-500 mb-1">📍 {org.address}</p>
                    )}
                    {org.contact_email && (
                      <p className="text-sm text-gray-500 mb-1">✉️ {org.contact_email}</p>
                    )}
                    {org.contact_phone && (
                      <p className="text-sm text-gray-500 mb-1">📞 {org.contact_phone}</p>
                    )}
                    <p className="text-sm text-gray-500">👥 {org.user_count || 0} users</p>
                  </div>
                  
                  <div className="flex space-x-2">
                    <button
                      onClick={() => handleEdit(org)}
                      className="text-xs px-3 py-1 text-blue-600 border border-blue-600 rounded hover:bg-blue-50"
                    >
                      Edit
                    </button>
                    <button
                      onClick={() => toggleOrgStatus(org.id, org.is_active)}
                      className={`text-xs px-3 py-1 border rounded hover:bg-opacity-50 ${
                        org.is_active 
                          ? 'text-red-600 border-red-600 hover:bg-red-50'
                          : 'text-green-600 border-green-600 hover:bg-green-50'
                      }`}
                    >
                      {org.is_active ? 'Deactivate' : 'Activate'}
                    </button>
                    <button
                      onClick={() => handleDelete(org.id)}
                      className="text-xs px-3 py-1 text-red-600 border border-red-600 rounded hover:bg-red-50"
                    >
                      Delete
                    </button>
                  </div>
                </div>
              ))}
            </div>
          )}
          
          {!loading && organizations.length === 0 && (
            <div className="text-center py-12">
              <div className="mx-auto h-24 w-24 text-gray-400 mb-4">
                🏢
              </div>
              <h3 className="text-lg font-medium text-gray-900 mb-2">No Organizations</h3>
              <p className="text-gray-500 mb-4">Get started by creating your first organization.</p>
              <button
                onClick={() => setShowAddModal(true)}
                className="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 transition-colors"
              >
                Add Organization
              </button>
            </div>
          )}
        </div>
      </main>

      {/* Add/Edit Organization Modal */}
      {showAddModal && (
        <div className="fixed inset-0 bg-gray-600 bg-opacity-50 overflow-y-auto h-full w-full z-50">
          <div className="relative top-20 mx-auto p-5 border w-96 shadow-lg rounded-md bg-white">
            <div className="mt-3">
              <h3 className="text-lg font-medium text-gray-900 mb-4">
                {editingOrg ? 'Edit Organization' : 'Add New Organization'}
              </h3>
              <form onSubmit={handleSubmit} className="space-y-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700">Organization Name</label>
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
                  <label className="block text-sm font-medium text-gray-700">Address</label>
                  <textarea
                    value={formData.address}
                    onChange={(e) => setFormData({...formData, address: e.target.value})}
                    className="mt-1 block w-full border border-gray-300 rounded-md px-3 py-2"
                    rows="2"
                  />
                </div>
                
                <div>
                  <label className="block text-sm font-medium text-gray-700">Contact Email</label>
                  <input
                    type="email"
                    value={formData.contact_email}
                    onChange={(e) => setFormData({...formData, contact_email: e.target.value})}
                    className="mt-1 block w-full border border-gray-300 rounded-md px-3 py-2"
                  />
                </div>
                
                <div>
                  <label className="block text-sm font-medium text-gray-700">Contact Phone</label>
                  <input
                    type="tel"
                    value={formData.contact_phone}
                    onChange={(e) => setFormData({...formData, contact_phone: e.target.value})}
                    className="mt-1 block w-full border border-gray-300 rounded-md px-3 py-2"
                  />
                </div>
                
                <div className="flex items-center">
                  <input
                    type="checkbox"
                    checked={formData.is_active}
                    onChange={(e) => setFormData({...formData, is_active: e.target.checked})}
                    className="mr-2"
                  />
                  <label className="text-sm font-medium text-gray-700">Active</label>
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
                    {editingOrg ? 'Update' : 'Create'}
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

export default OrganizationManagement;
