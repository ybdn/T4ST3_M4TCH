import React, { useState } from 'react';
import {
  AppBar,
  Toolbar,
  Typography,
  IconButton,
  Box,
  Container,
  Paper,
  Card,
  CardContent,
  BottomNavigation,
  BottomNavigationAction
} from '@mui/material';
import {
  Notifications as NotificationsIcon,
  AccountCircle as AccountCircleIcon,
  Home as HomeIcon,
  Explore as ExploreIcon,
  Favorite as FavoriteIcon,
  List as ListIcon,
  Add as AddIcon,
  TrendingUp as TrendingUpIcon,
  Stars as StarsIcon,
  PlaylistAdd as PlaylistAddIcon
} from '@mui/icons-material';
import { useAuth } from '../context/AuthContext';

interface HomePageProps {
  onNavigate?: (section: string) => void;
}

const HomePage: React.FC<HomePageProps> = ({ onNavigate }) => {
  const [bottomNavValue, setBottomNavValue] = useState(0); // "Accueil" selected
  const { user } = useAuth();

  const handleBottomNavChange = (_event: React.SyntheticEvent, newValue: number) => {
    setBottomNavValue(newValue);
    const sections = ['accueil', 'decouvrir', 'match', 'listes', 'ajout'];
    onNavigate?.(sections[newValue]);
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
        <Box sx={{ mb: 3 }}>
          <Typography variant="h4" component="h1" gutterBottom>
            Bienvenue, {user?.username} !
          </Typography>
          <Typography variant="body1" color="text.secondary">
            Découvrez et partagez vos goûts culturels
          </Typography>
        </Box>

        <Box sx={{ display: 'flex', flexDirection: 'column', gap: 3 }}>
          {/* Statistiques */}
          <Box sx={{ display: 'grid', gridTemplateColumns: { xs: '1fr', sm: 'repeat(2, 1fr)', md: 'repeat(4, 1fr)' }, gap: 2 }}>
            <Card>
              <CardContent sx={{ textAlign: 'center' }}>
                <ListIcon sx={{ fontSize: 40, color: '#1976d2', mb: 1 }} />
                <Typography variant="h6" component="h2">
                  Mes Listes
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  3 listes créées
                </Typography>
              </CardContent>
            </Card>

            <Card>
              <CardContent sx={{ textAlign: 'center' }}>
                <FavoriteIcon sx={{ fontSize: 40, color: '#dc004e', mb: 1 }} />
                <Typography variant="h6" component="h2">
                  Matchs
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  12 compatibilités
                </Typography>
              </CardContent>
            </Card>

            <Card>
              <CardContent sx={{ textAlign: 'center' }}>
                <TrendingUpIcon sx={{ fontSize: 40, color: '#4caf50', mb: 1 }} />
                <Typography variant="h6" component="h2">
                  Tendances
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  Découvertes récentes
                </Typography>
              </CardContent>
            </Card>

            <Card>
              <CardContent sx={{ textAlign: 'center' }}>
                <StarsIcon sx={{ fontSize: 40, color: '#ff9800', mb: 1 }} />
                <Typography variant="h6" component="h2">
                  Favoris
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  25 éléments aimés
                </Typography>
              </CardContent>
            </Card>
          </Box>

          {/* Actions rapides */}
          <Paper sx={{ p: 3 }}>
            <Typography variant="h6" gutterBottom>
              Actions rapides
            </Typography>
            <Box sx={{ display: 'grid', gridTemplateColumns: { xs: '1fr', sm: 'repeat(2, 1fr)', md: 'repeat(4, 1fr)' }, gap: 2 }}>
              <Card sx={{ cursor: 'pointer', '&:hover': { bgcolor: 'action.hover' } }}>
                <CardContent sx={{ textAlign: 'center', py: 2 }}>
                  <PlaylistAddIcon sx={{ fontSize: 32, mb: 1 }} />
                  <Typography variant="body1">
                    Créer une liste
                  </Typography>
                </CardContent>
              </Card>
              <Card sx={{ cursor: 'pointer', '&:hover': { bgcolor: 'action.hover' } }}>
                <CardContent sx={{ textAlign: 'center', py: 2 }}>
                  <ExploreIcon sx={{ fontSize: 32, mb: 1 }} />
                  <Typography variant="body1">
                    Découvrir
                  </Typography>
                </CardContent>
              </Card>
              <Card sx={{ cursor: 'pointer', '&:hover': { bgcolor: 'action.hover' } }}>
                <CardContent sx={{ textAlign: 'center', py: 2 }}>
                  <FavoriteIcon sx={{ fontSize: 32, mb: 1 }} />
                  <Typography variant="body1">
                    Faire un match
                  </Typography>
                </CardContent>
              </Card>
              <Card sx={{ cursor: 'pointer', '&:hover': { bgcolor: 'action.hover' } }}>
                <CardContent sx={{ textAlign: 'center', py: 2 }}>
                  <AddIcon sx={{ fontSize: 32, mb: 1 }} />
                  <Typography variant="body1">
                    Ajout rapide
                  </Typography>
                </CardContent>
              </Card>
            </Box>
          </Paper>
        </Box>
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

export default HomePage;