import React, { useState, useEffect } from 'react';
import {
  AppBar,
  Toolbar,
  Typography,
  IconButton,
  Box,
  Container,
  Paper,
  List,
  ListItem,
  ListItemText,
  ListItemSecondaryAction,
  IconButton as MuiIconButton,
  BottomNavigation,
  BottomNavigationAction,
  TextField,
  Button
} from '@mui/material';
import {
  Notifications as NotificationsIcon,
  AccountCircle as AccountCircleIcon,
  Home as HomeIcon,
  Explore as ExploreIcon,
  Favorite as FavoriteIcon,
  List as ListIcon,
  Add as AddIcon,
  ArrowBack as ArrowBackIcon,
  Edit as EditIcon,
  Delete as DeleteIcon
} from '@mui/icons-material';

interface DashboardProps {
  onNavigate?: (section: string) => void;
  listId?: number;
}

interface TasteList {
  id: number;
  name: string;
  description: string;
  owner: string;
  created_at: string;
  updated_at: string;
}

const Dashboard: React.FC<DashboardProps> = ({ onNavigate, listId = 1 }) => {
  const [bottomNavValue, setBottomNavValue] = useState(0);
  const [list, setList] = useState<TasteList | null>(null);
  const [isEditingTitle, setIsEditingTitle] = useState(false);
  const [isEditingDescription, setIsEditingDescription] = useState(false);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  const movies = [
    'Blade Runner 2049',
    'Dune (2021)',
    'Arrival',
    'Interstellar',
    'The Martian'
  ];

  // Récupérer les détails de la liste
  useEffect(() => {
    const fetchList = async () => {
      try {
        const token = localStorage.getItem('access_token');
        const response = await fetch(`http://localhost:8000/api/lists/${listId}/`, {
          headers: {
            'Authorization': `Bearer ${token}`
          }
        });

        if (response.ok) {
          const data = await response.json();
          setList(data);
        } else {
          // Si la liste n'existe pas, utiliser des données par défaut
          setList({
            id: listId,
            name: 'Mes 10 films de SF préférés',
            description: 'Une collection des meilleurs films de SF modernes.',
            owner: 'demo',
            created_at: new Date().toISOString(),
            updated_at: new Date().toISOString()
          });
        }
      } catch (err) {
        console.error('Erreur lors du chargement de la liste:', err);
        setError('Erreur lors du chargement de la liste');
        // Utiliser des données par défaut en cas d'erreur
        setList({
          id: listId,
          name: 'Mes 10 films de SF préférés',
          description: 'Une collection des meilleurs films de SF modernes.',
          owner: 'demo',
          created_at: new Date().toISOString(),
          updated_at: new Date().toISOString()
        });
      } finally {
        setLoading(false);
      }
    };

    fetchList();
  }, [listId]);

  const handleBottomNavChange = (event: React.SyntheticEvent, newValue: number) => {
    setBottomNavValue(newValue);
    const sections = ['accueil', 'decouvrir', 'match', 'listes', 'ajout'];
    onNavigate?.(sections[newValue]);
  };

  const handleDeleteMovie = (index: number) => {
    // TODO: Implémenter la suppression
    console.log(`Supprimer le film à l'index ${index}`);
  };

  const handleAddMovie = () => {
    // TODO: Implémenter l'ajout
    console.log('Ajouter un nouveau film');
  };

  return (
    <Box sx={{ display: 'flex', flexDirection: 'column', height: '100vh' }}>
      {/* Header */}
      <AppBar position="static" sx={{ backgroundColor: '#1976d2' }}>
        <Toolbar>
          <Typography variant="h6" component="div" sx={{ flexGrow: 1 }}>
            Taste Match
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
      <Container sx={{ flexGrow: 1, py: 2, overflow: 'auto' }}>
        <Paper elevation={2} sx={{ p: 3, mb: 2 }}>
          {/* Navigation retour */}
          <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
            <IconButton size="small" sx={{ mr: 1 }} aria-label="retour">
              <ArrowBackIcon />
            </IconButton>
            <Typography variant="body2" color="text.secondary">
              Retour au Dashboard
            </Typography>
          </Box>

          {/* Titre de la liste */}
          <Box sx={{ mb: 2 }}>
            {loading ? (
              <Typography variant="h4" component="h1">Chargement...</Typography>
            ) : isEditingTitle ? (
              <TextField
                fullWidth
                value={list?.name || ''}
                onChange={(e) => setList(list ? { ...list, name: e.target.value } : null)}
                onBlur={() => setIsEditingTitle(false)}
                onKeyPress={(e) => {
                  if (e.key === 'Enter') {
                    setIsEditingTitle(false);
                  }
                }}
                variant="standard"
                sx={{ '& .MuiInputBase-input': { fontSize: '1.5rem', fontWeight: 'bold' } }}
                autoFocus
              />
            ) : (
              <Box sx={{ display: 'flex', alignItems: 'center' }}>
                <Typography variant="h4" component="h1" sx={{ flexGrow: 1 }}>
                  {list?.name || 'Mes 10 films de SF préférés'}
                </Typography>
                <IconButton 
                  size="small" 
                  onClick={() => setIsEditingTitle(true)}
                  aria-label="edit"
                >
                  <EditIcon />
                </IconButton>
              </Box>
            )}
          </Box>

          {/* Description */}
          <Box sx={{ mb: 3 }}>
            {loading ? (
              <Typography variant="body1" color="text.secondary">Chargement de la description...</Typography>
            ) : isEditingDescription ? (
              <TextField
                fullWidth
                value={list?.description || ''}
                onChange={(e) => setList(list ? { ...list, description: e.target.value } : null)}
                onBlur={() => setIsEditingDescription(false)}
                variant="standard"
                multiline
                autoFocus
              />
            ) : (
              <Box sx={{ display: 'flex', alignItems: 'flex-start' }}>
                <Typography variant="body1" color="text.secondary" sx={{ flexGrow: 1 }}>
                  {list?.description || 'Une collection des meilleurs films de SF modernes.'}
                </Typography>
                <IconButton 
                  size="small" 
                  onClick={() => setIsEditingDescription(true)}
                  aria-label="edit"
                >
                  <EditIcon />
                </IconButton>
              </Box>
            )}
          </Box>

          {/* Section Éléments */}
          <Typography variant="h6" sx={{ mb: 2 }}>
            Éléments de la liste :
          </Typography>
          <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
            ======================
          </Typography>

          {/* Liste des films */}
          <List>
            {movies.map((movie, index) => (
              <ListItem key={index} sx={{ px: 0 }}>
                <ListItemText
                  primary={`${index + 1}. ${movie}`}
                  sx={{ '& .MuiListItemText-primary': { fontWeight: 'medium' } }}
                />
                <ListItemSecondaryAction>
                  <MuiIconButton 
                    edge="end" 
                    size="small"
                    onClick={() => handleDeleteMovie(index)}
                    aria-label="supprimer"
                  >
                    <DeleteIcon />
                  </MuiIconButton>
                </ListItemSecondaryAction>
              </ListItem>
            ))}
          </List>

          {/* Bouton Ajouter */}
          <Box sx={{ mt: 2 }}>
            <Button
              variant="outlined"
              startIcon={<AddIcon />}
              onClick={handleAddMovie}
              sx={{ width: '100%', py: 1.5 }}
            >
              Ajouter un élément
            </Button>
          </Box>
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

      {/* Espace pour éviter que le contenu soit caché par la bottom navigation */}
      <Box sx={{ height: 56 }} />
    </Box>
  );
};

export default Dashboard; 