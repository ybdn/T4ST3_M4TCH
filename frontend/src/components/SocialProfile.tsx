/**
 * Composant pour afficher et éditer le profil social
 */

import React, { useState } from "react";
import { useSocialProfile } from "../hooks";
// Import du type désactivé mais laissé en commentaire pour future réactivation
// import type { UpdateProfileData } from "../types/match";

interface SocialProfileProps {
  onClose?: () => void;
}

const SocialProfile: React.FC<SocialProfileProps> = ({ onClose }) => {
  const { profile, loading, error } = useSocialProfile();
  // Edition désactivée (stub) – suppression des états inutiles
  const [copied, setCopied] = useState(false);

  if (loading) {
    return (
      <div className="tm-glass-card rounded-xl p-6">
        <div className="animate-pulse space-y-4">
          <div className="w-16 h-16 bg-white/20 rounded-full mx-auto"></div>
          <div className="h-4 bg-white/20 rounded w-3/4 mx-auto"></div>
          <div className="h-3 bg-white/20 rounded w-1/2 mx-auto"></div>
          <div className="h-8 bg-white/20 rounded w-full"></div>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="tm-glass-card rounded-xl p-6 text-center">
        <div className="text-4xl mb-4">😞</div>
        <p className="text-tm-text mb-4">Erreur lors du chargement du profil</p>
        <p className="text-tm-text-muted text-sm">{error}</p>
      </div>
    );
  }

  if (!profile) {
    return (
      <div className="tm-glass-card rounded-xl p-6 text-center">
        <div className="text-4xl mb-4">👤</div>
        <p className="text-tm-text text-sm">
          Fonctionnalité sociale bientôt disponible
        </p>
      </div>
    );
  }

  return (
    <div className="tm-glass-card rounded-xl p-6 space-y-6">
      {/* En-tête avec bouton fermer */}
      {onClose && (
        <div className="flex justify-between items-center">
          <h2 className="text-xl font-bold text-white">Profil Social</h2>
          <button
            onClick={onClose}
            className="text-tm-text-muted hover:text-white transition-colors"
          >
            <svg
              className="w-6 h-6"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M6 18L18 6M6 6l12 12"
              />
            </svg>
          </button>
        </div>
      )}

      {/* Avatar et informations principales */}
      <div className="text-center space-y-4">
        {/* Avatar */}
        <div className="relative mx-auto w-20 h-20">
          {profile.avatar_url ? (
            <img
              src={profile.avatar_url}
              alt={profile.display_name}
              className="w-full h-full rounded-full object-cover"
            />
          ) : (
            <div className="w-full h-full rounded-full bg-tm-primary flex items-center justify-center">
              <span className="text-2xl font-bold text-white">
                {profile.display_name.charAt(0).toUpperCase()}
              </span>
            </div>
          )}
          {!profile.is_public && (
            <div className="absolute -top-1 -right-1 w-6 h-6 bg-yellow-500 rounded-full flex items-center justify-center">
              <svg
                className="w-3 h-3 text-white"
                fill="currentColor"
                viewBox="0 0 20 20"
              >
                <path
                  fillRule="evenodd"
                  d="M5 9V7a5 5 0 0110 0v2a2 2 0 012 2v5a2 2 0 01-2 2H5a2 2 0 01-2-2v-5a2 2 0 012-2z"
                  clipRule="evenodd"
                />
              </svg>
            </div>
          )}
        </div>

        {/* Nom et gamertag */}
        <div>
          <h3 className="text-xl font-bold text-white">
            {profile.display_name}
          </h3>
          <div className="inline-flex items-center gap-2 mt-1">
            <p className="text-tm-text-muted">#{profile.gamertag}</p>
            <button
              onClick={async () => {
                try {
                  await navigator.clipboard.writeText(profile.gamertag);
                  setCopied(true);
                  setTimeout(() => setCopied(false), 1500);
                } catch {
                  /* ignore clipboard errors */
                }
              }}
              className="px-2 py-0.5 text-xs rounded-full bg-white/10 text-white hover:bg-white/20 transition"
              title="Copier le gamertag"
            >
              {copied ? "Copié" : "Copier"}
            </button>
          </div>
        </div>

        {/* Bio */}
        {profile.bio && (
          <p className="text-tm-text text-sm italic">"{profile.bio}"</p>
        )}
      </div>

      {/* Statistiques */}
      <div className="grid grid-cols-2 gap-4">
        <div className="text-center p-3 tm-glass rounded-lg">
          <div className="text-2xl font-bold text-tm-primary">
            {profile.stats.friends_count}
          </div>
          <div className="text-xs text-tm-text-muted">Amis</div>
        </div>
        <div className="text-center p-3 tm-glass rounded-lg">
          <div className="text-2xl font-bold text-tm-primary">
            {profile.stats.total_matches}
          </div>
          <div className="text-xs text-tm-text-muted">Matchs</div>
        </div>
      </div>

      {/* Options de confidentialité et boutons */}
      <div className="space-y-4">
        {/* Switch de visibilité désactivé en mode stub */}

        {/* Boutons d'action désactivés en stub */}
      </div>

      {/* Demandes d'amitié en attente */}
      {profile.stats.pending_requests > 0 && (
        <div className="p-3 bg-yellow-500/20 border border-yellow-500/30 rounded-lg">
          <div className="flex items-center">
            <svg
              className="w-5 h-5 text-yellow-500 mr-2"
              fill="currentColor"
              viewBox="0 0 20 20"
            >
              <path
                fillRule="evenodd"
                d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7-4a1 1 0 11-2 0 1 1 0 012 0zM9 9a1 1 0 000 2v3a1 1 0 001 1h1a1 1 0 100-2v-3a1 1 0 00-1-1H9z"
                clipRule="evenodd"
              />
            </svg>
            <span className="text-sm text-yellow-200">
              {profile.stats.pending_requests} demande
              {profile.stats.pending_requests > 1 ? "s" : ""} d'amitié en
              attente
            </span>
          </div>
        </div>
      )}
    </div>
  );
};

export default SocialProfile;
