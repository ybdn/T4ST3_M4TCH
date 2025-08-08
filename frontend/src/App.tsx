import React from 'react';
import { BrowserRouter as Router, Routes, Route, useNavigate } from 'react-router-dom';
import Dashboard from './components/Dashboard';
import LoginPage from './pages/LoginPage';
import RegisterPage from './pages/RegisterPage';
import ListsPage from './pages/ListsPage';
import HomePage from './pages/HomePage';
import ExplorePage from './pages/ExplorePage';
import MatchPage from './pages/MatchPage';
import QuickAddPage from './pages/QuickAddPage';
import ProfilePage from './pages/ProfilePage';
import PrivateRoute from './components/PrivateRoute.tsx';
import ErrorBoundary from './components/ErrorBoundary';
import UserFeedback, { useUserFeedback } from './components/UserFeedback';
import { FeedbackProvider } from './context/FeedbackContext';

// Composant wrapper pour gérer la navigation
function AppContent() {
  const navigate = useNavigate();
  const { messages, removeMessage } = useUserFeedback();

  type NavigateParams = { listId?: number } | undefined;
  const handleNavigate = (section: string, params?: NavigateParams) => {
    switch (section) {
      case 'accueil':
        navigate('/');
        break;
      case 'decouvrir':
        navigate('/explore');
        break;
      case 'match':
        navigate('/match');
        break;
      case 'listes':
        navigate('/lists');
        break;
      case 'ajout':
        navigate('/quick-add');
        break;
      case 'profil':
        navigate('/profile');
        break;
      case 'dashboard': {
        const listId = params?.listId ?? 1;
        navigate(`/dashboard/${listId}`);
        break;
      }
      default:
        console.log(`Navigation vers: ${section}`, params);
    }
  };

  return (
    <>
      <Routes>
        <Route path="/login" element={<LoginPage />} />
        <Route path="/register" element={<RegisterPage />} />
        <Route 
          path="/" 
          element={
            <PrivateRoute>
              <HomePage onNavigate={handleNavigate} />
            </PrivateRoute>
          }
        />
        <Route 
          path="/explore" 
          element={
            <PrivateRoute>
              <ExplorePage onNavigate={handleNavigate} />
            </PrivateRoute>
          }
        />
        <Route 
          path="/match" 
          element={
            <PrivateRoute>
              <MatchPage onNavigate={handleNavigate} />
            </PrivateRoute>
          }
        />
        <Route 
          path="/lists" 
          element={
            <PrivateRoute>
              <ListsPage onNavigate={handleNavigate} />
            </PrivateRoute>
          }
        />
        <Route 
          path="/quick-add" 
          element={
            <PrivateRoute>
              <QuickAddPage onNavigate={handleNavigate} />
            </PrivateRoute>
          }
        />
        <Route 
          path="/profile" 
          element={
            <PrivateRoute>
              <ProfilePage onNavigate={handleNavigate} />
            </PrivateRoute>
          }
        />
        <Route 
          path="/dashboard/:listId?" 
          element={
            <PrivateRoute>
              <Dashboard onNavigate={handleNavigate} />
            </PrivateRoute>
          }
        />
      </Routes>
      
      {/* Système de feedback global */}
      {messages.map((message) => (
        <UserFeedback
          key={message.id}
          message={message}
          onClose={removeMessage}
        />
      ))}
    </>
  );
}

function App() {
  return (
    <ErrorBoundary>
      <FeedbackProvider>
        <Router>
          <AppContent />
        </Router>
      </FeedbackProvider>
    </ErrorBoundary>
  );
}

export default App;
