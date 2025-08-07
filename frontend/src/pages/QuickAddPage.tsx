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
  TextField,
  Select,
  MenuItem,
  FormControl,
  InputLabel,
  Grid,
  Card,
  CardContent,
  CardActions,
  Chip,
  BottomNavigation,
  BottomNavigationAction,
  Alert,
  CircularProgress,
  Autocomplete
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
  Search as SearchIcon,
  Save as SaveIcon
} from '@mui/icons-material';

interface QuickAddPageProps {
  onNavigate?: (section: string) => void;
}

const QuickAddPage: React.FC<QuickAddPageProps> = ({ onNavigate }) => {
  const [bottomNavValue, setBottomNavValue] = useState(4); // "Ajout rapide" selected
  const [selectedCategory, setSelectedCategory] = useState('');
  const [title, setTitle] = useState('');
  const [description, setDescription] = useState('');
  const [tags, setTags] = useState<string[]>([]);
  const [selectedList, setSelectedList] = useState('');
  const [loading, setLoading] = useState(false);
  const [success, setSuccess] = useState(false);

  const handleBottomNavChange = (event: React.SyntheticEvent, newValue: number) => {
    setBottomNavValue(newValue);
    const sections = ['accueil', 'decouvrir', 'match', 'listes', 'ajout'];
    onNavigate?.(sections[newValue]);
  };

  const categories = [
    { value: 'film', label: 'Film', icon: <MovieIcon /> },
    { value: 'serie', label: 'Série', icon: <TvIcon /> },
    { value: 'musique', label: 'Musique', icon: <MusicIcon /> },
    { value: 'livre', label: 'Livre', icon: <BookIcon /> }
  ];

  const myLists = [
    { value: 'films-favoris', label: 'Mes Films Favoris' },
    { value: 'musique-travail', label: 'Musique de Travail' },
    { value: 'livres-a-lire', label: 'Livres à Lire' }
  ];

  const popularTags = [
    'Action', 'Comédie', 'Drame', 'Sci-Fi', 'Thriller',
    'Rock', 'Pop', 'Jazz', 'Classique', 'Électronique',
    'Roman', 'Biographie', 'Science-Fiction', 'Fantasy', 'Histoire'
  ];

  const handleSubmit = async (event: React.FormEvent) => {
    event.preventDefault();
    
    if (!selectedCategory || !title.trim()) {
      return;
    }

    setLoading(true);
    
    try {
      // Simuler un appel API
      await new Promise(resolve => setTimeout(resolve, 1500));
      
      console.log('Nouvel élément ajouté:', {
        category: selectedCategory,
        title,
        description,
        tags,
        list: selectedList
      });
      
      setSuccess(true);
      
      // Réinitialiser le formulaire
      setTitle('');
      setDescription('');
      setTags([]);
      setSelectedList('');
      
      setTimeout(() => setSuccess(false), 3000);
    } catch (error) {
      console.error('Erreur lors de l\'ajout:', error);
    } finally {
      setLoading(false);
    }
  };

  const quickSuggestions = [
    { title: "The Batman", category: "film", tags: ["Action", "Thriller"] },
    { title: "Stranger Things", category: "serie", tags: ["Sci-Fi", "Thriller"] },
    { title: "Bad Bunny", category: "musique", tags: ["Reggaeton", "Pop"] },
    { title: "Dune", category: "livre", tags: ["Sci-Fi", "Épique"] }
  ];

  const handleQuickAdd = (suggestion: typeof quickSuggestions[0]) => {
    setSelectedCategory(suggestion.category);
    setTitle(suggestion.title);
    setTags(suggestion.tags);
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
      <Container sx={{ flexGrow: 1, py: 2, overflow: 'auto' }}>
        {success && (
          <Alert severity="success" sx={{ mb: 2 }}>
            Élément ajouté avec succès !
          </Alert>
        )}

        {/* Suggestions rapides */}
        <Paper sx={{ p: 3, mb: 3 }}>
          <Typography variant="h6" gutterBottom>
            Suggestions rapides
          </Typography>
          <Grid container spacing={2}>
            {quickSuggestions.map((suggestion, index) => (
              <Grid item xs={12} sm={6} md={3} key={index}>
                <Card sx={{ cursor: 'pointer', '&:hover': { bgcolor: 'action.hover' } }}>
                  <CardContent sx={{ textAlign: 'center', py: 2 }}>
                    {categories.find(c => c.value === suggestion.category)?.icon}
                    <Typography variant="body1" sx={{ mt: 1 }}>
                      {suggestion.title}
                    </Typography>
                    <Box sx={{ mt: 1 }}>
                      {suggestion.tags.slice(0, 2).map(tag => (
                        <Chip key={tag} label={tag} size="small" sx={{ m: 0.25 }} />
                      ))}
                    </Box>
                  </CardContent>
                  <CardActions sx={{ justifyContent: 'center', pt: 0 }}>
                    <Button 
                      size="small" 
                      onClick={() => handleQuickAdd(suggestion)}
                    >
                      Ajouter
                    </Button>
                  </CardActions>
                </Card>
              </Grid>
            ))}
          </Grid>
        </Paper>

        {/* Formulaire d'ajout */}
        <Paper sx={{ p: 3 }}>
          <Typography variant="h6" gutterBottom>
            Ajouter un nouvel élément
          </Typography>
          
          <Box component="form" onSubmit={handleSubmit}>
            <Grid container spacing={3}>
              {/* Catégorie */}
              <Grid item xs={12} sm={6}>
                <FormControl fullWidth required>
                  <InputLabel>Catégorie</InputLabel>
                  <Select
                    value={selectedCategory}
                    onChange={(e) => setSelectedCategory(e.target.value)}
                    label="Catégorie"
                  >
                    {categories.map((category) => (
                      <MenuItem key={category.value} value={category.value}>
                        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                          {category.icon}
                          {category.label}
                        </Box>
                      </MenuItem>
                    ))}
                  </Select>
                </FormControl>
              </Grid>

              {/* Liste de destination */}
              <Grid item xs={12} sm={6}>
                <FormControl fullWidth>
                  <InputLabel>Ajouter à une liste</InputLabel>
                  <Select
                    value={selectedList}
                    onChange={(e) => setSelectedList(e.target.value)}
                    label="Ajouter à une liste"
                  >
                    {myLists.map((list) => (
                      <MenuItem key={list.value} value={list.value}>
                        {list.label}
                      </MenuItem>
                    ))}
                  </Select>
                </FormControl>
              </Grid>

              {/* Titre */}
              <Grid item xs={12}>
                <TextField
                  fullWidth
                  required
                  label="Titre"
                  value={title}
                  onChange={(e) => setTitle(e.target.value)}
                  placeholder="Ex: Inception, The Beatles, Game of Thrones..."
                />
              </Grid>

              {/* Description */}
              <Grid item xs={12}>
                <TextField
                  fullWidth
                  multiline
                  rows={3}
                  label="Description (optionnelle)"
                  value={description}
                  onChange={(e) => setDescription(e.target.value)}
                  placeholder="Pourquoi aimez-vous cet élément ?"
                />
              </Grid>

              {/* Tags */}
              <Grid item xs={12}>
                <Autocomplete
                  multiple
                  options={popularTags}
                  value={tags}
                  onChange={(event, newValue) => setTags(newValue)}
                  renderTags={(value, getTagProps) =>
                    value.map((option, index) => (
                      <Chip
                        variant="outlined"
                        label={option}
                        {...getTagProps({ index })}
                      />
                    ))
                  }
                  renderInput={(params) => (
                    <TextField
                      {...params}
                      label="Tags"
                      placeholder="Ajoutez des tags..."
                    />
                  )}
                />
              </Grid>

              {/* Bouton de soumission */}
              <Grid item xs={12}>
                <Button
                  type="submit"
                  variant="contained"
                  size="large"
                  fullWidth
                  disabled={!selectedCategory || !title.trim() || loading}
                  startIcon={loading ? <CircularProgress size={20} /> : <SaveIcon />}
                >
                  {loading ? 'Ajout en cours...' : 'Ajouter à ma collection'}
                </Button>
              </Grid>
            </Grid>
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

export default QuickAddPage;