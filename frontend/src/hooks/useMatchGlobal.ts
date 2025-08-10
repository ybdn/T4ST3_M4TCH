/**
 * Hooks pour le mode Match Global (version active)
 * Issue #25: Remplacer le stub de useMatchRecommendations
 */

import { useState, useCallback, useEffect } from "react";
import { matchApi } from "../services/matchApi";
import { useErrorHandler } from "./useErrorHandler";

// Types dérivés (on enrichit la réponse minimale pour la page Match)
export interface GlobalMatchRecommendation {
  external_id: string;
  title: string;
  content_type: string; // ex: FILMS / SERIES ... (placeholder tant que normalisation en cours)
  source: string; // ex: tmdb / spotify...
  poster_url?: string;
  description?: string;
  metadata?: {
    description?: string;
    poster_url?: string;
  } & Record<string, unknown>;
  compatibility_score?: number;
}

interface AsyncState<T> {
  data: T;
  loading: boolean;
  error: string | null;
}

interface UseMatchRecommendationsReturn {
  recommendations: GlobalMatchRecommendation[];
  loading: boolean;
  error: string | null;
  fetchRecommendations: (params?: {
    category?: string;
    count?: number;
  }) => Promise<void>;
  submitAction: (action?: "like" | "dislike" | "add") => Promise<boolean>;
  currentIndex: number;
  nextRecommendation: () => void;
  hasMore: boolean;
  refresh: () => Promise<void>;
}

export const useMatchRecommendations = (initialParams?: {
  category?: string;
  count?: number;
}): UseMatchRecommendationsReturn => {
  const [state, setState] = useState<AsyncState<GlobalMatchRecommendation[]>>({
    data: [],
    loading: false,
    error: null,
  });
  const [currentIndex, setCurrentIndex] = useState(0);
  const [lastParams, setLastParams] = useState(initialParams);
  const { handleError } = useErrorHandler();

  const mapRawToRecommendation = useCallback(
    (raw: unknown): GlobalMatchRecommendation => {
      const r = raw as Record<string, unknown>;
      // Le service minimal fournit: id, title, category, poster_url?, description?
      // On complète pour le composant consommateur.
      const contentType = String(
        (r.content_type as string) || (r.category as string) || "FILMS"
      ).toUpperCase();
      const extId = (r.external_id as string) || (r.id as string);
      if (!extId) {
        throw new Error("Recommandation sans identifiant valide (external_id / id manquant)");
      }
      return {
        external_id: extId,
        title: (r.title as string) || "Contenu sans titre",
        content_type: contentType,
        source: (r.source as string) || "tmdb", // défaut temporaire
        poster_url: r.poster_url as string | undefined,
        description: r.description as string | undefined,
        metadata: {
          description: r.description as string | undefined,
          poster_url: r.poster_url as string | undefined,
          ...((r.metadata as Record<string, unknown>) || {}),
        },
        // Score simulé si absent (UI attend un pourcentage)
        compatibility_score:
          typeof r.compatibility_score === "number"
            ? r.compatibility_score
            : Math.round(60 + Math.random() * 40),
      };
    },
    []
  );

  const fetchRecommendations = useCallback(
    async (params?: { category?: string; count?: number }) => {
      setState((prev) => ({ ...prev, loading: true, error: null }));
      setLastParams(params);
      try {
        const resp = await matchApi.getRecommendations(params);
        const mapped = (resp.results || []).map(mapRawToRecommendation);
        setState({ data: mapped, loading: false, error: null });
        setCurrentIndex(0);
      } catch (e) {
        const msg =
          e instanceof Error ? e.message : "Erreur lors du chargement";
        setState({ data: [], loading: false, error: msg });
        handleError(e, "fetchRecommendations");
      }
    },
    [handleError, mapRawToRecommendation]
  );

  const submitAction = useCallback(
    async (action: "like" | "dislike" | "add" = "like") => {
      const current = state.data[currentIndex];
      if (!current) return false;
      try {
        await matchApi.submitAction({
          external_id: current.external_id,
          source: current.source,
          category: current.content_type,
          action,
          title: current.title,
          metadata: current.metadata,
          description: current.description,
          poster_url: current.poster_url,
        });
        // Retirer l'élément courant et ajuster l'index si nécessaire
        setState((prev) => {
          const newData = prev.data.filter((_, i) => i !== currentIndex);
            // Ajuster currentIndex pour ne pas sortir des bornes
          setCurrentIndex((prevIdx) => {
            if (newData.length === 0) return 0;
            return Math.min(prevIdx, newData.length - 1);
          });
          return { ...prev, data: newData };
        });
        return true;
      } catch (e) {
        handleError(e, "submitAction");
        return false;
      }
    },
    [currentIndex, state.data, handleError]
  );

  const nextRecommendation = useCallback(() => {
    setCurrentIndex((prev) => Math.min(prev + 1, state.data.length - 1));
  }, [state.data.length]);

  // Préchargement quand on approche de la fin (réagit toujours à la longueur actuelle)
  useEffect(() => {
    if (
      state.data.length > 0 &&
      currentIndex >= state.data.length - 2 &&
      state.data.length < 200 // garde-fou pour éviter boucle si backend renvoie peu d'items
    ) {
      fetchRecommendations(lastParams);
    }
  }, [currentIndex, state.data.length, fetchRecommendations, lastParams]);

  const refresh = useCallback(async () => {
    await fetchRecommendations(lastParams);
  }, [fetchRecommendations, lastParams]);

  return {
    recommendations: state.data,
    loading: state.loading,
    error: state.error,
    fetchRecommendations,
    submitAction,
    currentIndex,
    nextRecommendation,
    hasMore: currentIndex < state.data.length - 1,
    refresh,
  };
};

// Actions (placeholder amélioré — conserve signature actuelle simple)
export const useMatchActions = () => ({
  submitAction: async () => true,
  loading: false,
  error: null,
});

// Stats (toujours mockées pour le moment)
export const useMatchStats = () => ({
  totalMatches: 0,
  successfulMatches: 0,
  successRate: 0,
  refreshStats: () => {},
});
