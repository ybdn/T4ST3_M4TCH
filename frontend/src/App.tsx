import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import Dashboard from './components/Dashboard';
import LoginPage from './pages/LoginPage';
import RegisterPage from './pages/RegisterPage';
import PrivateRoute from './components/PrivateRoute';

function App() {
  const handleNavigate = (section: string) => {
    console.log(`Navigation vers: ${section}`);
    // TODO: Implémenter la navigation entre les sections
  };

  return (
    <Router>
      <Routes>
        <Route path="/login" element={<LoginPage />} />
        <Route path="/register" element={<RegisterPage />} />
        <Route 
          path="/" 
          element={
            <PrivateRoute>
              <Dashboard onNavigate={handleNavigate} />
            </PrivateRoute>
          }
        />
      </Routes>
    </Router>
  );
}

export default App;
