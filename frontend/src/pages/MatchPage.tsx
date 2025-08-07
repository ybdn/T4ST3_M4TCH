import React, { useState } from 'react';
import {
  AppBar,
  Toolbar,
  Typography,
  IconButton,
  Box,
  Container,
  Paper,
  Button,
  Card,
  CardContent,
  LinearProgress,
  BottomNavigation,
  BottomNavigationAction,
  Avatar,
  Chip
} from '@mui/material';
import {
  Notifications as NotificationsIcon,
  AccountCircle as AccountCircleIcon,
  Home as HomeIcon,
  Explore as ExploreIcon,
  Favorite as FavoriteIcon,
  List as ListIcon,
  Add as AddIcon,
  ThumbUp as ThumbUpIcon,
  ThumbDown as ThumbDownIcon,
  Refresh as RefreshIcon
} from '@mui/icons-material';

interface MatchPageProps {
  onNavigate?: (section: string) => void;
}

const MatchPage: React.FC<MatchPageProps> = ({ onNavigate }) => {
  const [bottomNavValue, setBottomNavValue] = useState(2); // "MATCH !" selected
  const [currentMatch, setCurrentMatch] = useState(0);
  const [matches, setMatches] = useState([
    {
      id: 1,
      title: "Blade Runner 2049",
      category: "Film",
      description: "Chef-d'œuvre de science-fiction de Denis Villeneuve",
      compatibilityScore: 92,
      commonFriends: ["Alice", "Bob"],
      reasons: ["Sci-fi", "Visuel époustouflant", "Histoire profonde"]
    },
    {
      id: 2, 
      title: "Radiohead",
      category: "Musique",
      description: "Groupe de rock alternatif britannique",
      compatibilityScore: 87,
      commonFriends: ["Charlie", "David"],
      reasons: ["Rock alternatif", "Expérimental", "OK Computer"]
    },
    {
      id: 3,
      title: "1984",
      category: "Livre", 
      description: "Roman dystopique de George Orwell",
      compatibilityScore: 95,
      commonFriends: ["Eve", "Frank", "Grace"],
      reasons: ["Dystopie", "Politique", "Classique"]
    }
  ]);

  const handleBottomNavChange = (event: React.SyntheticEvent, newValue: number) => {
    setBottomNavValue(newValue);
    const sections = ['accueil', 'decouvrir', 'match', 'listes', 'ajout'];
    onNavigate?.(sections[newValue]);
  };

  const handleLike = () => {
    console.log(`J'aime: ${matches[currentMatch].title}`);
    nextMatch();
  };

  const handleDislike = () => {
    console.log(`Je n'aime pas: ${matches[currentMatch].title}`);
    nextMatch();
  };

  const nextMatch = () => {
    if (currentMatch < matches.length - 1) {
      setCurrentMatch(currentMatch + 1);
    } else {
      // Remettre à zéro ou charger de nouveaux matches
      setCurrentMatch(0);
    }
  };

  const currentItem = matches[currentMatch];

  return (
    <Box sx={{ display: 'flex', flexDirection: 'column', height: '100vh' }}>
      {/* Header */}
      <AppBar position="static" sx={{ backgroundColor: '#dc004e' }}>
        <Toolbar>
          <Typography variant="h6" component="div" sx={{ flexGrow: 1 }}>
            MATCH !
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
      <Container sx={{ flexGrow: 1, py: 2, overflow: 'auto', display: 'flex', flexDirection: 'column' }}>
        {/* Barre de progression */}
        <Box sx={{ mb: 2 }}>
          <Typography variant="body2" color="text.secondary" gutterBottom>
            Match {currentMatch + 1} sur {matches.length}
          </Typography>
          <LinearProgress 
            variant="determinate" 
            value={((currentMatch + 1) / matches.length) * 100} 
            sx={{ height: 8, borderRadius: 4 }}
          />
        </Box>

        {/* Carte de match principale */}
        <Box sx={{ flexGrow: 1, display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
          <Card sx={{ 
            width: '100%', 
            maxWidth: 400, 
            minHeight: 500,
            display: 'flex',
            flexDirection: 'column',
            boxShadow: 4
          }}>
            <CardContent sx={{ flexGrow: 1, textAlign: 'center', p: 3 }}>
              {/* Score de compatibilité */}
              <Box sx={{ mb: 2 }}>
                <Typography variant="h3" component="div" color="primary" fontWeight="bold">
                  {currentItem.compatibilityScore}%
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  Compatibilité
                </Typography>
              </Box>

              {/* Catégorie */}
              <Chip 
                label={currentItem.category} 
                color="secondary" 
                sx={{ mb: 2 }}
              />

              {/* Titre */}
              <Typography variant="h4" component="h1" gutterBottom>
                {currentItem.title}
              </Typography>

              {/* Description */}
              <Typography variant="body1" color="text.secondary" sx={{ mb: 3 }}>
                {currentItem.description}
              </Typography>

              {/* Raisons du match */}
              <Box sx={{ mb: 3 }}>
                <Typography variant="h6" gutterBottom>
                  Pourquoi ce match ?
                </Typography>
                <Box sx={{ display: 'flex', gap: 1, flexWrap: 'wrap', justifyContent: 'center' }}>
                  {currentItem.reasons.map((reason) => (
                    <Chip key={reason} label={reason} variant="outlined" size="small" />
                  ))}
                </Box>
              </Box>

              {/* Amis en commun */}
              <Box sx={{ mb: 3 }}>
                <Typography variant="body2" color="text.secondary" gutterBottom>
                  Aimé par vos amis :
                </Typography>
                <Box sx={{ display: 'flex', gap: 1, justifyContent: 'center' }}>
                  {currentItem.commonFriends.map((friend) => (
                    <Avatar key={friend} sx={{ width: 32, height: 32, fontSize: '0.8rem' }}>
                      {friend[0]}
                    </Avatar>
                  ))}
                </Box>
              </Box>
            </CardContent>

            {/* Actions */}
            <Box sx={{ p: 2, display: 'flex', gap: 2, justifyContent: 'center' }}>
              <Button
                variant="contained"
                color="error"
                size="large"
                startIcon={<ThumbDownIcon />}
                onClick={handleDislike}
                sx={{ minWidth: 120 }}
              >
                Non merci
              </Button>
              <Button
                variant="contained"
                color="success"
                size="large"
                startIcon={<ThumbUpIcon />}
                onClick={handleLike}
                sx={{ minWidth: 120 }}
              >
                J'adore !
              </Button>
            </Box>
          </Card>
        </Box>

        {/* Bouton pour relancer */}
        <Box sx={{ textAlign: 'center', mt: 2 }}>
          <Button
            variant="outlined"
            startIcon={<RefreshIcon />}
            onClick={() => setCurrentMatch(0)}
          >
            Recommencer les matchs
          </Button>
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

export default MatchPage;