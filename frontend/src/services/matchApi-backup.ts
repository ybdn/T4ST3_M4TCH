/**
 * Service API pour le système Match Global + Social - Version de sauvegarde
 */

import type { 
  MatchRecommendationsResponse, 
  MatchRecommendationsParams,
  SubmitMatchActionResponse,
  MatchActionRequest,
  UserProfile,
  UpdateProfileData,
  AddFriendResponse,
  AddFriendRequest,
  FriendsListResponse,
  FriendRequestsResponse,
  FriendRequestResponse,
  RespondFriendRequest,
  CreateVersusMatchResponse,
  CreateVersusMatchRequest,
  VersusMatchesResponse,
  VersusSession,
  SubmitVersusChoiceResponse,
  SubmitVersusChoiceRequest,
  VersusMatchResults
} from '../types';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api';

// Utilitaire pour obtenir les headers avec authentification
const getAuthHeaders = (): HeadersInit => {
  const token = localStorage.getItem('access_token');
  return {
    'Content-Type': 'application/json',
    ...(token && { 'Authorization': `Bearer ${token}` })
  };
};

// Utilitaire pour gérer les erreurs API
const handleApiError = async (response: Response) => {
  if (!response.ok) {
    const errorData = await response.json().catch(() => ({ error: 'Une erreur est survenue' }));
    throw new Error(errorData.error || `Erreur ${response.status}`);
  }
  return response.json();
};

// ==========================================
// MATCH GLOBAL API
// ==========================================

export const matchApi = {
  // Récupérer les recommandations
  getRecommendations: async (params?: MatchRecommendationsParams): Promise<MatchRecommendationsResponse> => {
    const queryParams = new URLSearchParams();
    if (params?.category) queryParams.append('category', params.category);
    if (params?.count) queryParams.append('count', params.count.toString());

    const response = await fetch(`${API_BASE_URL}/match/recommendations/?${queryParams}`, {
      method: 'GET',
      headers: getAuthHeaders()
    });
    
    return handleApiError(response);
  },

  // Soumettre une action (like, dislike, add)
  submitAction: async (actionData: MatchActionRequest): Promise<SubmitMatchActionResponse> => {
    const response = await fetch(`${API_BASE_URL}/match/action/`, {
      method: 'POST',
      headers: getAuthHeaders(),
      body: JSON.stringify(actionData)
    });

    return handleApiError(response);
  }
};

// ==========================================
// SOCIAL PROFILE API
// ==========================================

export const socialApi = {
  // Récupérer le profil social
  getProfile: async (): Promise<UserProfile> => {
    const response = await fetch(`${API_BASE_URL}/social/profile/`, {
      method: 'GET',
      headers: getAuthHeaders()
    });

    return handleApiError(response);
  },

  // Mettre à jour le profil social
  updateProfile: async (profileData: UpdateProfileData): Promise<UserProfile> => {
    const response = await fetch(`${API_BASE_URL}/social/profile/update/`, {
      method: 'POST',
      headers: getAuthHeaders(),
      body: JSON.stringify(profileData)
    });

    return handleApiError(response);
  }
};

// ==========================================
// FRIENDS API
// ==========================================

export const friendsApi = {
  // Ajouter un ami par gamertag
  addFriend: async (friendData: AddFriendRequest): Promise<AddFriendResponse> => {
    const response = await fetch(`${API_BASE_URL}/social/friends/add/`, {
      method: 'POST',
      headers: getAuthHeaders(),
      body: JSON.stringify(friendData)
    });

    return handleApiError(response);
  },

  // Récupérer la liste des amis
  getFriends: async (): Promise<FriendsListResponse> => {
    const response = await fetch(`${API_BASE_URL}/social/friends/`, {
      method: 'GET',
      headers: getAuthHeaders()
    });

    return handleApiError(response);
  },

  // Récupérer les demandes d'amitié
  getFriendRequests: async (): Promise<FriendRequestsResponse> => {
    const response = await fetch(`${API_BASE_URL}/social/friends/requests/`, {
      method: 'GET',
      headers: getAuthHeaders()
    });

    return handleApiError(response);
  },

  // Répondre à une demande d'amitié
  respondToFriendRequest: async (
    friendshipId: number, 
    responseData: RespondFriendRequest
  ): Promise<FriendRequestResponse> => {
    const response = await fetch(`${API_BASE_URL}/social/friends/requests/${friendshipId}/respond/`, {
      method: 'POST',
      headers: getAuthHeaders(),
      body: JSON.stringify(responseData)
    });

    return handleApiError(response);
  }
};

// Export par défaut avec toutes les APIs (sans versus pour test)
export const matchApiService = {
  match: matchApi,
  social: socialApi,
  friends: friendsApi
};

export default matchApiService;