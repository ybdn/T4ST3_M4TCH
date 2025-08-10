/**
 * Types et interfaces pour le système Match Global + Social
 */

// Énums de base
export enum ContentType {
  FILMS = 'FILMS',
  SERIES = 'SERIES',
  MUSIQUE = 'MUSIQUE',
  LIVRES = 'LIVRES'
}

export enum ContentSource {
  TMDB = 'tmdb',
  SPOTIFY = 'spotify',
  GOOGLE_BOOKS = 'google_books',
  OPENLIBRARY = 'openlibrary'
}

export enum UserAction {
  LIKED = 'liked',
  DISLIKED = 'disliked',
  ADDED = 'added',
  SKIPPED = 'skipped'
}

export enum FriendshipStatus {
  PENDING = 'pending',
  ACCEPTED = 'accepted',
  BLOCKED = 'blocked',
  DECLINED = 'declined'
}

export enum MatchStatus {
  ACTIVE = 'active',
  COMPLETED = 'completed',
  ABANDONED = 'abandoned'
}

export enum MatchType {
  TASTE_COMPATIBILITY = 'taste_compatibility',
  VERSUS_CHALLENGE = 'versus_challenge',
  DISCOVERY_SYNC = 'discovery_sync'
}

export enum VersusChoice {
  LIKED = 'liked',
  DISLIKED = 'disliked',
  SKIPPED = 'skipped'
}

// Interfaces pour le contenu
export interface ContentMetadata {
  // Métadonnées communes
  poster_url?: string;
  backdrop_url?: string;
  description?: string;
  
  // Films/Séries (TMDB)
  release_date?: string;
  first_air_date?: string;
  vote_average?: number;
  genre_ids?: number[];
  original_language?: string;
  popularity?: number;
  origin_country?: string[];
  
  // Musique (Spotify)
  artist?: string;
  album?: string;
  duration_ms?: number;
  genres?: string[];
  
  // Livres (Google Books)
  authors?: string[];
  published_date?: string;
  page_count?: number;
  categories?: string[];
  language?: string;
  average_rating?: number;
}

export interface MatchContent {
  external_id: string;
  content_type: ContentType;
  source: ContentSource;
  title: string;
  description?: string;
  poster_url?: string;
  metadata: ContentMetadata;
  compatibility_score?: number;
}

export interface MatchRecommendation extends MatchContent {
  compatibility_score: number;
  reasons?: string[];
}

// Interfaces pour les préférences utilisateur
export interface UserPreference {
  id: number;
  external_id: string;
  content_type: ContentType;
  source: ContentSource;
  action: UserAction;
  title: string;
  metadata: ContentMetadata;
  created_at: string;
}

// Interfaces pour le profil social
export interface UserProfile {
  user_id: number;
  username: string;
  gamertag: string;
  display_name: string;
  bio: string;
  avatar_url: string;
  is_public: boolean;
  stats: UserStats;
  created_at: string;
}

export interface UserStats {
  total_matches: number;
  successful_matches: number;
  friends_count: number;
  pending_requests: number;
}

export interface UpdateProfileData {
  display_name?: string;
  bio?: string;
  avatar_url?: string;
  is_public?: boolean;
}

// Interfaces pour le système d'amitié
export interface FriendUser {
  user_id: number;
  username: string;
  gamertag: string;
  display_name: string;
  avatar_url: string;
}

export interface Friendship {
  friendship_id: number;
  requester: FriendUser;
  addressee: FriendUser;
  status: FriendshipStatus;
  created_at: string;
}

export interface FriendRequest {
  friendship_id: number;
  requester: FriendUser;
  created_at: string;
}

export interface FriendRequestResponse {
  success: boolean;
  friendship_id: number;
  action: 'accept' | 'decline';
  status: string;
}

// Interfaces pour les matchs versus
export interface VersusMatch {
  match_id: number;
  opponent: FriendUser;
  status: MatchStatus;
  current_round: number;
  total_rounds: number;
  scores: {
    your_score: number;
    opponent_score: number;
  };
  compatibility_score?: number;
  last_activity: string;
  is_your_turn: boolean;
}

export interface VersusSession {
  session_id: number;
  round_number: number;
  content: {
    external_id: string;
    type: ContentType;
    source: ContentSource;
    title: string;
    metadata: ContentMetadata;
  };
  your_choice?: VersusChoice;
  is_completed: boolean;
  is_match?: boolean;
  match_progress: {
    current_round: number;
    total_rounds: number;
    scores: {
      your_score: number;
      opponent_score: number;
    };
  };
}

export interface VersusMatchResults {
  match_id: number;
  users: {
    user1: {
      username: string;
      score: number;
    };
    user2: {
      username: string;
      score: number;
    };
  };
  compatibility_score: number;
  status: MatchStatus;
  total_rounds: number;
  completed_rounds: number;
  sessions: VersusSessionResult[];
}

export interface VersusSessionResult {
  round_number: number;
  content: {
    title: string;
    type: ContentType;
    poster_url?: string;
  };
  choices: {
    user1?: VersusChoice;
    user2?: VersusChoice;
  };
  is_match: boolean;
  is_completed: boolean;
}

// Interfaces pour les réponses API
export interface MatchRecommendationsResponse {
  results: MatchRecommendation[];
  count: number;
  category?: ContentType;
}

export interface SubmitMatchActionResponse {
  success: boolean;
  action: UserAction;
  preference_id: number;
  list_item_id?: number;
  list_id?: number;
}

export interface AddFriendResponse {
  success: boolean;
  friendship_id: number;
  target_user: FriendUser;
  status: string;
}

export interface FriendsListResponse {
  friends: FriendUser[];
  count: number;
}

export interface FriendRequestsResponse {
  requests: FriendRequest[];
  count: number;
}

export interface CreateVersusMatchResponse {
  success: boolean;
  match_id: number;
  match_type: MatchType;
  total_rounds: number;
  opponent: FriendUser;
}

export interface VersusMatchesResponse {
  matches: VersusMatch[];
  count: number;
}

export interface SubmitVersusChoiceResponse {
  success: boolean;
  session_completed: boolean;
  match_completed: boolean;
  is_match?: boolean;
  scores: {
    user1: number;
    user2: number;
  };
}

// Types pour les requêtes API
export interface MatchActionRequest {
  external_id: string;
  source: ContentSource;
  content_type: ContentType;
  action: UserAction;
  title: string;
  metadata?: ContentMetadata;
}

export interface AddFriendRequest {
  gamertag: string;
}

export interface RespondFriendRequest {
  action: 'accept' | 'decline';
}

export interface CreateVersusMatchRequest {
  target_gamertag: string;
  rounds?: number;
}

export interface SubmitVersusChoiceRequest {
  choice: VersusChoice;
}

// Types pour les erreurs
export interface ApiError {
  error: string;
  code?: string;
  details?: Record<string, any>;
}

// Types pour les paramètres de requête
export interface MatchRecommendationsParams {
  category?: ContentType;
  count?: number;
}