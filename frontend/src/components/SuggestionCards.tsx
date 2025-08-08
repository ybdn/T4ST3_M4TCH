import React, { useState, useEffect } from 'react';
import { useErrorHandler } from '../hooks/useErrorHandler';
import cacheService from '../services/cacheService';
import {
  Box,
  Card,
  CardContent,
  CardActions,
  Typography,
  Button,
  Grid,
  Skeleton,
  Alert,
  Chip,
  IconButton
} from '@mui/material';
import {
  Add as AddIcon,
  Refresh as RefreshIcon,
  TrendingUp as TrendingUpIcon,
  Lightbulb as LightbulbIcon
} from '@mui/icons-material';

interface Suggestion {
  title: string;
  description: string;
  category: string;
  category_display: string;
  popularity: number;
  type: 'popular' | 'suggestion';
}

interface SuggestionCardsProps {
  category?: string;
  limit?: number;
  onAdd?: (suggestion: Suggestion) => void;
  title?: string;
  showRefresh?: boolean;
}

const SuggestionCards: React.FC<SuggestionCardsProps> = ({
  category,
  limit = 6,
  onAdd,
  title,
  showRefresh = true
}) => {
  const [suggestions, setSuggestions] = useState<Suggestion[]>([]);
  const [loading, setLoading] = useState(true);
  const [addingIds, setAddingIds] = useState<Set<number>>(new Set());
  
  const { error, handleError, clearError } = useErrorHandler();

  const fetchSuggestions = async () => {
    setLoading(true);
    clearError();

    // Vérifier le cache d'abord
    const cacheKey = cacheService.generateSuggestionsKey(category, limit);
    const cachedData = cacheService.get<{ suggestions: Suggestion[] }>(cacheKey);
    
    if (cachedData) {
      setSuggestions(cachedData.suggestions);
      setLoading(false);
      return;
    }

    try {
      const token = localStorage.getItem('access_token');
      const params = new URLSearchParams({
        limit: limit.toString()
      });
      
      if (category) {
        params.append('category', category);
      }

      const response = await fetch(`http://localhost:8000/api/suggestions/?${params}`, {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });

      if (!response.ok) {
        throw new Error('Erreur lors du chargement des suggestions');
      }

      const data = await response.json();
      const suggestions = data.suggestions || [];
      
      // Mettre en cache pour 5 minutes
      cacheService.set(cacheKey, { suggestions }, 5 * 60 * 1000);
      
      setSuggestions(suggestions);
    } catch (err) {
      handleError(err, 'SuggestionCards');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchSuggestions();
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [category, limit]);

  const handleAdd = async (suggestion: Suggestion, index: number) => {
    if (!onAdd) return;

    setAddingIds(prev => new Set(prev.add(index)));

    try {
      await onAdd(suggestion);
    } finally {
      setAddingIds(prev => {
        const newSet = new Set(prev);
        newSet.delete(index);
        return newSet;
      });
    }
  };

  const getCategoryColor = (cat: string) => {
    const colors = {
      'FILMS': '#e53e3e',
      'SERIES': '#3182ce', 
      'MUSIQUE': '#38a169',
      'LIVRES': '#d69e2e'
    };
    return colors[cat as keyof typeof colors] || '#718096';
  };

  const getSuggestionTypeIcon = (type: string, popularity: number) => {
    if (type === 'popular' && popularity > 1) {
      return <TrendingUpIcon fontSize="small" />;
    }
    return <LightbulbIcon fontSize="small" />;
  };

  const getSuggestionTypeLabel = (type: string, popularity: number) => {
    if (type === 'popular' && popularity > 1) {
      return `Populaire (${popularity})`;
    }
    return 'Suggestion';
  };

  if (loading) {
    return (
      <Box>
        {title && (
          <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', mb: 2 }}>
            <Typography variant="h6" sx={{ fontSize: { xs: '1rem', sm: '1.25rem' } }}>
              {title}
            </Typography>
          </Box>
        )}
        <Grid container spacing={2}>
          {Array.from({ length: limit }).map((_, index) => (
            <Grid item xs={12} sm={6} md={4} key={index}>
              <Card>
                <CardContent>
                  <Skeleton variant="text" width="80%" height={24} />
                  <Skeleton variant="text" width="60%" height={20} sx={{ mt: 1 }} />
                  <Skeleton variant="text" width="100%" height={40} sx={{ mt: 1 }} />
                </CardContent>
                <CardActions>
                  <Skeleton variant="rectangular" width={100} height={36} />
                </CardActions>
              </Card>
            </Grid>
          ))}
        </Grid>
      </Box>
    );
  }

  if (error) {
    return (
      <Alert 
        severity="error" 
        action={
          <IconButton color="inherit" size="small" onClick={fetchSuggestions}>
            <RefreshIcon />
          </IconButton>
        }
      >
        {error.message}
      </Alert>
    );
  }

  if (suggestions.length === 0) {
    return (
      <Box sx={{ textAlign: 'center', py: 4 }}>
        <Typography variant="body1" color="text.secondary" gutterBottom>
          Aucune suggestion disponible pour le moment
        </Typography>
        <Button
          variant="outlined"
          startIcon={<RefreshIcon />}
          onClick={fetchSuggestions}
          sx={{ mt: 2 }}
        >
          Recharger
        </Button>
      </Box>
    );
  }

  return (
    <Box>
      {title && (
        <Box sx={{ 
          display: 'flex', 
          alignItems: 'center', 
          justifyContent: 'space-between', 
          mb: 2 
        }}>
          <Typography 
            variant="h6" 
            sx={{ 
              fontSize: { xs: '1rem', sm: '1.25rem' },
              fontWeight: 'medium'
            }}
          >
            {title}
          </Typography>
          {showRefresh && (
            <IconButton
              size="small"
              onClick={fetchSuggestions}
              disabled={loading}
              aria-label="refresh"
            >
              <RefreshIcon />
            </IconButton>
          )}
        </Box>
      )}

      <Grid container spacing={2}>
        {suggestions.map((suggestion, index) => (
          <Grid item xs={12} sm={6} md={4} key={index}>
            <Card 
              sx={{ 
                height: '100%',
                display: 'flex',
                flexDirection: 'column',
                transition: 'transform 0.2s, box-shadow 0.2s',
                '&:hover': {
                  transform: 'translateY(-2px)',
                  boxShadow: 4
                }
              }}
            >
              <CardContent sx={{ flexGrow: 1, pb: 1 }}>
                <Box sx={{ display: 'flex', alignItems: 'flex-start', justifyContent: 'space-between', mb: 1 }}>
                  <Typography 
                    variant="h6" 
                    component="h3"
                    sx={{ 
                      fontSize: { xs: '0.9rem', sm: '1.1rem' },
                      fontWeight: 'medium',
                      lineHeight: 1.2,
                      flexGrow: 1,
                      mr: 1
                    }}
                  >
                    {suggestion.title}
                  </Typography>
                  {!category && (
                    <Chip
                      label={suggestion.category_display}
                      size="small"
                      sx={{
                        fontSize: '0.7rem',
                        height: 20,
                        backgroundColor: getCategoryColor(suggestion.category),
                        color: 'white',
                        '& .MuiChip-label': {
                          px: 1
                        }
                      }}
                    />
                  )}
                </Box>

                {suggestion.description && (
                  <Typography 
                    variant="body2" 
                    color="text.secondary"
                    sx={{ 
                      fontSize: { xs: '0.75rem', sm: '0.875rem' },
                      lineHeight: 1.4,
                      mb: 1
                    }}
                  >
                    {suggestion.description}
                  </Typography>
                )}

                <Box sx={{ display: 'flex', alignItems: 'center', gap: 0.5 }}>
                  {getSuggestionTypeIcon(suggestion.type, suggestion.popularity)}
                  <Typography 
                    variant="caption" 
                    color="text.secondary"
                    sx={{ fontSize: '0.7rem' }}
                  >
                    {getSuggestionTypeLabel(suggestion.type, suggestion.popularity)}
                  </Typography>
                </Box>
              </CardContent>

              <CardActions sx={{ pt: 0, px: 2, pb: 2 }}>
                <Button
                  size="small"
                  variant="contained"
                  startIcon={<AddIcon />}
                  onClick={() => handleAdd(suggestion, index)}
                  disabled={addingIds.has(index)}
                  fullWidth
                  sx={{
                    fontSize: { xs: '0.75rem', sm: '0.875rem' },
                    py: { xs: 0.5, sm: 0.75 },
                    backgroundColor: getCategoryColor(suggestion.category),
                    '&:hover': {
                      backgroundColor: getCategoryColor(suggestion.category),
                      filter: 'brightness(0.9)'
                    }
                  }}
                >
                  {addingIds.has(index) ? 'Ajout...' : 'Ajouter'}
                </Button>
              </CardActions>
            </Card>
          </Grid>
        ))}
      </Grid>
    </Box>
  );
};

export default SuggestionCards;