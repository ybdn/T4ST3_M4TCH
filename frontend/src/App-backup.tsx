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
import SocialPage from './pages/SocialPage';
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
      case 'profil':
        navigate('/profile');
        break;
      case 'social':
        navigate('/social');
        break;
      default:
        break;
    }
  };

  return (
    <div className="App">
      <UserFeedback messages={messages} onRemove={removeMessage} />
      
      <Routes>
        <Route path="/login" element={<LoginPage />} />
        <Route path="/register" element={<RegisterPage />} />
        <Route path="/dashboard" element={<PrivateRoute><Dashboard /></PrivateRoute>} />
        <Route path="/lists" element={<PrivateRoute><ListsPage onNavigate={handleNavigate} /></PrivateRoute>} />
        <Route path="/lists/:listId" element={<PrivateRoute><ListsPage onNavigate={handleNavigate} /></PrivateRoute>} />
        <Route path="/explore" element={<PrivateRoute><ExplorePage onNavigate={handleNavigate} /></PrivateRoute>} />
        <Route path="/match" element={<PrivateRoute><MatchPage onNavigate={handleNavigate} /></PrivateRoute>} />
        <Route path="/profile" element={<PrivateRoute><ProfilePage onNavigate={handleNavigate} /></PrivateRoute>} />
        <Route path="/social" element={<PrivateRoute><SocialPage onNavigate={handleNavigate} /></PrivateRoute>} />
        <Route path="/quick-add" element={<PrivateRoute><QuickAddPage /></PrivateRoute>} />
        <Route path="/" element={<PrivateRoute><HomePage onNavigate={handleNavigate} /></PrivateRoute>} />
      </Routes>
    </div>
  );
}

export default function App() {
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