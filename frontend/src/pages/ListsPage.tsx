import React, { useState, useEffect } from "react";
import {
  Tab,
  TabGroup,
  TabList,
  TabPanel,
  TabPanels,
  Dialog,
  DialogPanel,
  DialogTitle,
} from "@headlessui/react";
import clsx from "clsx";
import type { List as TasteList, ListItem } from "../types";
import { useAuth } from "../context/AuthContext.tsx";
import AppHeader from "../components/AppHeader";
import AppBottomNav from "../components/AppBottomNav";
import FloatingAddButton from "../components/FloatingAddButton";
import { API_BASE_URL } from "../config";
import { matchApi } from "../services/matchApi";
import { ContentSource, ContentType, UserAction } from "../types/match";

// Utilisation du type TasteList global depuis types/index.ts

interface CategoryData {
  category_label: string;
  list: TasteList | null;
}

// Utilisation du type ListItem global depuis types/index.ts

interface ListsPageProps {
  onNavigate?: (section: string, params?: any) => void;
}

const ListsPage: React.FC<ListsPageProps> = ({ onNavigate }) => {
  const [categories, setCategories] = useState<Record<string, CategoryData>>(
    {}
  );
  const [allItems, setAllItems] = useState<ListItem[]>([]);
  const [filteredItems, setFilteredItems] = useState<ListItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [itemsLoading, setItemsLoading] = useState(false);
  const [error, setError] = useState("");
  const [selectedCategory, setSelectedCategory] = useState<string>("FILMS");
  const [bottomNavValue, setBottomNavValue] = useState(3); // "Mes listes" selected
  const [selectedItem, setSelectedItem] = useState<ListItem | null>(null);
  const [isModalOpen, setIsModalOpen] = useState(false);
  // Removed manual enrichment state variables
  // const [itemsToDelete, setItemsToDelete] = useState<Set<number>>(new Set()); // retiré (non utilisé)
  const [optionsOpen, setOptionsOpen] = useState<number | null>(null);
  const {} = useAuth();

  const handleBottomNavChange = (
    _event: React.SyntheticEvent,
    newValue: number
  ) => {
    setBottomNavValue(newValue);
    const sections = ["accueil", "decouvrir", "match", "listes", "profil"];
    onNavigate?.(sections[newValue]);
  };

  const handleItemClick = (item: ListItem) => {
    console.log("Item clicked:", item); // Debug pour voir les données
    setSelectedItem(item);
    setIsModalOpen(true);
  };

  const closeModal = () => {
    setIsModalOpen(false);
    setSelectedItem(null);
  };

  const toggleWatched = async (item: ListItem) => {
    try {
      const token = localStorage.getItem("access_token");
      const response = await fetch(
        `${API_BASE_URL}/lists/${
          item.list_id || getListIdForItem(item)
        }/items/${item.id}/`,
        {
          method: "PATCH",
          headers: {
            Authorization: `Bearer ${token}`,
            "Content-Type": "application/json",
          },
          body: JSON.stringify({
            is_watched: !item.is_watched,
          }),
        }
      );

      if (!response.ok) {
        throw new Error("Erreur lors de la mise à jour");
      }

      // Si on vient de marquer comme vu, proposer de liker/disliker pour alimenter les goûts
      const nowWatched = !item.is_watched;
      if (
        nowWatched &&
        item.external_ref?.external_id &&
        (item as any).category
      ) {
        const wantLike = window.confirm(
          'Vous venez de marquer cet élément comme vu/lu. Voulez-vous l\'aimer (Like) ?\nAppuyez sur "Annuler" pour Dislike.'
        );
        const action = wantLike ? UserAction.LIKED : UserAction.DISLIKED;
        try {
          await matchApi.submitAction({
            external_id: item.external_ref.external_id,
            source: (item.external_ref as any).source as ContentSource,
            content_type: (item as any).category as ContentType,
            action,
            title: item.title,
            metadata: (item.external_ref as any).metadata || {},
          } as any);
        } catch (e) {
          console.error("Erreur lors de l'enregistrement de la préférence:", e);
        }
      }

      // Rafraîchir les éléments après action
      fetchAllItems(selectedCategory);
    } catch (error) {
      console.error("Erreur lors du marquage:", error);
      // TODO: Afficher une notification d'erreur
    }
  };

  const deleteItem = async (item: ListItem) => {
    try {
      const token = localStorage.getItem("access_token");
      const response = await fetch(
        `${API_BASE_URL}/lists/${
          item.list_id || getListIdForItem(item)
        }/items/${item.id}/`,
        {
          method: "DELETE",
          headers: {
            Authorization: `Bearer ${token}`,
          },
        }
      );

      if (!response.ok) {
        throw new Error("Erreur lors de la suppression");
      }

      // Rafraîchir les éléments
      fetchAllItems(selectedCategory);
    } catch (error) {
      console.error("Erreur lors de la suppression:", error);
      // TODO: Afficher une notification d'erreur
    }
  };

  const getListIdForItem = (item: any): number => {
    // Trouver l'ID de la liste basé sur la catégorie de l'élément
    const categoryData = categories[item.category];
    return categoryData?.list?.id || 0;
  };

  // Removed manual enrichment functions - enrichment is now automatic

  // Fonctions simplifiées grâce à la normalisation côté backend
  const getPosterUrl = (item: ListItem): string | null => {
    return item.external_ref?.poster_url || null;
  };

  // backdrops non utilisés actuellement

  const getGenres = (item: ListItem): string[] => {
    return item.external_ref?.genres || [];
  };

  const getRating = (item: ListItem): number | null => {
    return item.external_ref?.rating || null;
  };

  const getYear = (item: ListItem): number | null => {
    return item.external_ref?.year || null;
  };

  const getOverview = (item: ListItem): string | null => {
    return item.external_ref?.overview || item.description || null;
  };

  const categories_config = [
    { key: "FILMS", label: "Films" },
    { key: "SERIES", label: "Séries" },
    { key: "MUSIQUE", label: "Musique" },
    { key: "LIVRES", label: "Livres" },
  ];

  // Fonction pour récupérer les listes par catégorie
  const fetchLists = async () => {
    try {
      const token = localStorage.getItem("access_token");
      const response = await fetch(`${API_BASE_URL}/lists/by_category/`, {
        headers: {
          Authorization: `Bearer ${token}`,
        },
      });

      if (!response.ok) {
        throw new Error("Erreur lors du chargement des listes");
      }

      const data = await response.json();
      setCategories(data);

      // Extraire tous les éléments de toutes les catégories
      const allItemsData: ListItem[] = [];
      for (const [categoryKey, categoryData] of Object.entries<any>(data)) {
        if (categoryData.list && categoryData.list.items) {
          const itemsWithCategory = categoryData.list.items.map(
            (item: any) => ({
              ...item,
              category: categoryKey,
              category_display: categoryData.category_label,
              list_id: categoryData.list.id,
            })
          );
          allItemsData.push(...itemsWithCategory);
        }
      }
      setAllItems(allItemsData);

      // Filtrer les éléments pour la catégorie sélectionnée
      const initialFilteredItems = allItemsData.filter(
        (item) => item.category === selectedCategory
      );
      setFilteredItems(initialFilteredItems);
    } catch (err) {
      setError("Impossible de charger les listes");
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  // Fonction pour récupérer tous les éléments de toutes les listes
  const fetchAllItems = async (categoryFilter?: string) => {
    try {
      setItemsLoading(true);

      // Filtrer les éléments existants par catégorie
      if (categoryFilter && allItems.length > 0) {
        const filteredItems = allItems.filter(
          (item) => item.category === categoryFilter
        );
        setFilteredItems(filteredItems);
      } else if (allItems.length === 0) {
        // Si pas d'éléments, recharger depuis fetchLists
        await fetchLists();
      }
    } catch (err) {
      console.error("Erreur lors du chargement des éléments:", err);
    } finally {
      setItemsLoading(false);
    }
  };

  useEffect(() => {
    fetchLists();
  }, []);

  useEffect(() => {
    if (Object.keys(categories).length > 0) {
      fetchAllItems(selectedCategory);
    }
  }, [categories, selectedCategory]);

  // Mettre à jour les éléments filtrés quand la catégorie change
  useEffect(() => {
    if (allItems.length > 0) {
      const filteredItems = allItems.filter(
        (item) => item.category === selectedCategory
      );
      setFilteredItems(filteredItems);
    }
  }, [selectedCategory, allItems]);

  // Fermer le menu d'options quand on clique ailleurs
  useEffect(() => {
    const handleClickOutside = () => {
      setOptionsOpen(null);
    };

    if (optionsOpen !== null) {
      document.addEventListener("click", handleClickOutside);
      return () => document.removeEventListener("click", handleClickOutside);
    }
  }, [optionsOpen]);

  return (
    <div className="min-h-screen tm-auth-bg font-inter">
      <AppHeader title="T4ST3 M4TCH" />

      <div className="main-content-with-safe-area">
        <div className="w-full max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4 space-y-6">
          {error && (
            <div
              className="tm-glass border border-red-400/40 text-red-400 p-4 rounded-xl text-sm text-center"
              style={{
                boxShadow:
                  "inset 0 1px 0 rgba(255, 255, 255, 0.15), 0 4px 12px rgba(239, 68, 68, 0.15)",
              }}
            >
              {error}
            </div>
          )}

          {loading ? (
            <div className="flex justify-center py-16">
              <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-tm-accent"></div>
            </div>
          ) : (
            <section className="tm-glass-card rounded-xl p-6">
              <TabGroup
                onChange={(index) => {
                  const categoryKey = categories_config[index].key;
                  setSelectedCategory(categoryKey);
                }}
              >
                <div className="flex justify-between items-center mb-6">
                  <TabList className="flex gap-1 overflow-x-auto scrollbar-hide flex-1 pr-2">
                    {categories_config.map((category) => (
                      <Tab
                        key={category.key}
                        className={({ selected, hover, focus }) =>
                          clsx(
                            "relative rounded-full px-3 py-2 text-xs sm:text-sm font-semibold transition-all duration-300 focus:outline-none whitespace-nowrap flex-shrink-0",
                            {
                              // État non sélectionné
                              "text-tm-text-muted": !selected,
                              "hover:bg-white/10": hover && !selected,
                              "focus:outline-2 focus:outline-white/50": focus,

                              // État sélectionné - seulement soulignement
                              "text-white": selected,
                            }
                          )
                        }
                      >
                        {({ selected }) => (
                          <>
                            <span
                              className={clsx(
                                "relative z-10 drop-shadow-sm transition-all duration-300",
                                {
                                  "underline decoration-tm-primary decoration-2 underline-offset-2":
                                    selected,
                                }
                              )}
                            >
                              {category.label}
                            </span>
                          </>
                        )}
                      </Tab>
                    ))}
                  </TabList>

                  {allItems.length > 0 && (
                    <span className="flex items-center justify-center w-8 h-8 text-sm font-semibold text-tm-text-muted bg-white/10 rounded-full">
                      {allItems.length}
                    </span>
                  )}
                </div>

                <TabPanels className="mt-6">
                  {categories_config.map((category) => (
                    <TabPanel
                      key={category.key}
                      className="rounded-xl bg-white/5 p-4"
                    >
                      {itemsLoading ? (
                        <ul className="space-y-1">
                          {Array.from({ length: 5 }).map((_, idx) => (
                            <li
                              key={idx}
                              className="relative rounded-md p-3 animate-pulse"
                            >
                              <div className="h-4 bg-white/10 rounded mb-2"></div>
                              <div className="h-3 bg-white/5 rounded w-3/4"></div>
                            </li>
                          ))}
                        </ul>
                      ) : (
                        <ul className="space-y-1">
                          {filteredItems.map((item: any) => (
                            <li
                              key={item.id}
                              className={`relative rounded-md p-3 text-sm/6 transition hover:bg-white/5 cursor-pointer ${
                                item.is_watched ? "opacity-70" : ""
                              }`}
                              onClick={() => handleItemClick(item)}
                            >
                              <div className="flex items-start gap-3">
                                {getPosterUrl(item) ? (
                                  <img
                                    src={getPosterUrl(item)!}
                                    alt={item.title}
                                    className="w-12 h-16 object-cover rounded flex-shrink-0"
                                    onError={(
                                      e: React.SyntheticEvent<HTMLImageElement>
                                    ) => {
                                      e.currentTarget.style.display = "none";
                                    }}
                                  />
                                ) : (
                                  // Image de fallback pour les éléments non enrichis
                                  <div className="w-12 h-16 bg-white/10 rounded flex-shrink-0 flex items-center justify-center border border-white/20 border-dashed">
                                    <svg
                                      className="w-6 h-6 text-tm-text-muted"
                                      fill="none"
                                      stroke="currentColor"
                                      viewBox="0 0 24 24"
                                    >
                                      <path
                                        strokeLinecap="round"
                                        strokeLinejoin="round"
                                        strokeWidth={2}
                                        d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z"
                                      />
                                    </svg>
                                  </div>
                                )}
                                <div className="flex-1 min-w-0">
                                  <div
                                    className={`font-semibold line-clamp-2 mb-1 transition-colors ${
                                      item.is_watched
                                        ? "text-tm-text-muted line-through"
                                        : "text-white"
                                    }`}
                                  >
                                    {item.is_watched && (
                                      <span className="text-green-400 mr-2">
                                        ✓
                                      </span>
                                    )}
                                    {item.title}
                                  </div>

                                  {/* Description supprimée pour optimiser l'espace - visible dans la modal */}

                                  {/* Informations supplémentaires */}
                                  <div className="flex flex-wrap gap-2 text-xs text-tm-text-muted">
                                    {getRating(item) && (
                                      <span className="flex items-center gap-1">
                                        <svg
                                          className="w-3 h-3 text-yellow-400"
                                          fill="currentColor"
                                          viewBox="0 0 20 20"
                                        >
                                          <path d="M9.049 2.927c.3-.921 1.603-.921 1.902 0l1.07 3.292a1 1 0 00.95.69h3.462c.969 0 1.371 1.24.588 1.81l-2.8 2.034a1 1 0 00-.364 1.118l1.07 3.292c.3.921-.755 1.688-1.54 1.118l-2.8-2.034a1 1 0 00-1.175 0l-2.8 2.034c-.784.57-1.838-.197-1.539-1.118l1.07-3.292a1 1 0 00-.364-1.118L2.98 8.72c-.783-.57-.38-1.81.588-1.81h3.461a1 1 0 00.951-.69l1.07-3.292z" />
                                        </svg>
                                        {getRating(item)}
                                      </span>
                                    )}

                                    {getYear(item) && (
                                      <span className="flex items-center gap-1">
                                        <svg
                                          className="w-3 h-3"
                                          fill="none"
                                          stroke="currentColor"
                                          viewBox="0 0 24 24"
                                        >
                                          <path
                                            strokeLinecap="round"
                                            strokeLinejoin="round"
                                            strokeWidth={2}
                                            d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z"
                                          />
                                        </svg>
                                        {getYear(item)}
                                      </span>
                                    )}

                                    {getGenres(item).length > 0 && (
                                      <span className="flex items-center gap-1">
                                        <svg
                                          className="w-3 h-3"
                                          fill="none"
                                          stroke="currentColor"
                                          viewBox="0 0 24 24"
                                        >
                                          <path
                                            strokeLinecap="round"
                                            strokeLinejoin="round"
                                            strokeWidth={2}
                                            d="M7 7h.01M7 3h5c.512 0 1.024.195 1.414.586l7 7a2 2 0 010 2.828l-7 7a2 2 0 01-2.828 0l-7-7A1.994 1.994 0 013 12V7a4 4 0 014-4z"
                                          />
                                        </svg>
                                        {getGenres(item).slice(0, 2).join(", ")}
                                        {getGenres(item).length > 2 && "..."}
                                      </span>
                                    )}
                                  </div>
                                </div>
                                <div className="relative ml-2">
                                  <button
                                    onClick={(e) => {
                                      e.stopPropagation();
                                      setOptionsOpen(
                                        optionsOpen === item.id ? null : item.id
                                      );
                                    }}
                                    className="p-2 bg-white/10 text-tm-text-muted hover:bg-white/20 hover:text-white rounded-full transition-colors"
                                    title="Options"
                                  >
                                    <svg
                                      className="w-4 h-4"
                                      fill="none"
                                      stroke="currentColor"
                                      viewBox="0 0 24 24"
                                    >
                                      <path
                                        strokeLinecap="round"
                                        strokeLinejoin="round"
                                        strokeWidth={2}
                                        d="M12 5v.01M12 12v.01M12 19v.01M12 6a1 1 0 110-2 1 1 0 010 2zm0 7a1 1 0 110-2 1 1 0 010 2zm0 7a1 1 0 110-2 1 1 0 010 2z"
                                      />
                                    </svg>
                                  </button>

                                  {optionsOpen === item.id && (
                                    <div className="absolute right-0 top-full mt-1 w-48 tm-glass-card rounded-lg overflow-hidden z-20 border border-white/20">
                                      <button
                                        onClick={(e) => {
                                          e.stopPropagation();
                                          toggleWatched(item);
                                          setOptionsOpen(null);
                                        }}
                                        className="w-full px-4 py-3 text-left text-sm hover:bg-white/10 transition-colors flex items-center gap-2"
                                      >
                                        <svg
                                          className="w-4 h-4"
                                          fill="none"
                                          stroke="currentColor"
                                          viewBox="0 0 24 24"
                                        >
                                          <path
                                            strokeLinecap="round"
                                            strokeLinejoin="round"
                                            strokeWidth={2}
                                            d={
                                              item.is_watched
                                                ? "M15 12a3 3 0 11-6 0 3 3 0 016 0z"
                                                : "M9 12l2 2 4-4"
                                            }
                                          />
                                        </svg>
                                        <span className="text-white">
                                          {item.is_watched
                                            ? "Marquer comme non vu"
                                            : "Marquer comme vu"}
                                        </span>
                                      </button>

                                      {/* Manual enrichment option removed - enrichment is now automatic */}
                                      <button
                                        onClick={(e) => {
                                          e.stopPropagation();
                                          setOptionsOpen(null);
                                          if (
                                            confirm(
                                              `Êtes-vous sûr de vouloir supprimer "${item.title}" ?`
                                            )
                                          ) {
                                            deleteItem(item);
                                          }
                                        }}
                                        className="w-full px-4 py-3 text-left text-sm hover:bg-red-500/20 transition-colors flex items-center gap-2 text-red-400"
                                      >
                                        <svg
                                          className="w-4 h-4"
                                          fill="none"
                                          stroke="currentColor"
                                          viewBox="0 0 24 24"
                                        >
                                          <path
                                            strokeLinecap="round"
                                            strokeLinejoin="round"
                                            strokeWidth={2}
                                            d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"
                                          />
                                        </svg>
                                        <span>Supprimer</span>
                                      </button>
                                    </div>
                                  )}
                                </div>
                              </div>
                            </li>
                          ))}
                        </ul>
                      )}

                      {!itemsLoading &&
                        filteredItems.length === 0 &&
                        !error && (
                          <div className="text-center py-8">
                            <div className="text-4xl mb-4">📋</div>
                            <p className="text-tm-text-muted mb-4">
                              Aucun élément trouvé dans la catégorie{" "}
                              {
                                categories_config.find(
                                  (c) => c.key === selectedCategory
                                )?.label
                              }
                            </p>
                            <button
                              onClick={() => onNavigate?.("decouvrir")}
                              className="tm-glass-button phi-button inline-flex items-center justify-center gap-2 rounded-xl focus:outline-none focus:ring-2 focus:ring-white/50"
                            >
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
                                  d="M12 4v16m8-8H4"
                                />
                              </svg>
                              Découvrir du contenu
                            </button>
                          </div>
                        )}
                    </TabPanel>
                  ))}
                </TabPanels>
              </TabGroup>
            </section>
          )}
        </div>
      </div>

      <AppBottomNav value={bottomNavValue} onChange={handleBottomNavChange} />

      {/* Modal de vue détaillée */}
      <Dialog open={isModalOpen} onClose={closeModal} className="relative z-50">
        <div
          className="fixed inset-0 bg-black/50 backdrop-blur-sm"
          aria-hidden="true"
        />

        <div className="fixed inset-0 flex items-center justify-center p-4">
          <DialogPanel className="tm-glass-card rounded-xl p-6 w-full max-w-md mx-auto">
            <div className="flex items-center justify-between mb-4">
              <DialogTitle className="text-lg font-semibold text-white">
                Détails
              </DialogTitle>
              <button
                onClick={closeModal}
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

            {selectedItem && (
              <div className="space-y-4">
                <div className="flex justify-center">
                  <div className="w-32 h-48 bg-white/10 rounded-lg overflow-hidden flex items-center justify-center">
                    {getPosterUrl(selectedItem) ? (
                      <img
                        src={getPosterUrl(selectedItem)!}
                        alt={selectedItem.title}
                        className="w-full h-full object-cover"
                        onError={(
                          e: React.SyntheticEvent<HTMLImageElement>
                        ) => {
                          e.currentTarget.src = "/vite.svg";
                        }}
                      />
                    ) : (
                      <div className="text-center">
                        <svg
                          className="w-12 h-12 text-tm-text-muted mx-auto mb-2"
                          fill="none"
                          stroke="currentColor"
                          viewBox="0 0 24 24"
                        >
                          <path
                            strokeLinecap="round"
                            strokeLinejoin="round"
                            strokeWidth={1}
                            d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z"
                          />
                        </svg>
                        <div className="text-xs text-tm-text-muted">
                          Pas d'image
                        </div>
                      </div>
                    )}
                  </div>
                </div>

                <div className="text-center">
                  <h3 className="text-xl font-bold text-white mb-2">
                    {selectedItem.title}
                  </h3>

                  <div className="flex justify-center mb-3">
                    <span className="px-3 py-1 text-xs font-semibold bg-tm-primary text-white rounded-full">
                      {(selectedItem as any).category_display}
                    </span>
                  </div>

                  {/* Description */}
                  {getOverview(selectedItem) && (
                    <p className="text-tm-text-muted text-sm leading-relaxed mb-4">
                      {getOverview(selectedItem)}
                    </p>
                  )}

                  {/* Informations supplémentaires */}
                  <div className="flex flex-wrap justify-center gap-3 mb-4 text-xs text-tm-text-muted">
                    {getRating(selectedItem) && (
                      <span className="flex items-center gap-1">
                        <svg
                          className="w-4 h-4 text-yellow-400"
                          fill="currentColor"
                          viewBox="0 0 20 20"
                        >
                          <path d="M9.049 2.927c.3-.921 1.603-.921 1.902 0l1.07 3.292a1 1 0 00.95.69h3.462c.969 0 1.371 1.24.588 1.81l-2.8 2.034a1 1 0 00-.364 1.118l1.07 3.292c.3.921-.755 1.688-1.54 1.118l-2.8-2.034a1 1 0 00-1.175 0l-2.8 2.034c-.784.57-1.838-.197-1.539-1.118l1.07-3.292a1 1 0 00-.364-1.118L2.98 8.72c-.783-.57-.38-1.81.588-1.81h3.461a1 1 0 00.951-.69l1.07-3.292z" />
                        </svg>
                        {getRating(selectedItem)}
                      </span>
                    )}

                    {getYear(selectedItem) && (
                      <span className="flex items-center gap-1">
                        <svg
                          className="w-4 h-4"
                          fill="none"
                          stroke="currentColor"
                          viewBox="0 0 24 24"
                        >
                          <path
                            strokeLinecap="round"
                            strokeLinejoin="round"
                            strokeWidth={2}
                            d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z"
                          />
                        </svg>
                        {getYear(selectedItem)}
                      </span>
                    )}
                  </div>

                  {/* Genres */}
                  {getGenres(selectedItem).length > 0 && (
                    <div className="mb-4">
                      <div className="text-xs text-tm-text-muted mb-2">
                        Genres :
                      </div>
                      <div className="flex flex-wrap justify-center gap-2">
                        {getGenres(selectedItem).map((genre, index) => (
                          <span
                            key={index}
                            className="px-2 py-1 text-xs bg-white/10 text-white rounded-full"
                          >
                            {genre}
                          </span>
                        ))}
                      </div>
                    </div>
                  )}

                  <div className="text-xs text-tm-text-muted">
                    Ajouté le{" "}
                    {new Date(selectedItem.created_at).toLocaleDateString(
                      "fr-FR",
                      {
                        year: "numeric",
                        month: "long",
                        day: "numeric",
                      }
                    )}
                  </div>
                </div>

                <div className="flex gap-2 pt-4">
                  <button
                    onClick={closeModal}
                    className="flex-1 tm-glass-button phi-button rounded-xl focus:outline-none focus:ring-2 focus:ring-white/50"
                  >
                    Fermer
                  </button>
                </div>
              </div>
            )}
          </DialogPanel>
        </div>
      </Dialog>

      <FloatingAddButton
        onAdd={() => {
          // Rafraîchir les listes après ajout
          fetchLists();
        }}
      />
    </div>
  );
};

export default ListsPage;
