import React from 'react';
import { Navigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext.tsx';

interface PrivateRouteProps {
  children: React.ReactElement;
}

const PrivateRoute: React.FC<PrivateRouteProps> = ({ children }) => {
  const { isAuthenticated } = useAuth();

  if (!isAuthenticated) {
    // Si l'utilisateur n'est pas authentifié, on le redirige vers la page de connexion
    return <Navigate to="/login" />;
  }

  return children;
};

export default PrivateRoute;
