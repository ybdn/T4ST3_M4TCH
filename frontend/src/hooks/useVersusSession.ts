import { useState, useEffect, useCallback } from 'react';
import axios from 'axios';
import { API_BASE_URL } from '../config';
import { useErrorHandler } from './useErrorHandler';

const API_URL = API_BASE_URL;

// Create axios instance with auth
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

interface VersusSession {
  id: number;
  status: 'active' | 'completed' | 'paused';
  current_round: number;
  total_rounds: number;
  progress_percentage: number;
  is_finished: boolean;
  score: number;
  started_at: string;
}

interface VersusRound {
  id: number;
  round_number: number;
  item_title: string;
  item_description: string;
  item_category: string;
  item_poster_url?: string;
  compatibility_score: number;
  is_answered: boolean;
}

interface SessionSummary {
  total_score: number;
  likes: number;
  dislikes: number;
  skips: number;
  completion_time: string;
}

interface VersusSessionState {
  session: VersusSession | null;
  currentRound: VersusRound | null;
  summary: SessionSummary | null;
  loading: boolean;
  submittingChoice: boolean;
}

export const useVersusSession = () => {
  const { handleError, clearError } = useErrorHandler();
  const [state, setState] = useState<VersusSessionState>({
    session: null,
    currentRound: null,
    summary: null,
    loading: false,
    submittingChoice: false,
  });

  // Récupère ou crée une session versus
  const fetchSession = useCallback(async () => {
    setState(prev => ({ ...prev, loading: true }));
    clearError();

    try {
      const response = await axiosInstance.get('/versus/session/');
      const data = response.data;
      
      setState(prev => ({
        ...prev,
        session: data.session,
        currentRound: data.current_round,
        summary: null, // Reset summary when fetching new session
        loading: false,
      }));

      return data;
    } catch (error) {
      handleError(error, 'fetchSession');
      setState(prev => ({ ...prev, loading: false }));
      return null;
    }
  }, [handleError, clearError]);

  // Crée une nouvelle session
  const createSession = useCallback(async (totalRounds: number = 10) => {
    setState(prev => ({ ...prev, loading: true }));
    clearError();

    try {
      const response = await axiosInstance.post('/versus/session/', {
        total_rounds: totalRounds
      });
      
      const sessionData = response.data.session;
      setState(prev => ({
        ...prev,
        session: sessionData,
        currentRound: null,
        summary: null,
        loading: false,
      }));

      // Fetch the first round
      await fetchSession();

      return sessionData;
    } catch (error) {
      handleError(error, 'createSession');
      setState(prev => ({ ...prev, loading: false }));
      return null;
    }
  }, [handleError, clearError, fetchSession]);

  // Soumet un choix pour le round actuel
  const submitChoice = useCallback(async (choice: 'like' | 'dislike' | 'skip') => {
    if (!state.currentRound) {
      handleError('Aucun round actuel disponible', 'submitChoice');
      return null;
    }

    if (state.session?.is_finished) {
      handleError('Cette session est déjà terminée', 'submitChoice');
      return null;
    }

    setState(prev => ({ ...prev, submittingChoice: true }));
    clearError();

    try {
      const response = await axiosInstance.post(
        `/versus/round/${state.currentRound.id}/choice/`,
        { choice }
      );

      const data = response.data;
      
      setState(prev => ({
        ...prev,
        session: data.session,
        summary: data.summary || null,
        submittingChoice: false,
      }));

      // Si la session n'est pas terminée, récupérer le prochain round
      if (!data.session.is_finished) {
        await fetchSession();
      } else {
        // Session terminée, pas de round suivant
        setState(prev => ({
          ...prev,
          currentRound: null,
        }));
      }

      return data;
    } catch (error) {
      handleError(error, 'submitChoice');
      setState(prev => ({ ...prev, submittingChoice: false }));
      return null;
    }
  }, [state.currentRound, state.session?.is_finished, handleError, clearError, fetchSession]);

  // Récupère les détails d'un round spécifique
  const fetchRound = useCallback(async (roundId: number) => {
    try {
      const response = await axiosInstance.get(`/versus/round/${roundId}/`);
      return response.data;
    } catch (error) {
      handleError(error, 'fetchRound');
      return null;
    }
  }, [handleError]);

  // Refetch round en cas de désynchronisation
  const refetchRound = useCallback(async () => {
    if (!state.session) return null;
    
    setState(prev => ({ ...prev, loading: true }));
    
    try {
      await fetchSession();
      return true;
    } catch (error) {
      handleError(error, 'refetchRound');
      setState(prev => ({ ...prev, loading: false }));
      return false;
    }
  }, [state.session, fetchSession, handleError]);

  // Initialise la session au chargement du hook
  useEffect(() => {
    fetchSession();
  }, [fetchSession]);

  return {
    // État
    session: state.session,
    currentRound: state.currentRound,
    summary: state.summary,
    loading: state.loading,
    submittingChoice: state.submittingChoice,
    
    // Actions
    fetchSession,
    createSession,
    submitChoice,
    fetchRound,
    refetchRound,
    
    // Utilitaires
    isSessionFinished: state.session?.is_finished ?? false,
    canSubmitChoice: !state.submittingChoice && !state.session?.is_finished && state.currentRound !== null,
    progressPercentage: state.session?.progress_percentage ?? 0,
    currentScore: state.session?.score ?? 0,
  };
};