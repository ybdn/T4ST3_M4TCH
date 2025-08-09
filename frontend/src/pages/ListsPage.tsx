import React, { useState, useEffect } from 'react';
import { Tab, TabGroup, TabList, TabPanel, TabPanels, Dialog, DialogPanel, DialogTitle } from '@headlessui/react';
import clsx from 'clsx';
import { useAuth } from '../context/AuthContext.tsx';
import AppHeader from '../components/AppHeader';
import AppBottomNav from '../components/AppBottomNav';
import FloatingAddButton from '../components/FloatingAddButton';
import { API_BASE_URL } from '../config';

interface TasteList {
  id: number;
  name: string;
  description: string;
  category: string;
  category_display: string;
  owner: string;
  items_count: number;
  created_at: string;
  updated_at: string;
}

interface CategoryData {
  category_label: string;
  list: TasteList | null;
}

interface ListItem {
  id: number;
  title: string;
  description: string;
  created_at: string;
  poster_url?: string;
  is_watched?: boolean;
  list_id?: number;
  external_ref?: {
    poster_url?: string;
    [key: string]: any;
  };
}


interface ListsPageProps {
  onNavigate?: (section: string, params?: any) => void;
}

const ListsPage: React.FC<ListsPageProps> = ({ onNavigate }) => {
  const [categories, setCategories] = useState<Record<string, CategoryData>>({});
  const [allItems, setAllItems] = useState<ListItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [itemsLoading, setItemsLoading] = useState(false);
  const [error, setError] = useState('');
  const [selectedCategory, setSelectedCategory] = useState<string>('all');
  const [bottomNavValue, setBottomNavValue] = useState(3); // "Mes listes" selected
  const [selectedItem, setSelectedItem] = useState<ListItem | null>(null);
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [itemsToDelete, setItemsToDelete] = useState<Set<number>>(new Set());
  const { } = useAuth();

  const handleBottomNavChange = (_event: React.SyntheticEvent, newValue: number) => {
    setBottomNavValue(newValue);
    const sections = ['accueil', 'decouvrir', 'match', 'listes', 'profil'];
    onNavigate?.(sections[newValue]);
  };

  const handleItemClick = (item: ListItem) => {
    console.log('Item clicked:', item); // Debug pour voir les données
    setSelectedItem(item);
    setIsModalOpen(true);
  };

  const closeModal = () => {
    setIsModalOpen(false);
    setSelectedItem(null);
  };

  const toggleWatched = async (item: ListItem) => {
    try {
      const token = localStorage.getItem('access_token');
      const response = await fetch(`${API_BASE_URL}/lists/${item.list_id || getListIdForItem(item)}/items/${item.id}/`, {
        method: 'PATCH',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          is_watched: !item.is_watched
        })
      });

      if (!response.ok) {
        throw new Error('Erreur lors de la mise à jour');
      }

      // Rafraîchir les éléments
      fetchAllItems(selectedCategory);
    } catch (error) {
      console.error('Erreur lors du marquage:', error);
      // TODO: Afficher une notification d'erreur
    }
  };

  const deleteItem = async (item: ListItem) => {
    try {
      const token = localStorage.getItem('access_token');
      const response = await fetch(`${API_BASE_URL}/lists/${item.list_id || getListIdForItem(item)}/items/${item.id}/`, {
        method: 'DELETE',
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });

      if (!response.ok) {
        throw new Error('Erreur lors de la suppression');
      }

      // Rafraîchir les éléments
      fetchAllItems(selectedCategory);
    } catch (error) {
      console.error('Erreur lors de la suppression:', error);
      // TODO: Afficher une notification d'erreur
    }
  };

  const getListIdForItem = (item: any): number => {
    // Trouver l'ID de la liste basé sur la catégorie de l'élément
    const categoryData = categories[item.category];
    return categoryData?.list?.id || 0;
  };


  const categories_config = [
    { key: 'all', label: 'Tous' },
    { key: 'FILMS', label: 'Films' },
    { key: 'SERIES', label: 'Séries' },
    { key: 'MUSIQUE', label: 'Musique' },
    { key: 'LIVRES', label: 'Livres' },
  ];

  // Fonction pour récupérer les listes par catégorie
  const fetchLists = async () => {
    try {
      const token = localStorage.getItem('access_token');
      const response = await fetch(`${API_BASE_URL}/lists/by_category/`, {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });

      if (!response.ok) {
        throw new Error('Erreur lors du chargement des listes');
      }

      const data = await response.json();
      setCategories(data);
    } catch (err) {
      setError('Impossible de charger les listes');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  // Fonction pour récupérer tous les éléments de toutes les listes
  const fetchAllItems = async (categoryFilter?: string) => {
    try {
      setItemsLoading(true);
      const token = localStorage.getItem('access_token');
      const allItemsData: ListItem[] = [];

      // Récupérer les éléments de chaque catégorie
      for (const [categoryKey, categoryData] of Object.entries(categories)) {
        if (categoryFilter && categoryFilter !== 'all' && categoryKey !== categoryFilter) {
          continue;
        }
        
        if (categoryData.list) {
          const response = await fetch(`${API_BASE_URL}/lists/${categoryData.list.id}/items/`, {
            headers: {
              'Authorization': `Bearer ${token}`
            }
          });

          if (response.ok) {
            const items = await response.json();
            // Ajouter la catégorie à chaque item pour le filtrage
            const itemsWithCategory = items.map((item: any) => ({
              ...item,
              category: categoryKey,
              category_display: categoryData.category_label,
              list_id: categoryData.list.id
            }));
            allItemsData.push(...itemsWithCategory);
          }
        }
      }

      setAllItems(allItemsData);
    } catch (err) {
      console.error('Erreur lors du chargement des éléments:', err);
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


  return (
    <div className="min-h-screen tm-auth-bg font-inter">
      <AppHeader title="T4ST3 M4TCH" />

      <div className="h-[calc(100vh-4rem)] overflow-y-auto pb-20">
        <div className="w-full max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4 space-y-6">

          {error && (
            <div className="tm-glass border border-red-400/40 text-red-400 p-4 rounded-xl text-sm text-center" style={{
              boxShadow: 'inset 0 1px 0 rgba(255, 255, 255, 0.15), 0 4px 12px rgba(239, 68, 68, 0.15)'
            }}>
              {error}
            </div>
          )}

          {loading ? (
            <div className="flex justify-center py-16">
              <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-tm-accent"></div>
            </div>
          ) : (
            <section className="tm-glass-card rounded-xl p-6">
              <TabGroup onChange={(index) => {
                const categoryKey = categories_config[index].key;
                setSelectedCategory(categoryKey);
              }}>
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
                            <span className={clsx(
                              "relative z-10 drop-shadow-sm transition-all duration-300",
                              {
                                "underline decoration-tm-primary decoration-2 underline-offset-2": selected
                              }
                            )}>
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
                    <TabPanel key={category.key} className="rounded-xl bg-white/5 p-4">
                      {itemsLoading ? (
                        <ul className="space-y-1">
                          {Array.from({ length: 5 }).map((_, idx) => (
                            <li key={idx} className="relative rounded-md p-3 animate-pulse">
                              <div className="h-4 bg-white/10 rounded mb-2"></div>
                              <div className="h-3 bg-white/5 rounded w-3/4"></div>
                            </li>
                          ))}
                        </ul>
                      ) : (
                        <ul className="space-y-1">
                          {allItems.map((item: any) => (
                            <li key={item.id} className={`relative rounded-md p-3 text-sm/6 transition hover:bg-white/5 cursor-pointer ${
                              item.is_watched ? 'opacity-70' : ''
                            }`} onClick={() => handleItemClick(item)}>
                              <div className="flex items-start gap-3">
                                {(item.external_ref?.poster_url || item.poster_url) && (
                                  <img
                                    src={item.external_ref?.poster_url || item.poster_url}
                                    alt={item.title}
                                    className="w-12 h-16 object-cover rounded flex-shrink-0"
                                    onError={(e: React.SyntheticEvent<HTMLImageElement>) => { 
                                      e.currentTarget.style.display = 'none';
                                    }}
                                  />
                                )}
                                <div className="flex-1 min-w-0">
                                  <div className={`font-semibold line-clamp-2 mb-1 transition-colors ${
                                    item.is_watched ? 'text-tm-text-muted line-through' : 'text-white'
                                  }`}>
                                    {item.is_watched && <span className="text-green-400 mr-2">✓</span>}
                                    {item.title}
                                  </div>
                                  {item.description && (
                                    <p className="text-tm-text-muted text-xs line-clamp-2 mb-2">
                                      {item.description}
                                    </p>
                                  )}
                                  <ul className="flex gap-2 text-tm-text-muted text-xs" aria-hidden="true">
                                    <li>{item.category_display}</li>
                                    <li aria-hidden="true">&middot;</li>
                                    <li>{new Date(item.created_at).toLocaleDateString('fr-FR')}</li>
                                  </ul>
                                </div>
                                <div className="flex gap-1 ml-2">
                                  <button
                                    onClick={(e) => {
                                      e.stopPropagation();
                                      toggleWatched(item);
                                    }}
                                    className={`p-2 rounded-full transition-colors ${
                                      item.is_watched 
                                        ? 'bg-green-500/20 text-green-400 hover:bg-green-500/30' 
                                        : 'bg-gray-500/20 text-gray-400 hover:bg-gray-500/30'
                                    }`}
                                    title={item.is_watched ? 'Marquer comme non vu' : 'Marquer comme vu'}
                                  >
                                    <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} 
                                            d={item.is_watched ? "M9 12l2 2 4-4" : "M15 12a3 3 0 11-6 0 3 3 0 016 0z"} />
                                    </svg>
                                  </button>
                                  <button
                                    onClick={(e) => {
                                      e.stopPropagation();
                                      if (confirm(`Êtes-vous sûr de vouloir supprimer "${item.title}" ?`)) {
                                        deleteItem(item);
                                      }
                                    }}
                                    className="p-2 bg-red-500/20 text-red-400 hover:bg-red-500/30 rounded-full transition-colors"
                                    title="Supprimer l'élément"
                                  >
                                    <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                                    </svg>
                                  </button>
                                </div>
                              </div>
                            </li>
                          ))}
                        </ul>
                      )}
                      
                      {!itemsLoading && allItems.length === 0 && !error && (
                        <div className="text-center py-8">
                          <div className="text-4xl mb-4">📋</div>
                          <p className="text-tm-text-muted mb-4">
                            {selectedCategory === 'all' 
                              ? 'Aucun élément trouvé dans vos listes'
                              : `Aucun élément trouvé dans la catégorie ${categories_config.find(c => c.key === selectedCategory)?.label}`
                            }
                          </p>
                          <button 
                            onClick={() => onNavigate?.('decouvrir')}
                            className="tm-glass-button phi-button inline-flex items-center justify-center gap-2 rounded-xl focus:outline-none focus:ring-2 focus:ring-white/50"
                          >
                            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
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
        <div className="fixed inset-0 bg-black/50 backdrop-blur-sm" aria-hidden="true" />
        
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
                <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                </svg>
              </button>
            </div>
            
            {selectedItem && (
              <div className="space-y-4">
                <div className="flex justify-center">
                  <div className="w-32 h-48 bg-white/10 rounded-lg overflow-hidden flex items-center justify-center">
                    {(selectedItem.external_ref?.poster_url || selectedItem.poster_url) ? (
                      <img
                        src={selectedItem.external_ref?.poster_url || selectedItem.poster_url}
                        alt={selectedItem.title}
                        className="w-full h-full object-cover"
                        onError={(e: React.SyntheticEvent<HTMLImageElement>) => {
                          e.currentTarget.src = '/vite.svg';
                        }}
                      />
                    ) : (
                      <div className="text-center">
                        <svg className="w-12 h-12 text-tm-text-muted mx-auto mb-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1} d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z" />
                        </svg>
                        <div className="text-xs text-tm-text-muted">Pas d'image</div>
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
                  
                  {selectedItem.description && (
                    <p className="text-tm-text-muted text-sm leading-relaxed mb-4">
                      {selectedItem.description}
                    </p>
                  )}
                  
                  <div className="text-xs text-tm-text-muted">
                    Ajouté le {new Date(selectedItem.created_at).toLocaleDateString('fr-FR', {
                      year: 'numeric',
                      month: 'long',
                      day: 'numeric'
                    })}
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
      
      <FloatingAddButton onAdd={() => {
        // Rafraîchir les listes après ajout
        fetchLists();
        if (Object.keys(categories).length > 0) {
          fetchAllItems(selectedCategory);
        }
      }} />
    </div>
  );
};

export default ListsPage;