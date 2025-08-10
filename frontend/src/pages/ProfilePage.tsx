import React, { useState } from "react";
import { useAuth } from "../context/AuthContext";
import AppHeader from "../components/AppHeader";
import AppBottomNav from "../components/AppBottomNav";
import SocialProfile from "../components/SocialProfile";

// --- Icônes SVG ---

const EditIcon = ({ className }: { className?: string }) => (
  <svg
    className={className}
    fill="none"
    stroke="currentColor"
    viewBox="0 0 24 24"
    strokeWidth={2}
  >
    <path
      strokeLinecap="round"
      strokeLinejoin="round"
      d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z"
    />
  </svg>
);

const LogoutIcon = ({ className }: { className?: string }) => (
  <svg
    className={className}
    fill="none"
    stroke="currentColor"
    viewBox="0 0 24 24"
    strokeWidth={2}
  >
    <path
      strokeLinecap="round"
      strokeLinejoin="round"
      d="M17 16l4-4m0 0l-4-4m4 4H7m6 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h4a3 3 0 013 3v1"
    />
  </svg>
);

const SettingsIcon = ({ className }: { className?: string }) => (
  <svg
    className={className}
    fill="none"
    stroke="currentColor"
    viewBox="0 0 24 24"
    strokeWidth={2}
  >
    <path
      strokeLinecap="round"
      strokeLinejoin="round"
      d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z"
    />
    <path
      strokeLinecap="round"
      strokeLinejoin="round"
      d="M15 12a3 3 0 11-6 0 3 3 0 016 0z"
    />
  </svg>
);

const SocialIcon = ({ className }: { className?: string }) => (
  <svg
    className={className}
    fill="none"
    stroke="currentColor"
    viewBox="0 0 24 24"
    strokeWidth={2}
  >
    <path
      strokeLinecap="round"
      strokeLinejoin="round"
      d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z"
    />
  </svg>
);

interface ProfilePageProps {
  onNavigate?: (section: string) => void;
}

const ProfilePage: React.FC<ProfilePageProps> = ({ onNavigate }) => {
  const [bottomNavValue, setBottomNavValue] = useState(4); // Profil est à l'index 4
  const { logout } = useAuth();

  const handleBottomNavChange = (
    _event: React.SyntheticEvent,
    newValue: number
  ) => {
    setBottomNavValue(newValue);
    const sections = ["accueil", "decouvrir", "match", "listes", "profil"];
    onNavigate?.(sections[newValue]);
  };

  const handleLogout = async () => {
    try {
      await logout();
      // Sans router : onNavigate vers accueil après logout
      onNavigate?.("accueil");
    } catch (error) {
      console.error("Erreur lors de la déconnexion:", error);
    }
  };

  // stats détaillées déjà affichées dans SocialProfile

  const profileActions = [
    {
      icon: <EditIcon className="w-5 h-5" />,
      title: "Modifier le profil",
      description: "Mettre à jour vos informations personnelles",
      action: () => console.log("Modifier profil"),
    },
    {
      icon: <SettingsIcon className="w-5 h-5" />,
      title: "Paramètres",
      description: "Gérer vos préférences et confidentialité",
      action: () => console.log("Paramètres"),
    },
    {
      icon: <LogoutIcon className="w-5 h-5" />,
      title: "Se déconnecter",
      description: "Quitter votre session en cours",
      action: handleLogout,
    },
  ];

  return (
    <div className="min-h-screen tm-auth-bg font-inter">
      <AppHeader title="Compte" />

      <div className="h-[calc(100vh-4rem)] overflow-y-auto pb-20">
        <div className="w-full max-w-7xl mx-auto px-2 sm:px-4 md:px-6 lg:px-8 py-4 sm:py-8 space-y-4 sm:space-y-8">
          {/* Identité + édition profil social (display_name, bio, avatar, public) + copie gamertag */}
          <section>
            <SocialProfile />
          </section>

          {/* CTA vers Social */}
          <section className="tm-glass-card rounded-xl p-6">
            <div className="text-center">
              <button
                onClick={() => onNavigate?.("social")}
                className="inline-flex items-center gap-2 px-4 py-2 bg-tm-primary text-white rounded-lg hover:bg-tm-primary-700 transition"
              >
                <SocialIcon className="w-4 h-4" />
                Aller au Social
              </button>
            </div>
          </section>

          {/* Réglages / Gestion du compte */}
          <section className="tm-glass-card rounded-xl p-6">
            <h2 className="text-xl font-cinzel text-white mb-6">
              Gestion du compte
            </h2>
            <div className="space-y-4">
              {profileActions.map((action) => (
                <button
                  key={action.title}
                  onClick={action.action}
                  className="w-full tm-glass p-4 rounded-xl text-left group hover:scale-[1.02] transition-all duration-200"
                >
                  <div className="flex items-center gap-4">
                    <div className="p-3 tm-glass-card rounded-xl text-tm-primary group-hover:text-white transition-colors duration-200 flex-shrink-0">
                      {action.icon}
                    </div>
                    <div className="flex-1 min-w-0">
                      <h3 className="text-base font-semibold text-white group-hover:text-tm-primary transition-colors duration-200 mb-1">
                        {action.title}
                      </h3>
                      <p className="text-sm text-tm-text-muted">
                        {action.description}
                      </p>
                    </div>
                    <div className="text-tm-text-muted group-hover:text-white transition-colors duration-200 flex-shrink-0">
                      <svg
                        className="w-5 h-5"
                        fill="none"
                        stroke="currentColor"
                        viewBox="0 0 24 24"
                      >
                        <path
                          strokeLinecap="round"
                          strokeLinejoin="round"
                          strokeWidth={2}
                          d="M9 5l7 7-7 7"
                        />
                      </svg>
                    </div>
                  </div>
                </button>
              ))}
            </div>
          </section>
        </div>
      </div>

      <AppBottomNav value={bottomNavValue} onChange={handleBottomNavChange} />

      {/* Modales sociales retirées pour centraliser dans /social */}
    </div>
  );
};

export default ProfilePage;
