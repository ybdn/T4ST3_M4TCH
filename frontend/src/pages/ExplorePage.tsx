import React, { useState } from 'react';
import {
  AppBar,
  Toolbar,
  Typography,
  IconButton,
  Box,
  Container,
  Paper,
  Grid,
  Card,
  CardContent,
  CardMedia,
  CardActions,
  Button,
  Chip,
  BottomNavigation,
  BottomNavigationAction,
  TextField,
  InputAdornment
} from '@mui/material';
import {
  Notifications as NotificationsIcon,
  AccountCircle as AccountCircleIcon,
  Home as HomeIcon,
  Explore as ExploreIcon,
  Favorite as FavoriteIcon,
  List as ListIcon,
  Add as AddIcon,
  Search as SearchIcon,
  ThumbUp as ThumbUpIcon,
  BookmarkAdd as BookmarkAddIcon
} from '@mui/icons-material';

interface ExplorePageProps {
  onNavigate?: (section: string) => void;
}

const ExplorePage: React.FC<ExplorePageProps> = ({ onNavigate }) => {
  const [bottomNavValue, setBottomNavValue] = useState(1); // "Découvrir" selected
  const [searchQuery, setSearchQuery] = useState('');

  const handleBottomNavChange = (event: React.SyntheticEvent, newValue: number) => {
    setBottomNavValue(newValue);
    const sections = ['accueil', 'decouvrir', 'match', 'listes', 'ajout'];
    onNavigate?.(sections[newValue]);
  };

  const trendingItems = [
    {
      id: 1,
      title: "Dune: Part Two",
      category: "Film",
      description: "Suite épique de l'adaptation de Frank Herbert",
      image: "/placeholder-movie.jpg",
      tags: ["Sci-Fi", "Épique", "Denis Villeneuve"]
    },
    {
      id: 2,
      title: "The Last of Us",
      category: "Série",
      description: "Adaptation du célèbre jeu vidéo post-apocalyptique",
      image: "/placeholder-series.jpg",
      tags: ["Post-apocalyptique", "Drame", "HBO"]
    },
    {
      id: 3,
      title: "Tomorrow X Together",
      category: "Musique",
      description: "Groupe de K-pop en pleine ascension",
      image: "/placeholder-music.jpg",
      tags: ["K-pop", "Pop", "Corée du Sud"]
    },
    {
      id: 4,
      title: "Klara and the Sun",
      category: "Livre",
      description: "Roman de Kazuo Ishiguro sur l'intelligence artificielle",
      image: "/placeholder-book.jpg",
      tags: ["Science-Fiction", "Nobellisé", "IA"]
    }
  ];

  return (
    <Box sx={{ display: 'flex', flexDirection: 'column', height: '100vh' }}>
      {/* Header */}
      <AppBar position="static" sx={{ backgroundColor: '#1976d2' }}>
        <Toolbar>
          <Typography variant="h6" component="div" sx={{ flexGrow: 1 }}>
            Découvrir
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
        {/* Barre de recherche */}
        <Paper sx={{ p: 2, mb: 3 }}>
          <TextField
            fullWidth
            placeholder="Rechercher des films, séries, musiques, livres..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            InputProps={{
              startAdornment: (
                <InputAdornment position="start">
                  <SearchIcon />
                </InputAdornment>
              ),
            }}
          />
        </Paper>

        {/* Catégories */}
        <Box sx={{ mb: 3 }}>
          <Typography variant="h6" gutterBottom>
            Catégories
          </Typography>
          <Box sx={{ display: 'flex', gap: 1, flexWrap: 'wrap' }}>
            <Chip label="Films" color="primary" />
            <Chip label="Séries" />
            <Chip label="Musique" />
            <Chip label="Livres" />
            <Chip label="Tendances" />
            <Chip label="Nouveautés" />
          </Box>
        </Box>

        {/* Contenu tendance */}
        <Typography variant="h6" gutterBottom>
          Tendances du moment
        </Typography>
        <Grid container spacing={2}>
          {trendingItems.map((item) => (
            <Grid item xs={12} sm={6} md={3} key={item.id}>
              <Card sx={{ height: '100%', display: 'flex', flexDirection: 'column' }}>
                <CardMedia
                  sx={{ height: 140, bgcolor: 'grey.300' }}
                  title={item.title}
                />
                <CardContent sx={{ flexGrow: 1 }}>
                  <Chip 
                    label={item.category} 
                    size="small" 
                    color="secondary" 
                    sx={{ mb: 1 }}
                  />
                  <Typography variant="h6" component="h2" gutterBottom>
                    {item.title}
                  </Typography>
                  <Typography variant="body2" color="text.secondary" sx={{ mb: 1 }}>
                    {item.description}
                  </Typography>
                  <Box sx={{ display: 'flex', gap: 0.5, flexWrap: 'wrap' }}>
                    {item.tags.map((tag) => (
                      <Chip key={tag} label={tag} size="small" variant="outlined" />
                    ))}
                  </Box>
                </CardContent>
                <CardActions>
                  <Button size="small" startIcon={<ThumbUpIcon />}>
                    J'aime
                  </Button>
                  <Button size="small" startIcon={<BookmarkAddIcon />}>
                    Ajouter
                  </Button>
                </CardActions>
              </Card>
            </Grid>
          ))}
        </Grid>

        {/* Recommandations personnalisées */}
        <Box sx={{ mt: 4 }}>
          <Typography variant="h6" gutterBottom>
            Recommandé pour vous
          </Typography>
          <Paper sx={{ p: 3, textAlign: 'center' }}>
            <Typography variant="body1" color="text.secondary">
              Créez des listes et likez du contenu pour recevoir des recommandations personnalisées !
            </Typography>
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

export default ExplorePage;