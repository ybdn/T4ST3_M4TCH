import React from "react";
import {
  BrowserRouter as Router,
  Routes,
  Route,
  useNavigate,
} from "react-router-dom";
import HomePage from "./pages/HomePage";
import ExplorePage from "./pages/ExplorePage";
import MatchPage from "./pages/MatchPage";
import ListsPage from "./pages/ListsPage";
import ProfilePage from "./pages/ProfilePage";
import SocialPage from "./pages/SocialPage";
import LoginPage from "./pages/LoginPage";
import RegisterPage from "./pages/RegisterPage";
import PrivateRoute from "./components/PrivateRoute.tsx";
import ErrorBoundary from "./components/ErrorBoundary";
import UserFeedback, { useUserFeedback } from "./components/UserFeedback";
import { FeedbackProvider } from "./context/FeedbackContext";

function AppContent() {
  const navigate = useNavigate();
  const { messages, removeMessage } = useUserFeedback();

  const handleNavigate = (section: string) => {
    switch (section) {
      case "accueil":
        navigate("/");
        break;
      case "decouvrir":
        navigate("/explore");
        break;
      case "match":
        navigate("/match");
        break;
      case "listes":
        navigate("/lists");
        break;
      case "profil":
        navigate("/profile");
        break;
      case "social":
        navigate("/social");
        break;
      default:
        navigate("/");
        break;
    }
  };

  return (
    <div className="App">
      <UserFeedback messages={messages} onClose={removeMessage} />
      <Routes>
        <Route path="/login" element={<LoginPage />} />
        <Route path="/register" element={<RegisterPage />} />
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
          path="/profile"
          element={
            <PrivateRoute>
              <ProfilePage onNavigate={handleNavigate} />
            </PrivateRoute>
          }
        />
        <Route
          path="/social"
          element={
            <PrivateRoute>
              <SocialPage onNavigate={handleNavigate} />
            </PrivateRoute>
          }
        />
        <Route
          path="/"
          element={
            <PrivateRoute>
              <HomePage onNavigate={handleNavigate} />
            </PrivateRoute>
          }
        />
      </Routes>
    </div>
  );
}

const App: React.FC = () => (
  <ErrorBoundary>
    <FeedbackProvider>
      <Router>
        <AppContent />
      </Router>
    </FeedbackProvider>
  </ErrorBoundary>
);

export default App;
