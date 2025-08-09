import React, { useEffect, useState } from 'react';
import { Tab, TabGroup, TabList, TabPanel, TabPanels } from '@headlessui/react';
import clsx from 'clsx';
import ExternalSearchBar from '../components/ExternalSearchBar';
import AppHeader from '../components/AppHeader';
import AppBottomNav from '../components/AppBottomNav';
import { API_BASE_URL } from '../config';

// Types
interface TrendingItem {
  external_id: string;
  source: string;
  category: string;
  category_display: string;
  title: string;
  description?: string;
  poster_url?: string;
  release_date?: string;
}

interface ExternalSearchResult {
  external_id: string;
  source: string;
  category: string;
  title: string;
  description?: string;
  poster_url?: string;
}

interface ExplorePageProps {
  onNavigate?: (section: string) => void;
}

const ExplorePage: React.FC<ExplorePageProps> = ({ onNavigate }) => {
  const [bottomNavValue, setBottomNavValue] = useState(1); // "Découvrir" selected
  const [selectedCategory, setSelectedCategory] = useState<string>('all');
  const [trending, setTrending] = useState<TrendingItem[]>([]);
  const [loading, setLoading] = useState<boolean>(false);
  const [error, setError] = useState<string>('');
  const [searchSuggestionsVisible, setSearchSuggestionsVisible] = useState<boolean>(false);
  const [searchResultsCount, setSearchResultsCount] = useState<number>(0);

  const handleBottomNavChange = (_event: React.SyntheticEvent, newValue: number) => {
    setBottomNavValue(newValue);
    const sections = ['accueil', 'decouvrir', 'match', 'listes', 'profil'];
    onNavigate?.(sections[newValue]);
  };


  const categories = [
    { key: 'all', label: 'Tous' },
    { key: 'FILMS', label: 'Films' },
    { key: 'SERIES', label: 'Séries' },
    { key: 'MUSIQUE', label: 'Musique' },
    { key: 'LIVRES', label: 'Livres' },
  ];

  const fetchTrending = async (category?: string) => {
    try {
      setLoading(true);
      setError('');
      const token = localStorage.getItem('access_token');
      const params = new URLSearchParams();
      if (category && category !== 'all') {
        params.append('category', category);
      }
      params.append('limit', '10');
      const response = await fetch(`${API_BASE_URL}/trending/external/?${params.toString()}`, {
        headers: {
          Authorization: `Bearer ${token}`,
        },
      });
      if (!response.ok) {
        throw new Error('Erreur lors du chargement des tendances');
      }
      const data = await response.json();
      setTrending(data.results || []);
    } catch (e: unknown) {
      const errorMessage = e instanceof Error ? e.message : 'Erreur lors du chargement';
      setError(errorMessage);
      setTrending([]);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchTrending(selectedCategory);
  }, [selectedCategory]);

  const handleAddFromTrending = async (item: TrendingItem | ExternalSearchResult) => {
    const token = localStorage.getItem('access_token');
    const response = await fetch(`${API_BASE_URL}/import/external/`, {
      method: 'POST',
      headers: {
        Authorization: `Bearer ${token}`,
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        external_id: item.external_id,
        source: item.source,
        category: item.category,
      }),
    });
    if (!response.ok) {
      const data = await response.json();
      throw new Error(data.error || 'Erreur lors de l\'ajout');
    }
  };

  return (
    <div className="min-h-screen tm-auth-bg font-inter">
      <AppHeader title="T4ST3 M4TCH" />

      <div className="h-[calc(100vh-4rem)] overflow-y-auto pb-20">
        <div className="w-full max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-8">
          
          {/* Hero Section */}
          <section className="text-center">
            <h1 className="text-lg xs:text-xl sm:text-2xl md:text-3xl lg:phi-title font-cinzel text-white mb-4 break-words leading-tight">
              Découvrez vos prochains coups de cœur ✨
            </h1>
            <p className="text-sm sm:phi-description text-tm-text-muted leading-relaxed max-w-2xl mx-auto">
              Explorez les tendances et trouvez votre prochain film, série, album ou livre préféré
            </p>
          </section>

          {/* Barre de recherche */}
          <section className={`tm-glass-card rounded-xl p-6 transition-all duration-300 ${
            searchSuggestionsVisible ? 'min-h-[520px] relative z-20' : ''
          }`}>
            <div className="flex items-center justify-between mb-4">
              <h2 className="phi-subtitle font-cinzel text-tm-text">
                Recherche externe
              </h2>
              {searchResultsCount > 0 && (
                <span className="flex items-center justify-center w-8 h-8 text-sm font-semibold text-tm-text-muted bg-white/10 rounded-full">
                  {searchResultsCount}
                </span>
              )}
            </div>
            <ExternalSearchBar
              showSourceFilter
              onSelect={(r: ExternalSearchResult) => handleAddFromTrending(r)}
              onQuickAdd={(r: ExternalSearchResult) => handleAddFromTrending(r)}
              onSuggestionsToggle={setSearchSuggestionsVisible}
              onResultsCount={setSearchResultsCount}
            />
          </section>

          {/* Section Tendances avec TabGroup */}
          <section className="tm-glass-card rounded-xl p-6">
            <h2 className="phi-subtitle font-cinzel text-tm-text mb-6">
              Tendances
            </h2>
            
            <TabGroup onChange={(index) => {
              const categoryKey = categories[index].key;
              setSelectedCategory(categoryKey);
            }}>
              <div className="flex justify-between items-center mb-6">
                <TabList className="flex gap-2 flex-wrap">
                  {categories.map((category) => (
                    <Tab
                      key={category.key}
                      className={({ selected, hover, focus }) =>
                        clsx(
                          "relative rounded-full px-6 py-3 text-sm font-semibold transition-all duration-300 focus:outline-none",
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
                              "underline decoration-tm-primary decoration-2 underline-offset-4": selected
                            }
                          )}>
                            {category.label}
                          </span>
                        </>
                      )}
                    </Tab>
                  ))}
                </TabList>
                
                {trending.length > 0 && (
                  <span className="flex items-center justify-center w-8 h-8 text-sm font-semibold text-tm-text-muted bg-white/10 rounded-full">
                    {trending.length}
                  </span>
                )}
              </div>
              
              <TabPanels>
                {categories.map((category) => (
                  <TabPanel key={category.key}>
                    {error && (
                      <div className="tm-glass border border-red-400/40 text-red-400 p-4 rounded-xl text-sm text-center mb-6" style={{
                        boxShadow: 'inset 0 1px 0 rgba(255, 255, 255, 0.15), 0 4px 12px rgba(239, 68, 68, 0.15)'
                      }}>
                        {error}
                      </div>
                    )}
                    
                    <div className="overflow-x-auto scrollbar-hide">
                      <div className="flex gap-6 pb-4" style={{ width: 'max-content' }}>
                        {loading ? (
                          Array.from({ length: 8 }).map((_, idx) => (
                            <div key={idx} className="tm-glass rounded-xl overflow-hidden flex-shrink-0 w-64 h-96">
                              <div className="aspect-[3/4] bg-white/10 animate-pulse"></div>
                              <div className="p-4 space-y-3">
                                <div className="h-4 bg-white/10 rounded animate-pulse"></div>
                                <div className="h-3 bg-white/5 rounded animate-pulse"></div>
                                <div className="h-8 bg-white/10 rounded animate-pulse"></div>
                              </div>
                            </div>
                          ))
                        ) : (
                          trending
                            .filter((item) => item.external_id && item.title) // Filtrer les items invalides
                            .map((item, index) => (
                            <div 
                              key={`${item.source}-${item.external_id}-${index}`} 
                              className="tm-glass rounded-xl overflow-hidden group hover:scale-[1.02] transition-all duration-300 flex flex-col flex-shrink-0 w-64 h-96"
                              style={{
                                boxShadow: 'inset 0 1px 0 rgba(255, 255, 255, 0.15), 0 4px 12px rgba(255, 255, 255, 0.05)'
                              }}
                            >
                              <div className="aspect-[3/4] relative overflow-hidden">
                                <img
                                  src={item.poster_url || '/vite.svg'}
                                  alt={`${item.category === 'LIVRES' ? 'Couverture de' : 'Poster for'} ${item.title}`}
                                  className="w-full h-full object-cover transition-transform duration-300 group-hover:scale-105"
                                  onError={(e: React.SyntheticEvent<HTMLImageElement>) => { 
                                    e.currentTarget.src = '/vite.svg'; 
                                  }}
                                />
                                <div className="absolute inset-0 bg-gradient-to-t from-black/60 via-transparent to-transparent" />
                                <div className="absolute top-3 left-3 flex gap-2">
                                  <span className="px-2 py-1 text-xs font-semibold bg-tm-primary text-white rounded-full">
                                    {item.category_display}
                                  </span>
                                  <span className="px-2 py-1 text-xs font-semibold bg-white/20 text-white rounded-full backdrop-blur-sm">
                                    {(item.source || '').toUpperCase()}
                                  </span>
                                </div>
                              </div>
                              
                              <div className="p-4 flex flex-col flex-grow">
                                <h3 className="font-bold text-sm text-white mb-2 line-clamp-2">
                                  {item.title}
                                </h3>
                                {item.description && (
                                  <p className="text-xs text-tm-text-muted line-clamp-3 mb-4 flex-grow">
                                    {item.description}
                                  </p>
                                )}
                                
                                <div className="flex gap-2 mt-auto">
                                  <button 
                                    className="flex-1 flex items-center justify-center p-2 bg-red-500/20 hover:bg-red-500/30 text-red-400 rounded-lg transition-colors duration-200"
                                    onClick={() => {/* TODO: Handle dislike */}}
                                  >
                                    <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                                    </svg>
                                  </button>
                                  <button 
                                    className="flex-1 flex items-center justify-center p-2 bg-green-500/20 hover:bg-green-500/30 text-green-400 rounded-lg transition-colors duration-200"
                                    onClick={() => handleAddFromTrending(item)}
                                  >
                                    <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
                                    </svg>
                                  </button>
                                </div>
                              </div>
                            </div>
                          ))
                        )}
                      </div>
                    </div>
                    
                    {!loading && trending.length === 0 && !error && (
                      <div className="tm-glass rounded-xl p-8 text-center" style={{
                        boxShadow: 'inset 0 1px 0 rgba(255, 255, 255, 0.15), 0 4px 12px rgba(255, 255, 255, 0.05)'
                      }}>
                        <div className="text-4xl mb-4">🔍</div>
                        <p className="text-tm-text-muted">
                          Aucune tendance trouvée pour cette catégorie
                        </p>
                      </div>
                    )}
                  </TabPanel>
                ))}
              </TabPanels>
            </TabGroup>
          </section>

          {/* Section Recommandations */}
          <section className="tm-glass-card rounded-xl p-6">
            <h2 className="phi-subtitle font-cinzel text-tm-text mb-6">
              Recommandé pour vous
            </h2>
            <div className="tm-glass rounded-xl p-8 text-center" style={{
              boxShadow: 'inset 0 1px 0 rgba(255, 255, 255, 0.15), 0 4px 12px rgba(255, 255, 255, 0.05)'
            }}>
              <div className="text-4xl mb-4">🎯</div>
              <p className="text-tm-text-muted mb-4 leading-relaxed">
                Créez des listes et likez du contenu pour recevoir des recommandations personnalisées !
              </p>
              <button 
                onClick={() => onNavigate?.('ajout')}
                className="tm-glass-button phi-button inline-flex items-center justify-center gap-2 rounded-xl focus:outline-none focus:ring-2 focus:ring-white/50"
              >
                <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
                </svg>
                Commencer maintenant
              </button>
            </div>
          </section>

        </div>
      </div>

      <AppBottomNav value={bottomNavValue} onChange={handleBottomNavChange} />
    </div>
  );
};

export default ExplorePage;
