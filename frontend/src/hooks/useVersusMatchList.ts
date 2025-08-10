import { useState, useEffect, useCallback } from 'react';
import axios from 'axios';
import { API_BASE_URL } from '../config';
import { useErrorHandler } from './useErrorHandler';

interface VersusMatch {
  id: number;
  user1: number;
  user2: number;
  user1_username: string;
  user2_username: string;
  status: 'active' | 'finished' | 'cancelled';
  status_display: string;
  compatibility_score: number | null;
  category: string | null;
  category_display: string | null;
  other_user: {
    id: number;
    username: string;
  } | null;
  created_at: string;
  updated_at: string;
  finished_at: string | null;
}

interface VersusMatchListResponse {
  matches: VersusMatch[];
  total: number;
  status_filter: string;
  category_filter: string;
  limit: number;
}

interface UseVersusMatchListOptions {
  status?: 'active' | 'finished' | 'cancelled' | '';
  category?: string;
  limit?: number;
  autoRefresh?: boolean;
}

interface UseVersusMatchListReturn {
  matches: VersusMatch[];
  loading: boolean;
  error: string | null;
  total: number;
  refresh: () => Promise<void>;
  clearError: () => void;
}

export const useVersusMatchList = (options: UseVersusMatchListOptions = {}): UseVersusMatchListReturn => {
  const {
    status = '',
    category = '',
    limit = 20,
    autoRefresh = true
  } = options;

  const [matches, setMatches] = useState<VersusMatch[]>([]);
  const [loading, setLoading] = useState(true);
  const [total, setTotal] = useState(0);
  const { error, handleError, clearError } = useErrorHandler();

  const fetchMatches = useCallback(async () => {
    try {
      setLoading(true);
      clearError();

      // Récupérer le token d'authentification depuis le localStorage
      const token = localStorage.getItem('authToken') || localStorage.getItem('access_token');
      if (!token) {
        throw new Error('Token d\'authentification manquant');
      }

      // Construire les paramètres de requête
      const params = new URLSearchParams();
      if (status) params.append('status', status);
      if (category) params.append('category', category);
      if (limit) params.append('limit', limit.toString());

      const response = await axios.get<VersusMatchListResponse>(
        `${API_BASE_URL}/versus-matches/?${params.toString()}`,
        {
          headers: {
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json',
          },
        }
      );

      setMatches(response.data.matches);
      setTotal(response.data.total);
    } catch (err) {
      handleError(err, 'useVersusMatchList.fetchMatches');
      // En cas d'erreur, garder les données existantes si possible
      // mais afficher l'erreur à l'utilisateur
    } finally {
      setLoading(false);
    }
  }, [status, category, limit, handleError, clearError]);

  const refresh = useCallback(async () => {
    await fetchMatches();
  }, [fetchMatches]);

  // Charger les données au montage du composant et quand les options changent
  useEffect(() => {
    if (autoRefresh) {
      fetchMatches();
    }
  }, [fetchMatches, autoRefresh]);

  return {
    matches,
    loading,
    error: error?.message || null,
    total,
    refresh,
    clearError
  };
};