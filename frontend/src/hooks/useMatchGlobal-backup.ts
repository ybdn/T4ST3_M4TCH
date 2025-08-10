/**
 * Hooks pour le mode Match Global - Sauvegarde
 */

import { useState, useCallback } from 'react';
import type { 
  MatchRecommendation, 
  MatchRecommendationsParams,
  UserAction,
  ContentType,
  AsyncState
} from '../types';
import { matchApiService } from '../services/matchApi';
import { useErrorHandler } from './useErrorHandler';

interface UseMatchRecommendationsReturn {
  recommendations: MatchRecommendation[];
  loading: boolean;
  error: string | null;
  fetchRecommendations: (params?: MatchRecommendationsParams) => Promise<void>;
  submitAction: (recommendation: MatchRecommendation, action: UserAction) => Promise<boolean>;
  currentIndex: number;
  nextRecommendation: () => void;
  hasMore: boolean;
  refresh: () => Promise<void>;
}

export const useMatchRecommendations = (
  initialParams?: MatchRecommendationsParams
): UseMatchRecommendationsReturn => {
  const [state, setState] = useState<AsyncState<MatchRecommendation[]>>({
    data: [],
    loading: false,
    error: null
  });

  const [currentIndex, setCurrentIndex] = useState(0);
  const [lastParams, setLastParams] = useState(initialParams);
  const { handleError } = useErrorHandler();

  const fetchRecommendations = useCallback(async (params?: MatchRecommendationsParams) => {
    setState(prev => ({ ...prev, loading: true, error: null }));
    setLastParams(params);

    try {
      const response = await matchApiService.match.getRecommendations(params);
      setState({
        data: response.results,
        loading: false,
        error: null
      });
      setCurrentIndex(0);
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : 'Erreur lors du chargement des recommandations';
      setState({
        data: [],
        loading: false,
        error: errorMessage
      });
      handleError(error);
    }
  }, [handleError]);

  const submitAction = useCallback(async (
    recommendation: MatchRecommendation, 
    action: UserAction
  ): Promise<boolean> => {
    try {
      // Mock implementation for now
      console.log('Action submitted:', { recommendation, action });

      // Retirer la recommandation de la liste après action
      setState(prev => ({
        ...prev,
        data: prev.data?.filter(r => r.external_id !== recommendation.external_id) || []
      }));

      return true;
    } catch (error) {
      handleError(error);
      return false;
    }
  }, [handleError]);

  const nextRecommendation = useCallback(() => {
    setCurrentIndex(prev => {
      const nextIndex = prev + 1;
      // Si on atteint la fin, recharger automatiquement plus de recommandations
      if (nextIndex >= (state.data?.length || 0) - 2 && state.data && state.data.length > 0) {
        fetchRecommendations(lastParams);
      }
      return nextIndex;
    });
  }, [state.data, fetchRecommendations, lastParams]);

  const refresh = useCallback(() => {
    return fetchRecommendations(lastParams);
  }, [fetchRecommendations, lastParams]);

  return {
    recommendations: state.data || [],
    loading: state.loading,
    error: state.error,
    fetchRecommendations,
    submitAction,
    currentIndex,
    nextRecommendation,
    hasMore: currentIndex < (state.data?.length || 0) - 1,
    refresh
  };
};

interface UseMatchActionsReturn {
  submitAction: (
    externalId: string,
    source: string,
    contentType: ContentType,
    action: UserAction,
    title: string,
    metadata?: any
  ) => Promise<boolean>;
  loading: boolean;
  error: string | null;
}

export const useMatchActions = (): UseMatchActionsReturn => {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const { handleError } = useErrorHandler();

  const submitAction = useCallback(async (
    externalId: string,
    source: string,
    contentType: ContentType,
    action: UserAction,
    title: string,
    metadata?: any
  ): Promise<boolean> => {
    setLoading(true);
    setError(null);

    try {
      // Mock implementation
      console.log('Match action:', { externalId, source, contentType, action, title, metadata });
      
      setLoading(false);
      return true;
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : 'Erreur lors de l\'action';
      setError(errorMessage);
      setLoading(false);
      handleError(error);
      return false;
    }
  }, [handleError]);

  return {
    submitAction,
    loading,
    error
  };
};

// Hook pour gérer les statistiques des matchs
interface UseMatchStatsReturn {
  totalMatches: number;
  successfulMatches: number;
  successRate: number;
  refreshStats: () => void;
}

export const useMatchStats = (): UseMatchStatsReturn => {
  const [stats, setStats] = useState({
    totalMatches: 0,
    successfulMatches: 0
  });

  // Ce hook peut être connecté au profil utilisateur pour récupérer les stats
  const refreshStats = useCallback(() => {
    // TODO: Implémenter la récupération des stats depuis le profil
    // Pour l'instant, on utilise le localStorage ou on fait appel au profil social
  }, []);

  const successRate = stats.totalMatches > 0 ? (stats.successfulMatches / stats.totalMatches) * 100 : 0;

  return {
    totalMatches: stats.totalMatches,
    successfulMatches: stats.successfulMatches,
    successRate,
    refreshStats
  };
};