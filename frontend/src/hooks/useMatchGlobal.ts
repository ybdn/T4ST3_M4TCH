/**
 * Hooks pour le mode Match Global
 */

import { useState, useCallback } from "react";

// Hook MATCH simplifié neutralisé (refactor en cours)
export const useMatchRecommendations = () => {
  const [recommendations] = useState<any[]>([]);
  const [loading] = useState(false);
  const [error] = useState<string | null>(null);
  const fetchRecommendations = useCallback(async () => {}, []);
  const submitAction = useCallback(async () => true, []);
  const nextRecommendation = useCallback(() => {}, []);
  const refresh = useCallback(async () => {}, []);
  return {
    recommendations,
    loading,
    error,
    fetchRecommendations,
    submitAction,
    currentIndex: 0,
    nextRecommendation,
    hasMore: false,
    refresh,
  };
};

export const useMatchActions = () => ({
  submitAction: async () => true,
  loading: false,
  error: null,
});
export const useMatchStats = () => ({
  totalMatches: 0,
  successfulMatches: 0,
  successRate: 0,
  refreshStats: () => {},
});
