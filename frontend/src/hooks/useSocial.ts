// Stubs simplifiés pour désactiver temporairement les features sociales
import type { UserProfile } from "../types/match";

export const useSocialProfile = () => ({
  // Profil nul tant que la feature sociale est désactivée
  profile: null as UserProfile | null,
  loading: false,
  error: null as string | null,
  // Signature réaliste pour éviter erreurs TS dans les composants
  updateProfile: async () => {
    return true;
  },
  refreshProfile: async () => {},
});

export const useFriends = () => ({
  friends: [] as unknown[],
  friendRequests: [] as unknown[],
  loading: false,
  error: null as string | null,
  addFriend: async () => false,
  acceptFriendRequest: async () => false,
  declineFriendRequest: async () => false,
  refreshFriends: async () => {},
  refreshFriendRequests: async () => {},
});

export const useFriendSearch = () => ({
  searchFriend: async () => false,
  addingFriend: false,
  searchError: null as string | null,
  lastSearchedGamertag: null as string | null,
});
