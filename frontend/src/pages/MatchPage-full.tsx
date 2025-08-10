import React, { useState, useEffect } from "react";
import { Tab, TabGroup, TabList, TabPanel, TabPanels } from "@headlessui/react";
import AppHeader from "../components/AppHeader";
import AppBottomNav from "../components/AppBottomNav";
import clsx from "clsx";
import { useMatchRecommendations } from "../hooks";
// UserAction non utilisé dans stub
import { VersusMatch, FriendsManager } from "../components";

// --- Icônes SVG ---
const ThumbUpIcon = ({ className }: { className?: string }) => (
  <svg
    xmlns="http://www.w3.org/2000/svg"
    className={className}
    fill="currentColor"
    viewBox="0 0 24 24"
    strokeWidth={0}
  >
    <path d="M2 20h2c.55 0 1-.45 1-1v-9c0-.55-.45-1-1-1H2v11zm19.83-7.12c.11-.25.17-.52.17-.8V8c0-1.1-.9-2-2-2h-4.26l.95-4.57.03-.32c0-.41-.17-.79-.44-1.06L14.17 0 7.58 6.59C7.22 6.95 7 7.45 7 8v10c0 1.1.9 2 2 2h9c.83 0 1.54-.5 1.84-1.22l3.02-7.05z" />
  </svg>
);
const ThumbDownIcon = ({ className }: { className?: string }) => (
  <svg
    xmlns="http://www.w3.org/2000/svg"
    className={className}
    fill="currentColor"
    viewBox="0 0 24 24"
    strokeWidth={0}
  >
    <path d="M22 4h-2c-.55 0-1 .45-1 1v9c0 .55.45 1 1 1h2V4zM2.17 11.12c-.11.25-.17.52-.17.8V16c0 1.1.9 2 2 2h4.26l-.95 4.57-.03.32c0 .41.17.79.44 1.06L9.83 24l6.59-6.59C16.78 17.05 17 16.55 17 16V6c0-1.1-.9-2-2-2H6c-.83 0-1.54.5-1.84 1.22l-3.02 7.05z" />
  </svg>
);
const RefreshIcon = ({ className }: { className?: string }) => (
  <svg
    xmlns="http://www.w3.org/2000/svg"
    className={className}
    fill="none"
    viewBox="0 0 24 24"
    stroke="currentColor"
    strokeWidth={2}
  >
    <path
      strokeLinecap="round"
      strokeLinejoin="round"
      d="M4 4v5h5M20 20v-5h-5M4 4l1.5 1.5A9 9 0 0120.5 15M20 20l-1.5-1.5A9 9 0 003.5 9"
    />
  </svg>
);

// --- Interfaces ---
interface MatchPageProps {
  onNavigate?: (section: string) => void;
}

