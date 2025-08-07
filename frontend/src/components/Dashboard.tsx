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
  Button,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
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
  ArrowBack as ArrowBackIcon,
  Edit as EditIcon,
  Delete as DeleteIcon,
  DragIndicator as DragIcon
} from '@mui/icons-material';

interface DashboardProps {
  onNavigate?: (section: string) => void;
  listId?: number;
}

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

interface ListItem {
  id: number;
  title: string;
  description: string;
  position: number;
  list: number;
  created_at: string;
  updated_at: string;
}

const Dashboard: React.FC<DashboardProps> = ({ onNavigate, listId = 1 }) => {
  const [bottomNavValue, setBottomNavValue] = useState(0);
  const [list, setList] = useState<TasteList | null>(null);
  const [items, setItems] = useState<ListItem[]>([]);
  const [isEditingTitle, setIsEditingTitle] = useState(false);
  const [isEditingDescription, setIsEditingDescription] = useState(false);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [openDialog, setOpenDialog] = useState(false);
  const [editingItem, setEditingItem] = useState<ListItem | null>(null);
  const [formData, setFormData] = useState({ title: '', description: '' });
  const [submitLoading, setSubmitLoading] = useState(false);

  // Récupérer les détails de la liste et ses éléments
  useEffect(() => {
    const fetchListData = async () => {
      try {
        const token = localStorage.getItem('access_token');
        
        // Récupérer les détails de la liste
        const listResponse = await fetch(`http://localhost:8000/api/lists/${listId}/`, {
          headers: { 'Authorization': `Bearer ${token}` }
        });
        
        if (listResponse.ok) {
          const listData = await listResponse.json();
          setList(listData);
        }
        
        // Récupérer les éléments de la liste
        const itemsResponse = await fetch(`http://localhost:8000/api/lists/${listId}/items/`, {
          headers: { 'Authorization': `Bearer ${token}` }
        });
        
        if (itemsResponse.ok) {
          const itemsData = await itemsResponse.json();
          setItems(Array.isArray(itemsData) ? itemsData : itemsData.results || []);
        }
        
      } catch (err) {
        console.error('Erreur lors du chargement:', err);
        setError('Erreur lors du chargement des données');
      } finally {
        setLoading(false);
      }
    };

    fetchListData();
  }, [listId]);

  const handleBottomNavChange = (event: React.SyntheticEvent, newValue: number) => {
    setBottomNavValue(newValue);
    const sections = ['accueil', 'decouvrir', 'match', 'listes', 'ajout'];
    onNavigate?.(sections[newValue]);
  };

  // Fonctions CRUD pour les éléments
  const handleOpenDialog = (item?: ListItem) => {
    setEditingItem(item || null);
    setFormData({
      title: item?.title || '',
      description: item?.description || ''
    });
    setOpenDialog(true);
    setError('');
  };

  const handleCloseDialog = () => {
    setOpenDialog(false);
    setEditingItem(null);
    setFormData({ title: '', description: '' });
    setError('');
  };

  const handleSubmitItem = async () => {
    if (!formData.title.trim()) {
      setError('Le titre est obligatoire');
      return;
    }

    setSubmitLoading(true);
    setError('');

    try {
      const token = localStorage.getItem('access_token');
      const url = editingItem 
        ? `http://localhost:8000/api/lists/${listId}/items/${editingItem.id}/`
        : `http://localhost:8000/api/lists/${listId}/items/`;
      
      const method = editingItem ? 'PUT' : 'POST';
      const body = {
        ...formData,
        ...(editingItem ? {} : { list: listId })
      };

      const response = await fetch(url, {
        method,
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(body)
      });

      if (!response.ok) {
        throw new Error('Erreur lors de la sauvegarde');
      }

      const data = await response.json();
      
      if (editingItem) {
        setItems(items.map(item => item.id === editingItem.id ? data : item));
      } else {
        setItems([...items, data].sort((a, b) => a.position - b.position));
      }

      handleCloseDialog();
    } catch (err) {
      setError('Erreur lors de la sauvegarde');
      console.error(err);
    } finally {
      setSubmitLoading(false);
    }
  };

  const handleDeleteItem = async (item: ListItem) => {
    if (!window.confirm(`Êtes-vous sûr de vouloir supprimer "${item.title}" ?`)) {
      return;
    }

    try {
      const token = localStorage.getItem('access_token');
      const response = await fetch(`http://localhost:8000/api/lists/${listId}/items/${item.id}/`, {
        method: 'DELETE',
        headers: { 'Authorization': `Bearer ${token}` }
      });

      if (!response.ok) {
        throw new Error('Erreur lors de la suppression');
      }

      setItems(items.filter(i => i.id !== item.id));
    } catch (err) {
      setError('Erreur lors de la suppression');
      console.error(err);
    }
  };

  const handleUpdateListInfo = async (field: 'name' | 'description', value: string) => {
    if (!list) return;

    try {
      const token = localStorage.getItem('access_token');
      const response = await fetch(`http://localhost:8000/api/lists/${listId}/`, {
        method: 'PUT',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({ ...list, [field]: value })
      });

      if (response.ok) {
        const updatedList = await response.json();
        setList(updatedList);
      }
    } catch (err) {
      console.error('Erreur lors de la mise à jour:', err);
    }
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
          {/* Navigation retour */}
          <Box sx={{ display: 'flex', alignItems: 'center', mb: { xs: 1, sm: 2 } }}>
            <IconButton 
              size="small" 
              sx={{ mr: 1, p: { xs: 0.5, sm: 1 } }} 
              aria-label="retour"
              onClick={() => onNavigate?.('listes')}
            >
              <ArrowBackIcon sx={{ fontSize: { xs: 20, sm: 24 } }} />
            </IconButton>
            <Typography 
              variant="body2" 
              color="text.secondary"
              sx={{ fontSize: { xs: '0.75rem', sm: '0.875rem' } }}
            >
              Retour aux Collections
            </Typography>
          </Box>

          {/* Titre de la liste */}
          <Box sx={{ mb: { xs: 1, sm: 2 } }}>
            {loading ? (
              <Typography 
                variant="h4" 
                component="h1"
                sx={{ fontSize: { xs: '1.25rem', sm: '2.125rem' } }}
              >
                Chargement...
              </Typography>
            ) : isEditingTitle ? (
              <TextField
                fullWidth
                value={list?.name || ''}
                onChange={(e) => setList(list ? { ...list, name: e.target.value } : null)}
                onBlur={() => {
                  setIsEditingTitle(false);
                  if (list) handleUpdateListInfo('name', list.name);
                }}
                onKeyPress={(e) => {
                  if (e.key === 'Enter') {
                    setIsEditingTitle(false);
                    if (list) handleUpdateListInfo('name', list.name);
                  }
                }}
                variant="standard"
                sx={{ 
                  '& .MuiInputBase-input': { 
                    fontSize: { xs: '1.25rem', sm: '1.5rem' }, 
                    fontWeight: 'bold' 
                  } 
                }}
                autoFocus
              />
            ) : (
              <Box sx={{ display: 'flex', alignItems: 'center' }}>
                <Typography 
                  variant="h4" 
                  component="h1" 
                  sx={{ 
                    flexGrow: 1,
                    fontSize: { xs: '1.25rem', sm: '2.125rem' },
                    fontWeight: 'bold'
                  }}
                >
                  {list?.name || 'Liste de goûts'}
                </Typography>
                <IconButton 
                  size="small" 
                  onClick={() => setIsEditingTitle(true)}
                  aria-label="edit"
                  sx={{ p: { xs: 0.5, sm: 1 } }}
                >
                  <EditIcon sx={{ fontSize: { xs: 18, sm: 24 } }} />
                </IconButton>
              </Box>
            )}
          </Box>

          {/* Catégorie */}
          {list?.category_display && (
            <Typography 
              variant="subtitle1" 
              color="primary" 
              sx={{ 
                mb: { xs: 1, sm: 2 }, 
                fontWeight: 'medium',
                fontSize: { xs: '0.875rem', sm: '1rem' }
              }}
            >
              📂 {list.category_display}
            </Typography>
          )}

          {/* Description */}
          <Box sx={{ mb: 3 }}>
            {loading ? (
              <Typography variant="body1" color="text.secondary">Chargement de la description...</Typography>
            ) : isEditingDescription ? (
              <TextField
                fullWidth
                value={list?.description || ''}
                onChange={(e) => setList(list ? { ...list, description: e.target.value } : null)}
                onBlur={() => {
                  setIsEditingDescription(false);
                  if (list) handleUpdateListInfo('description', list.description);
                }}
                variant="standard"
                multiline
                autoFocus
              />
            ) : (
              <Box sx={{ display: 'flex', alignItems: 'flex-start' }}>
                <Typography variant="body1" color="text.secondary" sx={{ flexGrow: 1 }}>
                  {list?.description || 'Cliquez pour ajouter une description.'}
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

          {error && (
            <Alert severity="error" sx={{ mb: 2 }} onClose={() => setError('')}>
              {error}
            </Alert>
          )}

          {/* Section Éléments */}
          <Typography 
            variant="h6" 
            sx={{ 
              mb: { xs: 1, sm: 2 },
              fontSize: { xs: '1rem', sm: '1.25rem' },
              fontWeight: 'medium'
            }}
          >
            Éléments ({items.length})
          </Typography>

          {loading ? (
            <Box sx={{ display: 'flex', justifyContent: 'center', py: 4 }}>
              <CircularProgress />
            </Box>
          ) : items.length === 0 ? (
            <Box sx={{ textAlign: 'center', py: 4 }}>
              <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
                Cette liste est vide
              </Typography>
              <Typography variant="body2" color="text.secondary">
                Ajoutez votre premier élément !
              </Typography>
            </Box>
          ) : (
            <List sx={{ px: 0 }}>
              {items.map((item, index) => (
                <ListItem 
                  key={item.id} 
                  sx={{ 
                    px: 0, 
                    py: { xs: 1, sm: 1 },
                    borderBottom: { xs: '1px solid #f0f0f0', sm: 'none' }
                  }}
                >
                  <Box sx={{ 
                    display: { xs: 'none', sm: 'flex' }, 
                    alignItems: 'center', 
                    mr: 2 
                  }}>
                    <DragIcon sx={{ color: 'text.secondary', cursor: 'move' }} />
                  </Box>
                  <ListItemText
                    primary={`${index + 1}. ${item.title}`}
                    secondary={item.description || undefined}
                    sx={{ 
                      '& .MuiListItemText-primary': { 
                        fontWeight: 'medium',
                        fontSize: { xs: '0.875rem', sm: '1rem' }
                      },
                      '& .MuiListItemText-secondary': { 
                        fontSize: { xs: '0.75rem', sm: '0.875rem' }
                      },
                      cursor: 'pointer'
                    }}
                    onClick={() => handleOpenDialog(item)}
                  />
                  <ListItemSecondaryAction sx={{ right: { xs: 8, sm: 16 } }}>
                    <MuiIconButton 
                      edge="end" 
                      size="small"
                      onClick={() => handleOpenDialog(item)}
                      aria-label="modifier"
                      sx={{ 
                        mr: { xs: 0.5, sm: 1 },
                        p: { xs: 0.5, sm: 1 }
                      }}
                    >
                      <EditIcon sx={{ fontSize: { xs: 16, sm: 20 } }} />
                    </MuiIconButton>
                    <MuiIconButton 
                      edge="end" 
                      size="small"
                      onClick={() => handleDeleteItem(item)}
                      aria-label="supprimer"
                      color="error"
                      sx={{ p: { xs: 0.5, sm: 1 } }}
                    >
                      <DeleteIcon sx={{ fontSize: { xs: 16, sm: 20 } }} />
                    </MuiIconButton>
                  </ListItemSecondaryAction>
                </ListItem>
              ))}
            </List>
          )}

          {/* Bouton Ajouter */}
          <Box sx={{ mt: { xs: 2, sm: 2 } }}>
            <Button
              variant="outlined"
              startIcon={<AddIcon sx={{ fontSize: { xs: 18, sm: 20 } }} />}
              onClick={() => handleOpenDialog()}
              sx={{ 
                width: '100%', 
                py: { xs: 1, sm: 1.5 },
                fontSize: { xs: '0.875rem', sm: '1rem' }
              }}
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


      {/* Dialog pour créer/modifier un élément */}
      <Dialog 
        open={openDialog} 
        onClose={handleCloseDialog} 
        maxWidth="sm" 
        fullWidth
        PaperProps={{
          sx: {
            mx: { xs: 2, sm: 3 },
            my: { xs: 2, sm: 3 },
            maxWidth: { xs: 'calc(100vw - 32px)', sm: '600px' }
          }
        }}
      >
        <DialogTitle sx={{ 
          fontSize: { xs: '1.1rem', sm: '1.25rem' },
          px: { xs: 2, sm: 3 },
          py: { xs: 2, sm: 2 }
        }}>
          {editingItem ? 'Modifier l\'élément' : 'Ajouter un élément'}
        </DialogTitle>
        <DialogContent sx={{ px: { xs: 2, sm: 3 } }}>
          <TextField
            autoFocus
            margin="dense"
            label="Titre *"
            fullWidth
            variant="outlined"
            value={formData.title}
            onChange={(e) => setFormData({ ...formData, title: e.target.value })}
            sx={{ 
              mb: 2,
              '& .MuiInputBase-input': {
                fontSize: { xs: '0.875rem', sm: '1rem' }
              }
            }}
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
            sx={{ 
              '& .MuiInputBase-input': {
                fontSize: { xs: '0.875rem', sm: '1rem' }
              }
            }}
          />
          {error && (
            <Alert severity="error" sx={{ mt: 2, fontSize: { xs: '0.875rem', sm: '1rem' } }}>
              {error}
            </Alert>
          )}
        </DialogContent>
        <DialogActions sx={{ 
          px: { xs: 2, sm: 3 },
          py: { xs: 2, sm: 2 },
          gap: { xs: 1, sm: 1 }
        }}>
          <Button 
            onClick={handleCloseDialog}
            sx={{ fontSize: { xs: '0.875rem', sm: '1rem' } }}
          >
            Annuler
          </Button>
          <Button
            onClick={handleSubmitItem}
            variant="contained"
            disabled={submitLoading}
            startIcon={submitLoading ? <CircularProgress size={20} /> : null}
            sx={{ fontSize: { xs: '0.875rem', sm: '1rem' } }}
          >
            {editingItem ? 'Modifier' : 'Ajouter'}
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};

export default Dashboard; 