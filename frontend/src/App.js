import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from 'react-query';
import { Toaster } from 'react-hot-toast';
import { AuthProvider } from './context/AuthContext';
import Login from './pages/Login';
import SignUp from './pages/SignUp';
import ForgotPassword from './pages/ForgotPassword';
import ResetPassword from './pages/ResetPassword';
import Dashboard from './pages/Dashboard';
import QuizList from './components/QuizList';
import CreateQuiz from './pages/CreateQuiz';
import MyQuizzes from './pages/MyQuizzes';
import AvailableQuizzes from './pages/AvailableQuizzes';
import TakeQuiz from './pages/TakeQuiz';
import QuizResult from './pages/QuizResult';
import MyResults from './pages/MyResults';
import GroupManagement from './pages/GroupManagement';
import GroupsDashboard from './pages/GroupsDashboard';
import TopicQuizSearch from './pages/TopicQuizSearch';
import GroupDetail from './pages/GroupDetail';
import PracticeQuizzes from './pages/PracticeQuizzes';
import UserManagement from './pages/admin/UserManagement';
import OrganizationManagement from './pages/admin/OrganizationManagement';
import Reports from './pages/admin/Reports';
import SystemSettings from './pages/admin/SystemSettings';
import StudentResults from './pages/StudentResults';
import QuizPreview from './pages/QuizPreview';
import EditQuiz from './pages/EditQuiz';
import QuizResults from './pages/QuizResults';
import ProtectedRoute from './components/ProtectedRoute';
import './index.css';

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      refetchOnWindowFocus: false,
      retry: 1,
    },
  },
});

function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <AuthProvider>
        <Router>
          <div className="min-h-screen bg-gray-50">
            <Routes>
              <Route path="/login" element={<Login />} />
              <Route path="/signup" element={<SignUp />} />
              <Route path="/forgot-password" element={<ForgotPassword />} />
              <Route path="/reset-password" element={<ResetPassword />} />
              <Route path="/" element={
                <ProtectedRoute>
                  <Dashboard />
                </ProtectedRoute>
              } />
              <Route path="/quizzes" element={
                <ProtectedRoute>
                  <QuizList />
                </ProtectedRoute>
              } />
              <Route path="/dashboard" element={
                <ProtectedRoute>
                  <Dashboard />
                </ProtectedRoute>
              } />
              <Route path="/create-quiz" element={
                <ProtectedRoute>
                  <CreateQuiz />
                </ProtectedRoute>
              } />
              <Route path="/my-quizzes" element={
                <ProtectedRoute>
                  <MyQuizzes />
                </ProtectedRoute>
              } />
              <Route path="/available-quizzes" element={
                <ProtectedRoute>
                  <AvailableQuizzes />
                </ProtectedRoute>
              } />
              <Route path="/take-quiz/:attemptId" element={
                <ProtectedRoute>
                  <TakeQuiz />
                </ProtectedRoute>
              } />
              <Route path="/quiz-result/:attemptId" element={
                <ProtectedRoute>
                  <QuizResult />
                </ProtectedRoute>
              } />
              <Route path="/my-results" element={
                <ProtectedRoute>
                  <MyResults />
                </ProtectedRoute>
              } />
              
              {/* Quiz Management Routes */}
              <Route path="/quiz-preview/:id" element={
                <ProtectedRoute>
                  <QuizPreview />
                </ProtectedRoute>
              } />
              <Route path="/edit-quiz/:id" element={
                <ProtectedRoute>
                  <EditQuiz />
                </ProtectedRoute>
              } />
              <Route path="/quiz-results/:id" element={
                <ProtectedRoute>
                  <QuizResults />
                </ProtectedRoute>
              } />
              
              {/* Admin Routes */}
              <Route path="/admin/users" element={
                <ProtectedRoute>
                  <UserManagement />
                </ProtectedRoute>
              } />
              <Route path="/admin/organizations" element={
                <ProtectedRoute>
                  <OrganizationManagement />
                </ProtectedRoute>
              } />
              <Route path="/admin/reports" element={
                <ProtectedRoute>
                  <Reports />
                </ProtectedRoute>
              } />
              <Route path="/admin/settings" element={
                <ProtectedRoute>
                  <SystemSettings />
                </ProtectedRoute>
              } />
              
              {/* Instructor Routes */}
              <Route path="/student-results" element={
                <ProtectedRoute>
                  <StudentResults />
                </ProtectedRoute>
              } />
              {/* Enhanced Group Routes */}
              <Route path="/groups" element={
                <ProtectedRoute>
                  <GroupsDashboard />
                </ProtectedRoute>
              } />
              <Route path="/groups/:id" element={
                <ProtectedRoute>
                  <GroupDetail />
                </ProtectedRoute>
              } />
              <Route path="/create-group" element={
                <ProtectedRoute>
                  <GroupManagement />
                </ProtectedRoute>
              } />
              <Route path="/topic-search" element={
                <ProtectedRoute>
                  <TopicQuizSearch />
                </ProtectedRoute>
              } />
              <Route path="/practice-quizzes" element={
                <ProtectedRoute>
                  <PracticeQuizzes />
                </ProtectedRoute>
              } />
            </Routes>
            <Toaster position="top-right" />
          </div>
        </Router>
      </AuthProvider>
    </QueryClientProvider>
  );
}

export default App;