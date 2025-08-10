/**
 * Export de tous les types TypeScript
 */

// Types existants (si il y en a)
export * from "./match";

// Types génériques pour l'API
export interface ApiResponse<T> {
  data: T;
  message?: string;
  success?: boolean;
}

export interface PaginatedResponse<T> {
  results: T[];
  count: number;
  next?: string;
  previous?: string;
}

export interface ErrorResponse {
  error: string;
  code?: string;
  details?: Record<string, any>;
}

// Types pour l'authentification (complément à AuthContext)
export interface LoginCredentials {
  username: string;
  password: string;
}

export interface RegisterData {
  username: string;
  email: string;
  password: string;
  password2: string;
}

export interface AuthTokens {
  access: string;
  refresh: string;
}

export interface AuthUser {
  id: number;
  username: string;
  email: string;
}

// Types pour les listes existantes (complément)
export enum ListCategory {
  FILMS = "FILMS",
  SERIES = "SERIES",
  MUSIQUE = "MUSIQUE",
  LIVRES = "LIVRES",
}

export interface ListItem {
  id: number;
  title: string;
  description: string;
  position: number;
  list: number;
  is_watched: boolean;
  created_at: string;
  updated_at: string;
  external_ref?: ExternalReference;
  // Champs ajoutés dynamiquement côté frontend (non fournis par le backend sur certains endpoints)
  category?: string; // ex: 'FILMS'
  category_display?: string; // ex: 'Films'
  list_id?: number; // aide pour opérations PATCH/DELETE quand 'list' absent
}

export interface List {
  id: number;
  name: string;
  description: string;
  category: ListCategory;
  owner: number;
  created_at: string;
  updated_at: string;
  items?: ListItem[];
}

export interface ExternalReference {
  source: string;
  external_id: string;
  poster_url?: string;
  backdrop_url?: string;
  rating?: number;
  release_date?: string;
  year?: number;
  genres: string[];
  overview?: string;
  metadata: Record<string, any>;
}

// Types utilitaires
export type LoadingState = "idle" | "loading" | "success" | "error";

export interface AsyncState<T> {
  data: T | null;
  loading: boolean;
  error: string | null;
}

export type Optional<T, K extends keyof T> = Omit<T, K> & Partial<Pick<T, K>>;

export type DeepPartial<T> = {
  [P in keyof T]?: T[P] extends object ? DeepPartial<T[P]> : T[P];
};
