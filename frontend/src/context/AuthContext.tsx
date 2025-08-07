import React, { createContext, useState, useContext, useEffect, ReactNode } from 'react';
import axios from 'axios';

const API_URL = 'http://localhost:8000/api';

// Axios instance for authenticated requests
const axiosInstance = axios.create({
  baseURL: API_URL,
});

axiosInstance.interceptors.request.use((config) => {
  const token = localStorage.getItem('access_token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

interface User {
  id: number;
  username: string;
  email: string;
}

interface AuthContextType {
  isAuthenticated: boolean;
  user: User | null;
  login: (username: string, password: string) => Promise<void>;
  register: (username: string, email: string, password: string) => Promise<void>;
  logout: () => void;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};

interface AuthProviderProps {
  children: ReactNode;
}

export const AuthProvider: React.FC<AuthProviderProps> = ({ children }) => {
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const checkLoggedIn = async () => {
      const token = localStorage.getItem('access_token');
      if (token) {
        try {
          const response = await axiosInstance.get('/users/me/');
          setUser(response.data);
          setIsAuthenticated(true);
        } catch (error) {
          console.error('Token validation failed', error);
          localStorage.removeItem('access_token');
          localStorage.removeItem('refresh_token');
        }
      }
      setLoading(false);
    };

    checkLoggedIn();
  }, []);

  const login = async (username, password) => {
    const response = await axios.post(`${API_URL}/auth/token/`, {
      username,
      password,
    });
    localStorage.setItem('access_token', response.data.access);
    localStorage.setItem('refresh_token', response.data.refresh);
    
    const userResponse = await axiosInstance.get('/users/me/');
    setUser(userResponse.data);
    setIsAuthenticated(true);
  };

  const register = async (username, email, password) => {
    await axios.post(`${API_URL}/auth/register/`, {
      username,
      email,
      password,
      password2: password,
    });
    await login(username, password);
  };

  const logout = () => {
    localStorage.removeItem('access_token');
    localStorage.removeItem('refresh_token');
    setIsAuthenticated(false);
    setUser(null);
  };

  const authContextValue = {
    isAuthenticated,
    user,
    login,
    register,
    logout,
  };

  if (loading) {
    return <div>Loading...</div>; // Ou un spinner de chargement
  }

  return (
    <AuthContext.Provider value={authContextValue}>
      {children}
    </AuthContext.Provider>
  );
};
