import React, { createContext, useState, useContext, useEffect } from "react";
import type { ReactNode } from "react";
import axios from "axios";
import { API_BASE_URL } from "../config";

const API_URL = API_BASE_URL;

// Axios instance for authenticated requests
const axiosInstance = axios.create({
  baseURL: API_URL,
});

axiosInstance.interceptors.request.use((config) => {
  const token = localStorage.getItem("access_token");
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
  register: (
    username: string,
    email: string,
    password: string
  ) => Promise<void>;
  logout: () => void;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error("useAuth must be used within an AuthProvider");
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
    const checkLoggedIn = async (): Promise<void> => {
      const token = localStorage.getItem("access_token");
      if (token) {
        try {
          const response = await axiosInstance.get("/users/me/");
          setUser(response.data);
          setIsAuthenticated(true);
        } catch {
          // Tentative de rafraîchissement si un refresh_token est présent
          const refreshToken = localStorage.getItem("refresh_token");
          if (refreshToken) {
            try {
              const refreshResponse = await axios.post(
                `${API_URL}/auth/token/refresh/`,
                {
                  refresh: refreshToken,
                }
              );
              const newAccess = refreshResponse.data?.access;
              if (newAccess) {
                localStorage.setItem("access_token", newAccess);
                // Réessayer l'appel /users/me/ avec le nouveau token
                const retryResponse = await axiosInstance.get("/users/me/");
                setUser(retryResponse.data);
                setIsAuthenticated(true);
              } else {
                localStorage.removeItem("access_token");
                localStorage.removeItem("refresh_token");
              }
            } catch {
              // Échec du refresh: nettoyer les tokens
              localStorage.removeItem("access_token");
              localStorage.removeItem("refresh_token");
            }
          } else {
            // Pas de refresh token, nettoyer silencieusement
            localStorage.removeItem("access_token");
            localStorage.removeItem("refresh_token");
          }
        }
      }
      setLoading(false);
    };

    checkLoggedIn();
  }, []);

  const login = async (username: string, password: string): Promise<void> => {
    const response = await axios.post(`${API_URL}/auth/token/`, {
      username,
      password,
    });
    localStorage.setItem("access_token", response.data.access);
    localStorage.setItem("refresh_token", response.data.refresh);

    const userResponse = await axiosInstance.get("/users/me/");
    setUser(userResponse.data);
    setIsAuthenticated(true);
  };

  const register = async (
    username: string,
    email: string,
    password: string
  ): Promise<void> => {
    await axios.post(`${API_URL}/auth/register/`, {
      username,
      email,
      password,
      password2: password,
    });
    await login(username, password);
  };

  const logout = () => {
    localStorage.removeItem("access_token");
    localStorage.removeItem("refresh_token");
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
