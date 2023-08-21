import React, { useState } from 'react';
import { useAuth } from '../context/AuthContext';
import Navbar from '../components/Navbar';
import api from '../services/api';
import toast from 'react-hot-toast';

const TopicQuizSearch = () => {
  useAuth(); // Ensure user is authenticated
  const [searchTopic, setSearchTopic] = useState('');
  const [availableQuizzes, setAvailableQuizzes] = useState([]);
  const [relevantGroups, setRelevantGroups] = useState([]);
  const [loading, setLoading] = useState(false);
  const [hasSearched, setHasSearched] = useState(false);

  const popularTopics = [
    'Mathematics', 'Science', 'Programming', 'History', 'English',
    'Physics', 'Chemistry', 'Biology', 'Geography', 'Literature'
  ];

  const handleSearch = async () => {
    if (!searchTopic.trim()) {
      toast.error('Please enter a topic to search');
      return;
    }

    try {
      setLoading(true);
      const response = await api.get('/api/groups/search-by-topic/', {
        params: { topic: searchTopic }
      });
      
      setAvailableQuizzes(response.data.available_quizzes);
      setRelevantGroups(response.data.relevant_groups);
      setHasSearched(true);
    } catch (error) {
      console.error('Error searching quizzes by topic:', error);
      toast.error('Failed to search quizzes');
    } finally {
      setLoading(false);
    }
  };

  const handleQuickTopicSearch = (topic) => {
    setSearchTopic(topic);
    setTimeout(() => handleSearch(), 100);
  };

  const handleTakeQuiz = async (quiz) => {
    try {
      const response = await api.post(`/api/quiz/${quiz.id}/start/`);
      if (response.data.success) {
        window.location.href = `/take-quiz/${response.data.attempt_id}`;
      } else {
        toast.error(response.data.message || 'Failed to start quiz');
      }
    } catch (error) {
      console.error('Error starting quiz:', error);
      toast.error(error.response?.data?.message || 'Failed to start quiz');
    }
  };

  const handleJoinGroup = async (groupId) => {
    try {
      await api.post('/api/groups/join/', { group_id: groupId });
      toast.success('Successfully joined the group!');
      // Refresh search results
      handleSearch();
    } catch (error) {
      console.error('Error joining group:', error);
      toast.error(error.response?.data?.message || 'Failed to join group');
    }
  };

  const renderQuizCard = (quiz) => (
    <div key={quiz.id} className="bg-white rounded-lg shadow-sm border border-gray-200 p-6 hover:shadow-md transition-shadow">
      <div className="flex items-start justify-between mb-4">
        <div className="flex-1">
          <h3 className="text-lg font-semibold text-gray-900 mb-2">{quiz.title}</h3>
          <p className="text-sm text-gray-600 mb-3">{quiz.description || 'No description available'}</p>
          
          <div className="flex items-center space-x-4 text-sm text-gray-500 mb-3">
            <span>⏱️ {quiz.duration_minutes} min</span>
            <span>📝 {quiz.total_questions} questions</span>
            <span>🎯 Pass: {quiz.passing_score}%</span>
            <span className={`px-2 py-1 rounded text-xs font-medium ${
              quiz.visibility === 'public' 
                ? 'bg-green-100 text-green-800'
                : 'bg-blue-100 text-blue-800'
            }`}>
              {quiz.visibility}
            </span>
          </div>
          
          {quiz.created_by && (
            <p className="text-sm text-gray-500">
              Created by: {quiz.created_by.first_name} {quiz.created_by.last_name}
            </p>
          )}
        </div>
      </div>
      
      <div className="flex items-center justify-between">
        <div className="text-sm">
          {quiz.can_attempt ? (
            <span className="text-green-600 font-medium">✓ Available to take</span>
          ) : (
            <span className="text-red-600 font-medium">✗ {quiz.attempt_reason}</span>
          )}
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
          
          {quiz.group && (
            <button
              onClick={() => window.location.href = `/groups/${quiz.group.id}`}
              className="text-blue-600 border border-blue-600 px-4 py-2 rounded-md hover:bg-blue-50 transition-colors"
            >
              View Group
            </button>
          )}
        </div>
      </div>
    </div>
  );

  const renderGroupCard = (group) => (
    <div key={group.id} className="bg-white rounded-lg shadow-sm border border-gray-200 p-6 hover:shadow-md transition-shadow">
      <div className="flex items-start justify-between mb-4">
        <div className="flex items-center space-x-3 flex-1">
          <span className="text-2xl">
            {group.group_type === 'course' ? '🏫' : 
             group.group_type === 'study' ? '📚' : 
             group.group_type === 'public' ? '🌍' : '🎯'}
          </span>
          <div className="flex-1">
            <h3 className="text-lg font-semibold text-gray-900">{group.name}</h3>
            <p className="text-sm text-gray-600">{group.description || 'No description'}</p>
          </div>
        </div>
        
        <span className={`inline-flex px-2 py-1 text-xs font-semibold rounded-full ${
          group.is_public 
            ? 'bg-green-100 text-green-800'
            : 'bg-blue-100 text-blue-800'
        }`}>
          {group.is_public ? 'Public' : 'Private'}
        </span>
      </div>
      
      <div className="flex items-center justify-between text-sm text-gray-500 mb-4">
        <div className="flex space-x-4">
          <span>👥 {group.member_count}/{group.max_members} members</span>
          <span>📝 {group.quiz_count} quizzes</span>
        </div>
      </div>
      
      <div className="flex space-x-2">
        <button
          onClick={() => handleJoinGroup(group.id)}
          className="bg-green-600 text-white px-4 py-2 rounded-md hover:bg-green-700 transition-colors"
        >
          Join Group
        </button>
        <button
          onClick={() => window.location.href = `/groups/${group.id}`}
          className="text-blue-600 border border-blue-600 px-4 py-2 rounded-md hover:bg-blue-50 transition-colors"
        >
          View Details
        </button>
      </div>
    </div>
  );

  return (
    <div className="min-h-screen bg-gray-50">
      <Navbar />
      
      <main className="max-w-7xl mx-auto py-6 sm:px-6 lg:px-8">
        <div className="px-4 py-6 sm:px-0">
          {/* Header */}
          <div className="text-center mb-8">
            <h1 className="text-3xl font-bold text-gray-900 mb-4">Find Quizzes by Topic</h1>
            <p className="text-lg text-gray-600 max-w-3xl mx-auto">
              Search for quizzes on specific topics without joining a group. 
              Find public quizzes and relevant study groups based on your interests.
            </p>
          </div>

          {/* Search Section */}
          <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6 mb-8">
            <div className="flex flex-col sm:flex-row gap-4">
              <div className="flex-1">
                <input
                  type="text"
                  placeholder="Enter a topic (e.g., Mathematics, Programming, History...)"
                  value={searchTopic}
                  onChange={(e) => setSearchTopic(e.target.value)}
                  onKeyPress={(e) => e.key === 'Enter' && handleSearch()}
                  className="w-full border border-gray-300 rounded-md px-4 py-3 focus:outline-none focus:ring-2 focus:ring-blue-500 text-lg"
                />
              </div>
              <button
                onClick={handleSearch}
                disabled={loading}
                className="bg-blue-600 text-white px-8 py-3 rounded-md hover:bg-blue-700 transition-colors disabled:opacity-50 disabled:cursor-not-allowed text-lg font-medium"
              >
                {loading ? 'Searching...' : 'Search'}
              </button>
            </div>
            
            {/* Popular Topics */}
            <div className="mt-6">
              <p className="text-sm font-medium text-gray-700 mb-3">Popular topics:</p>
              <div className="flex flex-wrap gap-2">
                {popularTopics.map((topic) => (
                  <button
                    key={topic}
                    onClick={() => handleQuickTopicSearch(topic)}
                    className="text-sm bg-gray-100 text-gray-700 px-3 py-1 rounded-full hover:bg-gray-200 transition-colors"
                  >
                    {topic}
                  </button>
                ))}
              </div>
            </div>
          </div>

          {/* Search Results */}
          {hasSearched && (
            <div className="space-y-8">
              {/* Available Quizzes */}
              <div>
                <div className="flex items-center justify-between mb-6">
                  <div>
                    <h2 className="text-2xl font-bold text-gray-900">Available Quizzes</h2>
                    <p className="text-gray-600">
                      Public quizzes on "{searchTopic}" that you can take without joining a group
                    </p>
                  </div>
                  <span className="bg-blue-100 text-blue-800 px-3 py-1 rounded-full text-sm font-medium">
                    {availableQuizzes.length} found
                  </span>
                </div>
                
                {availableQuizzes.length > 0 ? (
                  <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                    {availableQuizzes.map(renderQuizCard)}
                  </div>
                ) : (
                  <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-12 text-center">
                    <div className="text-gray-400 text-6xl mb-4">📝</div>
                    <h3 className="text-lg font-medium text-gray-900 mb-2">No Public Quizzes Found</h3>
                    <p className="text-gray-600 mb-4">
                      No public quizzes available on "{searchTopic}". 
                      Check out the relevant groups below or try a different topic.
                    </p>
                  </div>
                )}
              </div>

              {/* Relevant Groups */}
              <div>
                <div className="flex items-center justify-between mb-6">
                  <div>
                    <h2 className="text-2xl font-bold text-gray-900">Relevant Study Groups</h2>
                    <p className="text-gray-600">
                      Join these groups to access more quizzes and collaborative learning on "{searchTopic}"
                    </p>
                  </div>
                  <span className="bg-green-100 text-green-800 px-3 py-1 rounded-full text-sm font-medium">
                    {relevantGroups.length} found
                  </span>
                </div>
                
                {relevantGroups.length > 0 ? (
                  <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                    {relevantGroups.map(renderGroupCard)}
                  </div>
                ) : (
                  <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-12 text-center">
                    <div className="text-gray-400 text-6xl mb-4">👥</div>
                    <h3 className="text-lg font-medium text-gray-900 mb-2">No Relevant Groups Found</h3>
                    <p className="text-gray-600 mb-4">
                      No public groups found for "{searchTopic}". 
                      Consider creating your own study group!
                    </p>
                    <button
                      onClick={() => window.location.href = '/groups'}
                      className="bg-blue-600 text-white px-6 py-2 rounded-md hover:bg-blue-700 transition-colors"
                    >
                      Create Study Group
                    </button>
                  </div>
                )}
              </div>
            </div>
          )}

          {/* Getting Started Section */}
          {!hasSearched && (
            <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-8">
              <div className="text-center">
                <div className="text-gray-400 text-6xl mb-4">🔍</div>
                <h3 className="text-xl font-semibold text-gray-900 mb-4">Find Quizzes by Topic</h3>
                <p className="text-gray-600 mb-6 max-w-2xl mx-auto">
                  Enter any topic you're interested in to discover public quizzes and relevant study groups. 
                  Perfect for self-study and exploring new subjects without committing to a specific group.
                </p>
                
                <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mt-8">
                  <div className="text-center">
                    <div className="text-blue-600 text-3xl mb-3">📝</div>
                    <h4 className="font-semibold text-gray-900 mb-2">Instant Access</h4>
                    <p className="text-sm text-gray-600">
                      Take public quizzes immediately without joining groups
                    </p>
                  </div>
                  <div className="text-center">
                    <div className="text-green-600 text-3xl mb-3">🔍</div>
                    <h4 className="font-semibold text-gray-900 mb-2">Smart Discovery</h4>
                    <p className="text-sm text-gray-600">
                      Find relevant content based on your search terms
                    </p>
                  </div>
                  <div className="text-center">
                    <div className="text-purple-600 text-3xl mb-3">👥</div>
                    <h4 className="font-semibold text-gray-900 mb-2">Join Communities</h4>
                    <p className="text-sm text-gray-600">
                      Discover and join study groups with similar interests
                    </p>
                  </div>
                </div>
              </div>
            </div>
          )}
        </div>
      </main>
    </div>
  );
};

export default TopicQuizSearch;
