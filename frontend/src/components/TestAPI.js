import React, { useState, useEffect } from 'react';

const TestAPI = () => {
  const [data, setData] = useState(null);
  const [error, setError] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    testAPI();
  }, []);

  const testAPI = async () => {
    try {
      setLoading(true);
      setError(null);
      
      // Test the API endpoint directly
      const response = await fetch('http://127.0.0.1:8000/quizzes/api/dashboard/stats/');
      
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      
      const result = await response.json();
      setData(result);
      
    } catch (err) {
      setError(err.message);
      console.error('API Test Error:', err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gray-50 p-8">
      <div className="max-w-4xl mx-auto">
        <h1 className="text-3xl font-bold text-gray-900 mb-8">API Connection Test</h1>
        
        <div className="bg-white shadow rounded-lg p-6 mb-6">
          <h2 className="text-xl font-semibold text-gray-800 mb-4">🔗 Testing Backend Connection</h2>
          
          {loading && (
            <div className="flex items-center">
              <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-500 mr-3"></div>
              <span>Testing API connection...</span>
            </div>
          )}
          
          {error && (
            <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded mb-4">
              <strong>❌ Error:</strong> {error}
              <button 
                onClick={testAPI}
                className="ml-4 bg-red-500 text-white px-3 py-1 rounded text-sm hover:bg-red-600"
              >
                Retry
              </button>
            </div>
          )}
          
          {data && (
            <div className="bg-green-100 border border-green-400 text-green-700 px-4 py-3 rounded">
              <strong>✅ Success!</strong> API is working!
              <pre className="mt-2 text-sm bg-white p-2 rounded border">
                {JSON.stringify(data, null, 2)}
              </pre>
            </div>
          )}
        </div>

        <div className="bg-white shadow rounded-lg p-6">
          <h2 className="text-xl font-semibold text-gray-800 mb-4">🔧 Debug Information</h2>
          <div className="grid grid-cols-2 gap-4 text-sm">
            <div>
              <strong>Backend URL:</strong> http://127.0.0.1:8000
            </div>
            <div>
              <strong>Frontend URL:</strong> http://localhost:3000
            </div>
            <div>
              <strong>API Endpoint:</strong> /quizzes/api/dashboard/stats/
            </div>
            <div>
              <strong>CORS:</strong> Configured
            </div>
          </div>
          
          <div className="mt-4">
            <button 
              onClick={() => window.open('http://127.0.0.1:8000/quizzes/api/dashboard/stats/', '_blank')}
              className="bg-blue-500 text-white px-4 py-2 rounded hover:bg-blue-600 mr-2"
            >
              Open API in New Tab
            </button>
            <button 
              onClick={() => window.open('http://127.0.0.1:8000/admin/', '_blank')}
              className="bg-green-500 text-white px-4 py-2 rounded hover:bg-green-600"
            >
              Open Django Admin
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};

export default TestAPI;
