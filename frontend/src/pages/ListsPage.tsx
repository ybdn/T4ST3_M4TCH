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
  BottomNavigation,
  BottomNavigationAction,
  Button,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField,
  Alert,
  CircularProgress
} from '@mui/material';
import {
  Notifications as NotificationsIcon,
  AccountCircle as AccountCircleIcon,
  Home as HomeIcon,
  Explore as ExploreIcon,
  Favorite as FavoriteIcon,
  List as ListIcon,
  Add as AddIcon,
  Edit as EditIcon,
  Delete as DeleteIcon
} from '@mui/icons-material';
import { useAuth } from '../context/AuthContext';

interface TasteList {
  id: number;
  name: string;
  description: string;
  owner: string;
  created_at: string;
  updated_at: string;
}

interface ListsPageProps {
  onNavigate?: (section: string) => void;
}

const ListsPage: React.FC<ListsPageProps> = ({ onNavigate }) => {
  const [lists, setLists] = useState<TasteList[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [openDialog, setOpenDialog] = useState(false);
  const [editingList, setEditingList] = useState<TasteList | null>(null);
  const [formData, setFormData] = useState({ name: '', description: '' });
  const [submitLoading, setSubmitLoading] = useState(false);
  const [bottomNavValue, setBottomNavValue] = useState(3); // "Mes listes" selected
  const { user } = useAuth();

  const handleBottomNavChange = (event: React.SyntheticEvent, newValue: number) => {
    setBottomNavValue(newValue);
    const sections = ['accueil', 'decouvrir', 'match', 'listes', 'ajout'];
    onNavigate?.(sections[newValue]);
  };

  // Fonction pour récupérer les listes
  const fetchLists = async () => {
    try {
      const token = localStorage.getItem('access_token');
      const response = await fetch('http://localhost:8000/api/lists/', {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });

      if (!response.ok) {
        throw new Error('Erreur lors du chargement des listes');
      }

      const data = await response.json();
      setLists(data);
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

  // Ouvrir le dialog pour créer une nouvelle liste
  const handleOpenDialog = () => {
    setEditingList(null);
    setFormData({ name: '', description: '' });
    setOpenDialog(true);
  };

  // Ouvrir le dialog pour modifier une liste
  const handleEditList = (list: TasteList) => {
    setEditingList(list);
    setFormData({ name: list.name, description: list.description });
    setOpenDialog(true);
  };

  // Fermer le dialog
  const handleCloseDialog = () => {
    setOpenDialog(false);
    setEditingList(null);
    setFormData({ name: '', description: '' });
    setError('');
  };

  // Soumettre le formulaire (créer ou modifier)
  const handleSubmit = async () => {
    if (!formData.name.trim()) {
      setError('Le nom de la liste est obligatoire');
      return;
    }

    setSubmitLoading(true);
    setError('');

    try {
      const token = localStorage.getItem('access_token');
      const url = editingList 
        ? `http://localhost:8000/api/lists/${editingList.id}/`
        : 'http://localhost:8000/api/lists/';
      
      const method = editingList ? 'PUT' : 'POST';

      const response = await fetch(url, {
        method,
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(formData)
      });

      if (!response.ok) {
        throw new Error('Erreur lors de la sauvegarde');
      }

      const data = await response.json();
      
      if (editingList) {
        // Mise à jour d'une liste existante
        setLists(lists.map(list => list.id === editingList.id ? data : list));
      } else {
        // Nouvelle liste
        setLists([data, ...lists]);
      }

      handleCloseDialog();
    } catch (err) {
      setError('Erreur lors de la sauvegarde de la liste');
      console.error(err);
    } finally {
      setSubmitLoading(false);
    }
  };

  // Supprimer une liste
  const handleDeleteList = async (listId: number) => {
    if (!window.confirm('Êtes-vous sûr de vouloir supprimer cette liste ?')) {
      return;
    }

    try {
      const token = localStorage.getItem('access_token');
      const response = await fetch(`http://localhost:8000/api/lists/${listId}/`, {
        method: 'DELETE',
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });

      if (!response.ok) {
        throw new Error('Erreur lors de la suppression');
      }

      setLists(lists.filter(list => list.id !== listId));
    } catch (err) {
      setError('Erreur lors de la suppression de la liste');
      console.error(err);
    }
  };

  return (
    <Box sx={{ display: 'flex', flexDirection: 'column', minHeight: '100vh' }}>
      {/* Header */}
      <AppBar position="static" sx={{ backgroundColor: '#1976d2' }}>
        <Toolbar>
          <Typography variant="h6" component="div" sx={{ flexGrow: 1 }}>
            Mes Listes
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
          <Box sx={{ mb: 3 }}>
            <Typography variant="h4" component="h1" gutterBottom>
              Mes Listes
            </Typography>
            <Typography variant="body1" color="text.secondary">
              Choisissez une liste pour la consulter et la modifier
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
            <>
              {lists.length === 0 ? (
                <Box sx={{ textAlign: 'center', py: 4 }}>
                  <Typography variant="h6" gutterBottom>
                    Vous n'avez pas encore de listes
                  </Typography>
                  <Typography variant="body2" color="text.secondary" sx={{ mb: 3 }}>
                    Créez votre première liste pour commencer !
                  </Typography>
                  <Button
                    variant="contained"
                    startIcon={<AddIcon />}
                    onClick={handleOpenDialog}
                  >
                    Créer ma première liste
                  </Button>
                </Box>
              ) : (
                <>
                  <List>
                    {lists.map((list) => (
                      <ListItem key={list.id} sx={{ px: 0 }}>
                        <ListItemText
                          primary={list.name}
                          secondary={list.description || 'Aucune description'}
                          sx={{ cursor: 'pointer' }}
                          onClick={() => {
                            // TODO: Navigation vers la page de détail de la liste
                            console.log(`Ouvrir la liste: ${list.name}`);
                          }}
                        />
                        <ListItemSecondaryAction>
                          <IconButton 
                            edge="end" 
                            size="small"
                            onClick={() => handleEditList(list)}
                            aria-label="modifier"
                            sx={{ mr: 1 }}
                          >
                            <EditIcon />
                          </IconButton>
                          <IconButton 
                            edge="end" 
                            size="small"
                            onClick={() => handleDeleteList(list.id)}
                            aria-label="supprimer"
                            color="error"
                          >
                            <DeleteIcon />
                          </IconButton>
                        </ListItemSecondaryAction>
                      </ListItem>
                    ))}
                  </List>

                  <Box sx={{ mt: 3, textAlign: 'center' }}>
                    <Button
                      variant="outlined"
                      startIcon={<AddIcon />}
                      onClick={handleOpenDialog}
                    >
                      Créer une nouvelle liste
                    </Button>
                  </Box>
                </>
              )}
            </>
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

      {/* Espace pour éviter que le contenu soit caché par la bottom navigation */}
      <Box sx={{ height: 56 }} />

      {/* Dialog pour créer/modifier une liste */}
      <Dialog open={openDialog} onClose={handleCloseDialog} maxWidth="sm" fullWidth>
        <DialogTitle>
          {editingList ? 'Modifier la liste' : 'Créer une nouvelle liste'}
        </DialogTitle>
        <DialogContent>
          <TextField
            autoFocus
            margin="dense"
            label="Nom de la liste"
            fullWidth
            variant="outlined"
            value={formData.name}
            onChange={(e) => setFormData({ ...formData, name: e.target.value })}
            sx={{ mb: 2 }}
          />
          <TextField
            margin="dense"
            label="Description (optionnelle)"
            fullWidth
            multiline
            rows={3}
            variant="outlined"
            value={formData.description}
            onChange={(e) => setFormData({ ...formData, description: e.target.value })}
          />
          {error && (
            <Alert severity="error" sx={{ mt: 2 }}>
              {error}
            </Alert>
          )}
        </DialogContent>
        <DialogActions>
          <Button onClick={handleCloseDialog}>Annuler</Button>
          <Button
            onClick={handleSubmit}
            variant="contained"
            disabled={submitLoading}
            startIcon={submitLoading ? <CircularProgress size={20} /> : null}
          >
            {editingList ? 'Modifier' : 'Créer'}
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};

export default ListsPage;