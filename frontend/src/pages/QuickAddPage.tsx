import React, { useState } from 'react';
import {
  AppBar,
  Toolbar,
  Typography,
  IconButton,
  Box,
  Container,
  Paper,
  Select,
  MenuItem,
  FormControl,
  InputLabel,
  BottomNavigation,
  BottomNavigationAction,
  Alert,
  Snackbar,
  Tab,
  Tabs
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
  LibraryMusic as MusicIcon,
  MenuBook as BookIcon,
  Tv as TvIcon,
  Search as SearchIcon
} from '@mui/icons-material';
import SearchBar from '../components/SearchBar';
import SuggestionCards from '../components/SuggestionCards';

interface QuickAddPageProps {
  onNavigate?: (section: string) => void;
}

const QuickAddPage: React.FC<QuickAddPageProps> = ({ onNavigate }) => {
  const [bottomNavValue, setBottomNavValue] = useState(4); // "Ajout rapide" selected
  const [selectedCategory, setSelectedCategory] = useState<string>('ALL');
  const [tabValue, setTabValue] = useState(0);
  const [successMessage, setSuccessMessage] = useState('');
  const [errorMessage, setErrorMessage] = useState('');
  const [snackbarOpen, setSnackbarOpen] = useState(false);

  const handleBottomNavChange = (event: React.SyntheticEvent, newValue: number) => {
    setBottomNavValue(newValue);
    const sections = ['accueil', 'decouvrir', 'match', 'listes', 'ajout'];
    onNavigate?.(sections[newValue]);
  };

  const categories = [
    { value: 'ALL', label: 'Toutes catégories', icon: <AddIcon />, color: '#9c27b0' },
    { value: 'FILMS', label: 'Films', icon: <MovieIcon />, color: '#e53e3e' },
    { value: 'SERIES', label: 'Séries', icon: <TvIcon />, color: '#3182ce' },
    { value: 'MUSIQUE', label: 'Musique', icon: <MusicIcon />, color: '#38a169' },
    { value: 'LIVRES', label: 'Livres', icon: <BookIcon />, color: '#d69e2e' }
  ];

  interface SearchResult {
    title: string;
    description: string;
    category: string;
    category_display: string;
    popularity: number;
  }

  interface Suggestion {
    title: string;
    description: string;
    category: string;
    category_display: string;
    popularity: number;
    type: 'popular' | 'suggestion';
  }

  const quickAddItem = async (title: string, description: string, category: string) => {
    try {
      const token = localStorage.getItem('access_token');
      const response = await fetch('http://localhost:8000/api/quick-add/', {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({ title, description, category })
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.error || 'Erreur lors de l\'ajout');
      }

      const data = await response.json();
      setSuccessMessage(data.message);
      setSnackbarOpen(true);
      return data;
    } catch (error: unknown) {
      const message = error instanceof Error ? error.message : 'Erreur inconnue';
      setErrorMessage(message);
      setSnackbarOpen(true);
      throw error;
    }
  };

  const handleSearchSelect = async (result: SearchResult) => {
    await quickAddItem(result.title, result.description, result.category);
  };

  const handleSuggestionAdd = async (suggestion: Suggestion) => {
    await quickAddItem(suggestion.title, suggestion.description, suggestion.category);
  };

  const handleTabChange = (event: React.SyntheticEvent, newValue: number) => {
    setTabValue(newValue);
  };

  const handleCategoryChange = (event: React.ChangeEvent<{ value: unknown }>) => {
    setSelectedCategory(event.target.value as string);
  };

  const getSelectedCategoryConfig = () => {
    return categories.find(cat => cat.value === selectedCategory) || categories[0];
  };

  const handleCloseSnackbar = () => {
    setSnackbarOpen(false);
    setSuccessMessage('');
    setErrorMessage('');
  };

  return (
    <Box sx={{ display: 'flex', flexDirection: 'column', height: '100vh' }}>
      {/* Header */}
      <AppBar position="static" sx={{ backgroundColor: '#4caf50' }}>
        <Toolbar>
          <Typography variant="h6" component="div" sx={{ flexGrow: 1 }}>
            Ajout Rapide
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
          {/* Filtre par catégorie */}
          <Box sx={{ mb: { xs: 2, sm: 3 } }}>
            <Typography 
              variant="h4" 
              component="h1" 
              gutterBottom
              sx={{ 
                fontSize: { xs: '1.5rem', sm: '2.125rem' },
                fontWeight: 'bold',
                mb: 2
              }}
            >
              Ajout Rapide
            </Typography>
            
            <FormControl 
              fullWidth 
              sx={{ 
                mb: 2,
                '& .MuiInputBase-input': {
                  fontSize: { xs: '0.875rem', sm: '1rem' }
                }
              }}
            >
              <InputLabel>Filtrer par catégorie</InputLabel>
              <Select
                value={selectedCategory}
                onChange={handleCategoryChange}
                label="Filtrer par catégorie"
              >
                {categories.map((category) => (
                  <MenuItem key={category.value} value={category.value}>
                    <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                      <Box 
                        sx={{ 
                          color: category.color,
                          display: 'flex', 
                          alignItems: 'center' 
                        }}
                      >
                        {category.icon}
                      </Box>
                      {category.label}
                    </Box>
                  </MenuItem>
                ))}
              </Select>
            </FormControl>
          </Box>

          {/* Onglets */}
          <Box sx={{ borderBottom: 1, borderColor: 'divider', mb: 3 }}>
            <Tabs 
              value={tabValue} 
              onChange={handleTabChange} 
              variant="fullWidth"
              sx={{
                '& .MuiTab-root': {
                  fontSize: { xs: '0.75rem', sm: '0.875rem' },
                  minHeight: { xs: 40, sm: 48 }
                }
              }}
            >
              <Tab 
                icon={<SearchIcon />} 
                label="Rechercher" 
                iconPosition="start"
              />
              <Tab 
                icon={<AddIcon />} 
                label="Suggestions" 
                iconPosition="start"
              />
            </Tabs>
          </Box>

          {/* Contenu des onglets */}
          {tabValue === 0 && (
            <Box>
              <Typography 
                variant="h6" 
                sx={{ 
                  mb: 2,
                  fontSize: { xs: '1rem', sm: '1.25rem' },
                  fontWeight: 'medium'
                }}
              >
                Rechercher et Ajouter
              </Typography>
              <Typography 
                variant="body2" 
                color="text.secondary" 
                sx={{ 
                  mb: 3,
                  fontSize: { xs: '0.75rem', sm: '0.875rem' }
                }}
              >
                Tapez pour rechercher dans la base de données ou ajouter directement à vos listes
              </Typography>
              <SearchBar
                category={selectedCategory === 'ALL' ? undefined : selectedCategory}
                onSelect={handleSearchSelect}
                onQuickAdd={handleSearchSelect}
                placeholder={`Rechercher ${selectedCategory === 'ALL' ? 'dans toutes les catégories' : 'des ' + getSelectedCategoryConfig().label.toLowerCase()}...`}
                autoFocus
              />
            </Box>
          )}

          {tabValue === 1 && (
            <Box>
              <SuggestionCards
                category={selectedCategory === 'ALL' ? undefined : selectedCategory}
                onAdd={handleSuggestionAdd}
                title={`Suggestions ${selectedCategory === 'ALL' ? 'Populaires' : getSelectedCategoryConfig().label}`}
                limit={6}
              />
            </Box>
          )}
        </Paper>
      </Container>

      {/* Snackbar pour les messages */}
      <Snackbar
        open={snackbarOpen}
        autoHideDuration={4000}
        onClose={handleCloseSnackbar}
        anchorOrigin={{ vertical: 'top', horizontal: 'center' }}
      >
        <Alert 
          onClose={handleCloseSnackbar} 
          severity={successMessage ? 'success' : 'error'}
          sx={{ width: '100%' }}
        >
          {successMessage || errorMessage}
        </Alert>
      </Snackbar>

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

export default QuickAddPage;