import React, { useState, useEffect, useCallback } from 'react';
import api from '../services/api';

const GroupSystemValidator = () => {
  const [validationResults, setValidationResults] = useState({
    backendConnectivity: null,
    authenticationFlow: null,
    groupCreation: null,
    groupDiscovery: null,
    topicSearch: null,
  });
  const [loading, setLoading] = useState(false);

  const runValidation = useCallback(async () => {
    setLoading(true);
    const results = { ...validationResults };

    try {
      // Test 1: Backend Connectivity
      try {
        const response = await api.get('/api/groups/discover/');
        results.backendConnectivity = response.status === 200 ? '✅ Connected' : '⚠️ Issues';
      } catch (error) {
        if (error.response?.status === 401) {
          results.backendConnectivity = '🔐 Auth Required (Normal)';
        } else {
          results.backendConnectivity = '❌ Connection Failed';
        }
      }

      // Test 2: Authentication Flow
      try {
        const response = await api.get('/api/groups/by-type/');
        results.authenticationFlow = response.status === 200 ? '✅ Auth Working' : '❌ Auth Issues';
      } catch (error) {
        results.authenticationFlow = error.response?.status === 401 ? 
          '🔐 Unauthenticated (Expected)' : '❌ Auth Error';
      }

      // Test 3: Group Creation Endpoint
      try {
        // This should fail without auth, but endpoint should exist
        await api.post('/api/groups/', {});
        results.groupCreation = '⚠️ Unexpected Success';
      } catch (error) {
        results.groupCreation = error.response?.status === 401 ? 
          '✅ Endpoint Available' : '❌ Endpoint Error';
      }

      // Test 4: Group Discovery
      try {
        const response = await api.get('/api/groups/discover/');
        results.groupDiscovery = response.status === 200 || response.status === 401 ? 
          '✅ Discovery Ready' : '❌ Discovery Issues';
      } catch (error) {
        results.groupDiscovery = '❌ Discovery Failed';
      }

      // Test 5: Topic Search
      try {
        const response = await api.get('/api/groups/search-by-topic/', { params: { topic: 'test' } });
        results.topicSearch = response.status === 200 || response.status === 401 ? 
          '✅ Topic Search Ready' : '❌ Topic Search Issues';
      } catch (error) {
        results.topicSearch = '❌ Topic Search Failed';
      }

    } catch (error) {
      console.error('Validation error:', error);
    }

    setValidationResults(results);
    setLoading(false);
  }, []);

  useEffect(() => {
    runValidation();
  }, [runValidation]);

  return (
    <div className="bg-white shadow rounded-lg p-6 max-w-2xl mx-auto">
      <div className="flex items-center justify-between mb-6">
        <h2 className="text-xl font-bold text-gray-900">Groups System Validation</h2>
        <button
          onClick={runValidation}
          disabled={loading}
          className="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700 disabled:opacity-50"
        >
          {loading ? 'Validating...' : 'Re-validate'}
        </button>
      </div>

      <div className="space-y-4">
        {Object.entries(validationResults).map(([test, result]) => (
          <div key={test} className="flex items-center justify-between p-3 bg-gray-50 rounded">
            <span className="font-medium text-gray-700">
              {test.replace(/([A-Z])/g, ' $1').replace(/^./, str => str.toUpperCase())}
            </span>
            <span className="text-sm">
              {result || (loading ? '⏳ Testing...' : '⚪ Pending')}
            </span>
          </div>
        ))}
      </div>

      <div className="mt-6 p-4 bg-blue-50 rounded-lg">
        <h3 className="font-medium text-blue-900 mb-2">System Status</h3>
        <div className="text-sm text-blue-800">
          {loading ? (
            '🔄 Running validation tests...'
          ) : (
            <>
              {Object.values(validationResults).every(result => 
                result && (result.includes('✅') || result.includes('🔐'))) ? (
                '🎉 All systems operational! Groups functionality is ready.'
              ) : (
                '⚠️ Some issues detected. Check individual test results above.'
              )}
            </>
          )}
        </div>
      </div>

      <div className="mt-4 text-xs text-gray-500">
        <p>• 🔐 Auth Required responses are normal for protected endpoints</p>
        <p>• ✅ indicates the endpoint is working correctly</p>
        <p>• ❌ indicates an issue that needs attention</p>
      </div>
    </div>
  );
};

export default GroupSystemValidator;
