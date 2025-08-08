import React, { useState, useEffect } from 'react';
import { FilmIcon, SeriesIcon, MusicIcon, BookIcon } from '../components/icons';
import { useAuth } from '../context/AuthContext.tsx';
import AppHeader from '../components/AppHeader';
import AppBottomNav from '../components/AppBottomNav';

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

interface ListsPageProps {
  onNavigate?: (section: string, params?: any) => void;
}

const ListsPage: React.FC<ListsPageProps> = ({ onNavigate }) => {
  const [categories, setCategories] = useState<Record<string, CategoryData>>({});
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [bottomNavValue, setBottomNavValue] = useState(3); // "Mes listes" selected
  const [selectedListId, setSelectedListId] = useState<number | null>(null);
  const { user } = useAuth();

  const handleBottomNavChange = (event: React.SyntheticEvent, newValue: number) => {
    setBottomNavValue(newValue);
    const sections = ['accueil', 'decouvrir', 'match', 'listes', 'profil'];
    onNavigate?.(sections[newValue]);
  };

  // Fonction pour récupérer les listes par catégorie
  const fetchLists = async () => {
    try {
      const token = localStorage.getItem('access_token');
      const response = await fetch('http://localhost:8000/api/lists/by_category/', {
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

  useEffect(() => {
    fetchLists();
  }, []);

  // Fonction pour naviguer vers le Dashboard d'une catégorie
  const handleCategoryClick = (listId: number, category: string) => {
    setSelectedListId(listId);
    // Naviguer vers le Dashboard avec l'ID de la liste
    onNavigate?.('dashboard', { listId });
  };

  const getCategoryConfig = (category: string) => {
    const configs = {
      'FILMS': {
        icon: FilmIcon,
        color: '#ffffff'
      },
      'SERIES': {
        icon: SeriesIcon,
        color: '#ffffff'
      },
      'MUSIQUE': {
        icon: MusicIcon,
        color: '#ffffff'
      },
      'LIVRES': {
        icon: BookIcon,
        color: '#ffffff'
      }
    };
    return configs[category as keyof typeof configs] || configs['FILMS'];
  };

  return (
    <div className="flex flex-col h-screen">
      <AppHeader title="T4ST3 M4TCH" />

      {/* Contenu principal */}
      <div className="flex-1 overflow-auto">
        <div className="max-w-4xl mx-auto py-6 px-4 sm:py-8 sm:px-6">
          {/* Header épuré */}
          <div className="mb-12">
            <h1 className="text-3xl sm:text-5xl font-bold text-tm-text mb-2">
              Mes listes
            </h1>
            <p className="text-base text-tm-text-muted leading-relaxed">
              Gérez vos listes culturelles
            </p>
          </div>

          {error && (
            <div className="mb-8 p-4 bg-red-900/20 border border-red-800 text-red-300 rounded-none">
              {error}
            </div>
          )}

          {loading ? (
            <div className="flex justify-center py-16">
              <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-tm-accent"></div>
            </div>
          ) : (
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-6">
              {Object.entries(categories).map(([categoryKey, categoryData]) => {
                const config = getCategoryConfig(categoryKey);
                const IconComponent = config.icon;
                const list = categoryData.list;
                
                return (
                  <button
                    key={categoryKey}
                    onClick={() => list && handleCategoryClick(list.id, categoryKey)}
                    className="tm-card p-6 text-left hover:bg-tm-bg-elevated transition-colors cursor-pointer"
                  >
                    {/* Header avec icône et titre */}
                    <div className="flex items-center mb-6">
                      <IconComponent size={32} color="#e7e9ea" />
                      <h2 className="ml-3 text-lg font-semibold text-tm-text">
                        {categoryData.category_label}
                      </h2>
                    </div>
                    
                    {/* Statistiques */}
                    <div className="mb-4">
                      <div className="text-3xl font-bold mb-1" style={{ color: config.color }}>
                        {list?.items_count || 0}
                      </div>
                      
                      <div className="text-sm text-tm-text-muted">
                        {list?.items_count === 0 
                          ? 'Aucun élément'
                          : list?.items_count === 1 
                            ? '1 élément' 
                            : `${list?.items_count} éléments`
                        }
                      </div>
                    </div>

                    {/* Description */}
                    <p className="text-sm text-tm-text-muted leading-relaxed">
                      {list?.description || 'Cliquez pour gérer cette collection'}
                    </p>
                  </button>
                );
              })}
            </div>
          )}
        </div>
      </div>

      <AppBottomNav value={bottomNavValue} onChange={handleBottomNavChange} />

      {/* Espace pour éviter que le contenu soit caché par la bottom navigation */}
      <div className="h-14"></div>
    </div>
  );
};

export default ListsPage;