const MatchPage: React.FC<MatchPageProps> = ({ onNavigate }) => {
  const [bottomNavValue, setBottomNavValue] = useState(2); // Match est à l'index 2
  const [selectedTab, setSelectedTab] = useState(0); // 0 = Global, 1 = Versus

  // Versus désactivé temporairement
  const [showFriends, setShowFriends] = useState(false);

  // Hook pour les recommandations
  const {
    recommendations,
    loading,
    error,
    fetchRecommendations,
    submitAction,
    currentIndex,
    nextRecommendation,
    hasMore,
    refresh,
  } = useMatchRecommendations();

  // Charger les recommandations au montage
  useEffect(() => {
    if (selectedTab === 0 && recommendations.length === 0) {
      fetchRecommendations();
    }
  }, [selectedTab, fetchRecommendations, recommendations.length]);

  const currentItem = recommendations[currentIndex];

  const handleBottomNavChange = (
    _event: React.SyntheticEvent,
    newValue: number
  ) => {
    setBottomNavValue(newValue);
    const sections = ["accueil", "decouvrir", "match", "listes", "profil"];
    onNavigate?.(sections[newValue]);
  };

  const handleAction = async () => {
    if (!currentItem) return;
    const success = await submitAction();
    if (success) {
      nextRecommendation();

      // Si on arrive à la fin des recommandations, en charger plus
      if (!hasMore) fetchRecommendations();
    }
  };

  const handleLike = () => handleAction();
  const handleDislike = () => handleAction();
  const handleAdd = () => handleAction();

  const handleRefresh = () => {
    refresh();
  };

  // Fonction pour générer des raisons de compatibilité basées sur les métadonnées
  const getCompatibilityReasons = (item: typeof currentItem) => {
    if (!item) return [] as string[];
    const meta = (item.metadata || {}) as Record<string, unknown> & {
      genre_ids?: unknown;
      vote_average?: unknown;
      popularity?: unknown;
    };
    const reasons: string[] = [];
    if (Array.isArray(meta.genre_ids) && meta.genre_ids.length > 0) {
      reasons.push("Genre compatible");
    }
    const vote = typeof meta.vote_average === "number" ? meta.vote_average : undefined;
    if (vote !== undefined && vote > 7) {
      reasons.push("Très bien noté");
    }
    const popularity = typeof meta.popularity === "number" ? meta.popularity : undefined;
    if (popularity !== undefined && popularity > 100) {
      reasons.push("Populaire");
    }
    if ((item.compatibility_score ?? 0) > 80) {
      reasons.push("Forte compatibilité");
    }

    return reasons.length > 0 ? reasons : ["Recommandé pour vous"];
  };

  // Versus handlers désactivés

  return (
    <div className="min-h-screen tm-auth-bg font-inter">
      <AppHeader title="T4ST3 M4TCH" />

      <div
        className="flex flex-col px-4 sm:px-6 lg:px-8"
        style={{
          height: "calc(100vh - 2.5rem - 3.5rem)",
          paddingTop: "calc(2.5rem + env(safe-area-inset-top))",
          paddingBottom: "calc(3.5rem + env(safe-area-inset-bottom))",
        }}
      >
        {/* Onglets discrets */}
        <div className="mb-3">
          <TabGroup selectedIndex={selectedTab} onChange={setSelectedTab}>
            <TabList className="flex justify-center gap-8">
              <Tab
                className={({ selected }) =>
                  clsx(
                    "px-1 py-1 text-sm font-medium transition-all duration-200 focus:outline-none relative",
                    {
                      "text-white": selected,
                      "text-tm-text-muted hover:text-white/70": !selected,
                    }
                  )
                }
              >
                {({ selected }) => (
                  <>
                    Global
                    {selected && (
                      <div className="absolute -bottom-1 left-0 right-0 h-0.5 bg-white rounded-full" />
                    )}
                  </>
                )}
              </Tab>
              <Tab
                className={({ selected }) =>
                  clsx(
                    "px-1 py-1 text-sm font-medium transition-all duration-200 focus:outline-none relative",
                    {
                      "text-white": selected,
                      "text-tm-text-muted hover:text-white/70": !selected,
                    }
                  )
                }
              >
                {({ selected }) => (
                  <>
                    Versus
                    {selected && (
                      <div className="absolute -bottom-1 left-0 right-0 h-0.5 bg-white rounded-full" />
                    )}
                  </>
                )}
              </Tab>
            </TabList>
          </TabGroup>
        </div>

        {/* Card de match - occupe l'espace restant */}
        <div className="flex-1 flex items-center justify-center py-2">
          <TabGroup selectedIndex={selectedTab} onChange={setSelectedTab}>
            <TabPanels className="w-full max-w-sm h-full flex items-center justify-center">
              {/* Panel Global */}
              <TabPanel className="w-full h-full flex items-center justify-center">
                <div
                  className="tm-glass-card rounded-xl overflow-hidden w-full"
                  style={{
                    height: "510px",
                    maxHeight: "510px",
                    minHeight: "450px",
                  }}
                >
                  {/* États de chargement et d'erreur */}
                  {loading && (
                    <div className="h-full flex items-center justify-center">
                      <div className="text-center">
                        <div className="animate-spin rounded-full h-12 w-12 border-2 border-tm-primary border-t-transparent mx-auto mb-4"></div>
                        <p className="text-tm-text">
                          Chargement des recommandations...
                        </p>
                      </div>
                    </div>
                  )}

                  {error && (
                    <div className="h-full flex items-center justify-center">
                      <div className="text-center">
                        <div className="text-6xl mb-4">😞</div>
                        <p className="text-tm-text mb-4">
                          Erreur lors du chargement
                        </p>
                        <button
                          onClick={handleRefresh}
                          className="px-4 py-2 bg-tm-primary text-white rounded-lg hover:bg-tm-primary-700 transition-colors"
                        >
                          <RefreshIcon className="h-4 w-4 inline mr-2" />
                          Réessayer
                        </button>
                      </div>
                    </div>
                  )}

                  {/* Pas de recommandations */}
                  {!loading && !error && !currentItem && (
                    <div className="h-full flex items-center justify-center">
                      <div className="text-center">
                        <div className="text-6xl mb-4">🎯</div>
                        <p className="text-tm-text mb-4">
                          Aucune recommandation disponible
                        </p>
                        <button
                          onClick={handleRefresh}
                          className="px-4 py-2 bg-tm-primary text-white rounded-lg hover:bg-tm-primary-700 transition-colors"
                        >
                          <RefreshIcon className="h-4 w-4 inline mr-2" />
                          Actualiser
                        </button>
                      </div>
                    </div>
                  )}

                  {/* Contenu principal avec recommandation */}
                  {!loading && !error && currentItem && (
                    <>
                      {/* Image de couverture */}
                      <div className="relative h-1/2 overflow-hidden">
                        <img
                          src={currentItem.poster_url || "/vite.svg"}
                          alt={currentItem.title}
                          className="w-full h-full object-cover"
                          onError={(
                            e: React.SyntheticEvent<HTMLImageElement>
                          ) => {
                            e.currentTarget.src = "/vite.svg";
                          }}
                        />
                        <div className="absolute inset-0 bg-gradient-to-t from-black/60 via-transparent to-transparent" />

                        {/* Score de compatibilité en overlay */}
                        <div className="absolute top-4 right-4 bg-white/10 backdrop-blur-md rounded-full px-3 py-2">
                          <p className="text-2xl font-bold text-white">
                            {Math.round(currentItem.compatibility_score ?? 0)}%
                          </p>
                          <p className="text-xs text-white/80 text-center">
                            Match
                          </p>
                        </div>

                        {/* Badge catégorie en overlay */}
                        <div className="absolute top-4 left-4">
                          <span className="px-3 py-1 text-xs font-semibold bg-tm-primary text-white rounded-full">
                            {currentItem.content_type}
                          </span>
                        </div>
                      </div>

                      {/* Contenu */}
                      <div className="h-1/2 p-6 flex flex-col justify-between text-center">
                        {/* Contenu principal */}
                        <div className="flex-1">
                          {/* Titre */}
                          <h1 className="text-xl font-bold font-cinzel text-white mb-2">
                            {currentItem.title}
                          </h1>

                          {/* Description */}
                          <p className="text-sm text-tm-text-muted mb-3 leading-relaxed line-clamp-2">
                            {currentItem.description ||
                              currentItem.metadata?.description ||
                              "Découvrez ce contenu recommandé pour vous"}
                          </p>

                          {/* Raisons du match */}
                          <div className="mb-4">
                            <h2 className="text-sm font-semibold text-tm-text mb-2">
                              Pourquoi ce match ?
                            </h2>
                            <div className="flex flex-wrap justify-center gap-1">
                              {getCompatibilityReasons(currentItem).map(
                                (reason) => (
                                  <span
                                    key={reason}
                                    className="px-2 py-1 text-xs tm-glass rounded-full text-tm-text-muted"
                                  >
                                    {reason}
                                  </span>
                                )
                              )}
                            </div>
                          </div>
                        </div>

                        {/* Boutons d'action */}
                        <div className="flex gap-4 justify-center">
                          <button
                            onClick={handleDislike}
                            className="w-14 h-14 flex items-center justify-center bg-red-500/20 text-red-400 rounded-full hover:bg-red-500/30 hover:scale-110 transition-all duration-200"
                            title="Ne pas aimer"
                          >
                            <ThumbDownIcon className="h-6 w-6" />
                          </button>
                          <button
                            onClick={handleAdd}
                            className="w-14 h-14 flex items-center justify-center bg-blue-500/20 text-blue-400 rounded-full hover:bg-blue-500/30 hover:scale-110 transition-all duration-200"
                            title="Ajouter à ma liste"
                          >
                            <svg
                              className="h-6 w-6"
                              fill="none"
                              stroke="currentColor"
                              viewBox="0 0 24 24"
                            >
                              <path
                                strokeLinecap="round"
                                strokeLinejoin="round"
                                strokeWidth={2}
                                d="M12 4v16m8-8H4"
                              />
                            </svg>
                          </button>
                          <button
                            onClick={handleLike}
                            className="w-14 h-14 flex items-center justify-center bg-green-500/20 text-green-400 rounded-full hover:bg-green-500/30 hover:scale-110 transition-all duration-200"
                            title="J'aime"
                          >
                            <ThumbUpIcon className="h-6 w-6" />
                          </button>
                        </div>
                      </div>
                    </>
                  )}
                </div>
              </TabPanel>

              {/* Panel Versus */}
              <TabPanel className="w-full h-full flex items-center justify-center">
                <div className="w-full max-w-sm">
                  <VersusMatch />
                </div>
              </TabPanel>
            </TabPanels>
          </TabGroup>
        </div>
      </div>

      <AppBottomNav value={bottomNavValue} onChange={handleBottomNavChange} />

      {/* Modal de sélection des amis */}
      {showFriends && (
        <div className="fixed inset-0 bg-black/50 backdrop-blur-sm z-50 flex items-center justify-center p-4">
          <div className="w-full max-w-md max-h-[80vh] overflow-y-auto">
            <FriendsManager
              onClose={() => setShowFriends(false)}
              // onSelectFriend={handleSelectFriend} // (désactivé: fonction non implémentée dans version simplifiée)
            />
          </div>
        </div>
      )}
    </div>
  );
};

export default MatchPage;
