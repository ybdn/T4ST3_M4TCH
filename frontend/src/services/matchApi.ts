// Service Match minimal (features sociales & versus temporairement désactivées)
import { API_BASE_URL } from "../config";

// Types locaux minimalistes pour limiter la surface pendant refactor
export interface MatchRecommendationsParams {
  category?: string;
  count?: number;
}
export interface MatchRecommendation {
  id: string;
  title: string;
  category: string;
  poster_url?: string;
  description?: string;
}
export interface MatchRecommendationsResponse {
  results: MatchRecommendation[];
}
export type MatchUserAction = "like" | "dislike" | "add";
export interface MatchActionRequest {
  external_id: string;
  source: string;
  category: string;
  action: MatchUserAction;
  title?: string;
  metadata?: { description?: string; poster_url?: string };
  description?: string;
  poster_url?: string;
}
export interface SubmitMatchActionResponse {
  success: boolean;
}

const getAuthHeaders = (): HeadersInit => {
  const token = localStorage.getItem("access_token");
  return {
    "Content-Type": "application/json",
    ...(token && { Authorization: `Bearer ${token}` }),
  };
};

const handleApiError = async (response: Response) => {
  if (!response.ok) {
    const data = await response
      .json()
      .catch(() => ({ error: "Erreur inconnue" }));
    throw new Error(data.error || `Erreur ${response.status}`);
  }
  return response.json();
};

export const matchApi = {
  getRecommendations: async (
    params?: MatchRecommendationsParams
  ): Promise<MatchRecommendationsResponse> => {
    const qs = new URLSearchParams();
    if (params?.category) qs.append("category", params.category);
    if (params?.count) qs.append("count", String(params.count));
    const resp = await fetch(
      `${API_BASE_URL}/match/recommendations/?${qs.toString()}`,
      { headers: getAuthHeaders() }
    );
    return handleApiError(resp);
  },
  submitAction: async (
    actionData: MatchActionRequest
  ): Promise<SubmitMatchActionResponse> => {
    const payload = {
      ...actionData,
      description: actionData.description ?? actionData.metadata?.description,
      poster_url: actionData.poster_url ?? actionData.metadata?.poster_url,
    };
    const resp = await fetch(`${API_BASE_URL}/match/action/`, {
      method: "POST",
      headers: getAuthHeaders(),
      body: JSON.stringify(payload),
    });
    return handleApiError(resp);
  },
};

export default matchApi;
