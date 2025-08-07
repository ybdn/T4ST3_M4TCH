import React, { useState, useEffect } from 'react';
import {
  AppBar,
  Toolbar,
  Typography,
  IconButton,
  Box,
  Container,
  Paper,
  BottomNavigation,
  BottomNavigationAction,
  Card,
  CardContent,
  CardActionArea,
  Alert,
  CircularProgress,
  Grid
} from '@mui/material';
import {
  Notifications as NotificationsIcon,
  AccountCircle as AccountCircleIcon,
  Home as HomeIcon,
  Explore as ExploreIcon,
  Favorite as FavoriteIcon,
  List as ListIcon,
  Add as AddIcon,
  Movie as MovieIcon,
  Tv as TvIcon,
  MusicNote as MusicIcon,
  MenuBook as BookIcon
} from '@mui/icons-material';
import { useAuth } from '../context/AuthContext';

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
  onNavigate?: (section: string) => void;
}

const ListsPage: React.FC<ListsPageProps> = ({ onNavigate }) => {
  const [categories, setCategories] = useState<Record<string, CategoryData>>({});
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [bottomNavValue, setBottomNavValue] = useState(3); // "Mes listes" selected
  // eslint-disable-next-line @typescript-eslint/no-unused-vars
  const { user } = useAuth();

  const handleBottomNavChange = (event: React.SyntheticEvent, newValue: number) => {
    setBottomNavValue(newValue);
    const sections = ['accueil', 'decouvrir', 'match', 'listes', 'ajout'];
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
    // TODO: Navigation vers Dashboard avec l'ID de la liste
    console.log(`Navigate to Dashboard for list ${listId} (${category})`);
  };

  // Configuration des icônes et couleurs par catégorie
  const getCategoryConfig = (category: string) => {
    const configs = {
      'FILMS': { icon: MovieIcon, color: '#e53e3e', bgColor: '#fef2f2' },
      'SERIES': { icon: TvIcon, color: '#3182ce', bgColor: '#ebf8ff' },
      'MUSIQUE': { icon: MusicIcon, color: '#38a169', bgColor: '#f0fff4' },
      'LIVRES': { icon: BookIcon, color: '#d69e2e', bgColor: '#fffaf0' }
    };
    return configs[category as keyof typeof configs] || { icon: ListIcon, color: '#718096', bgColor: '#f7fafc' };
  };


  return (
    <Box sx={{ display: 'flex', flexDirection: 'column', minHeight: '100vh' }}>
      {/* Header */}
      <AppBar position="static" sx={{ backgroundColor: '#1976d2' }}>
        <Toolbar>
          <Typography variant="h6" component="div" sx={{ flexGrow: 1 }}>
            Mes Collections
          </Typography>
          <IconButton color="inherit" size="large" aria-label="notifications">
            <NotificationsIcon />
          </IconButton>
          <IconButton color="inherit" size="large" aria-label="profile">
            <AccountCircleIcon />
          </IconButton>
        </Toolbar>
      </AppBar>

      {/* Contenu principal */}
      <Container 
        maxWidth="sm" 
        sx={{ 
          flexGrow: 1, 
          py: 1, 
          px: 2, 
          overflow: 'auto',
          pb: 9 // Espace pour la bottom navigation
        }}
      >
        <Paper elevation={2} sx={{ p: { xs: 2, sm: 3 }, mb: 2 }}>
          <Box sx={{ mb: { xs: 2, sm: 3 } }}>
            <Typography 
              variant="h4" 
              component="h1" 
              gutterBottom
              sx={{ 
                fontSize: { xs: '1.5rem', sm: '2.125rem' },
                fontWeight: 'bold'
              }}
            >
              Mes Collections
            </Typography>
            <Typography 
              variant="body1" 
              color="text.secondary"
              sx={{ fontSize: { xs: '0.875rem', sm: '1rem' } }}
            >
              Gérez vos goûts en films, séries, musique et livres
            </Typography>
          </Box>

          {error && (
            <Alert severity="error" sx={{ mb: 2 }} onClose={() => setError('')}>
              {error}
            </Alert>
          )}

          {loading ? (
            <Box sx={{ display: 'flex', justifyContent: 'center', py: 4 }}>
              <CircularProgress />
            </Box>
          ) : (
            <Grid container spacing={2}>
              {Object.entries(categories).map(([categoryKey, categoryData]) => {
                const config = getCategoryConfig(categoryKey);
                const IconComponent = config.icon;
                const list = categoryData.list;
                
                return (
                  <Grid item xs={6} sm={6} key={categoryKey}>
                    <Card 
                      sx={{ 
                        height: '100%',
                        transition: 'transform 0.2s, box-shadow 0.2s',
                        '&:hover': {
                          transform: 'translateY(-4px)',
                          boxShadow: 6
                        }
                      }}
                    >
                      <CardActionArea
                        sx={{ height: '100%' }}
                        onClick={() => list && handleCategoryClick(list.id, categoryKey)}
                      >
                        <CardContent sx={{ p: { xs: 2, sm: 3 }, backgroundColor: config.bgColor }}>
                          {/* Mobile: Layout vertical, Desktop: Layout horizontal */}
                          <Box sx={{ 
                            display: 'flex', 
                            flexDirection: { xs: 'column', sm: 'row' },
                            alignItems: { xs: 'center', sm: 'flex-start' },
                            mb: 2 
                          }}>
                            <Box
                              sx={{
                                width: { xs: 40, sm: 48 },
                                height: { xs: 40, sm: 48 },
                                borderRadius: '50%',
                                backgroundColor: config.color,
                                display: 'flex',
                                alignItems: 'center',
                                justifyContent: 'center',
                                mr: { xs: 0, sm: 2 },
                                mb: { xs: 1, sm: 0 }
                              }}
                            >
                              <IconComponent sx={{ color: 'white', fontSize: { xs: 20, sm: 24 } }} />
                            </Box>
                            <Typography 
                              variant="h6" 
                              component="h2" 
                              color={config.color}
                              sx={{ 
                                fontSize: { xs: '0.9rem', sm: '1.25rem' },
                                textAlign: { xs: 'center', sm: 'left' },
                                fontWeight: 'medium'
                              }}
                            >
                              {categoryData.category_label}
                            </Typography>
                          </Box>
                          
                          <Typography 
                            variant="h4" 
                            sx={{ 
                              mb: 1, 
                              color: config.color, 
                              fontWeight: 'bold',
                              fontSize: { xs: '1.5rem', sm: '2.125rem' },
                              textAlign: { xs: 'center', sm: 'left' }
                            }}
                          >
                            {list?.items_count || 0}
                          </Typography>
                          
                          <Typography 
                            variant="body2" 
                            color="text.secondary" 
                            sx={{ 
                              mb: { xs: 1, sm: 2 },
                              fontSize: { xs: '0.75rem', sm: '0.875rem' },
                              textAlign: { xs: 'center', sm: 'left' }
                            }}
                          >
                            {list?.items_count === 0 
                              ? 'Aucun élément'
                              : list?.items_count === 1 
                                ? '1 élément' 
                                : `${list.items_count} éléments`
                            }
                          </Typography>

                          <Typography 
                            variant="body2" 
                            sx={{ 
                              fontStyle: 'italic', 
                              color: 'text.secondary',
                              fontSize: { xs: '0.7rem', sm: '0.875rem' },
                              textAlign: { xs: 'center', sm: 'left' },
                              display: { xs: 'none', sm: 'block' } // Masquer sur mobile pour économiser l'espace
                            }}
                          >
                            {list?.description || 'Cliquez pour gérer cette collection'}
                          </Typography>
                        </CardContent>
                      </CardActionArea>
                    </Card>
                  </Grid>
                );
              })}
            </Grid>
          )}
        </Paper>
      </Container>

      {/* Bottom Navigation */}
      <Paper sx={{ position: 'fixed', bottom: 0, left: 0, right: 0 }} elevation={3}>
        <BottomNavigation
          value={bottomNavValue}
          onChange={handleBottomNavChange}
          showLabels
        >
          <BottomNavigationAction label="Accueil" icon={<HomeIcon />} />
          <BottomNavigationAction label="Découvrir" icon={<ExploreIcon />} />
          <BottomNavigationAction label="MATCH !" icon={<FavoriteIcon />} />
          <BottomNavigationAction label="Mes listes" icon={<ListIcon />} />
          <BottomNavigationAction label="Ajout rapide" icon={<AddIcon />} />
        </BottomNavigation>
      </Paper>

    </Box>
  );
};

export default ListsPage;