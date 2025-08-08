import React, { useState, useEffect } from 'react';
import {
  Box,
  Card,
  CardContent,
  CardMedia,
  Typography,
  Button,
  Chip,
  Grid,
  Skeleton,
  Alert,
  IconButton,
  Tooltip,
  Rating
} from '@mui/material';
import {
  Add as AddIcon,
  Info as InfoIcon,
  Star as StarIcon,
  CalendarToday as CalendarIcon,
  Language as LanguageIcon
} from '@mui/icons-material';
import { useFeedback } from '../context/FeedbackContext';
import cacheService from '../services/cacheService';

interface ExternalSearchResult {
  external_id: string;
  title: string;
  description: string;
  category: string;
  category_display: string;
  poster_url?: string;
  backdrop_url?: string;
  rating?: number;
  release_date?: string;
  popularity?: number;
  source: string;
  type: string;
  metadata?: any;
}

interface ExternalSearchResultsProps {
  query: string;
  category?: string;
  source?: string;
  onAdd?: (result: ExternalSearchResult) => void;
  onSelect?: (result: ExternalSearchResult) => void;
}

const ExternalSearchResults: React.FC<ExternalSearchResultsProps> = ({
  query,
  category,
  source,
  onAdd,
  onSelect
}) => {
  const [results, setResults] = useState<ExternalSearchResult[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [addingIds, setAddingIds] = useState<Set<string>>(new Set());
  const { showSuccess, showError } = useFeedback();

  const fetchResults = async () => {
    if (!query.trim() || query.length < 2) {
      setResults([]);
      return;
    }

    setLoading(true);
    setError('');

    // Vérifier le cache
    const cacheKey = `external_search:${query}:${category || 'all'}:${source || 'all'}`;
    const cachedResults = cacheService.get<{ results: ExternalSearchResult[] }>(cacheKey);
    
    if (cachedResults) {
      setResults(cachedResults.results);
      setLoading(false);
      return;
    }

    try {
      const token = localStorage.getItem('access_token');
      const params = new URLSearchParams({
        q: query,
        limit: '12'
      });
      
      if (category) {
        params.append('category', category);
      }
      if (source) {
        params.append('source', source);
      }

      const response = await fetch(`http://localhost:8000/api/search/external/?${params}`, {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });

      if (!response.ok) {
        throw new Error('Erreur lors de la recherche externe');
      }

      const data = await response.json();
      const results = data.results || [];
      
      // Mettre en cache pour 5 minutes
      cacheService.set(cacheKey, { results }, 5 * 60 * 1000);
      
      setResults(results);
    } catch (err) {
      console.error('External search error:', err);
      setError('Impossible de charger les résultats externes');
      showError('Erreur lors de la recherche externe');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchResults();
  }, [query, category, source]);

  const handleAdd = async (result: ExternalSearchResult) => {
    if (!onAdd) return;

    setAddingIds(prev => new Set(prev.add(result.external_id)));

    try {
      await onAdd(result);
      showSuccess(`${result.title} ajouté avec succès`);
    } catch (err) {
      showError('Erreur lors de l\'ajout');
    } finally {
      setAddingIds(prev => {
        const newSet = new Set(prev);
        newSet.delete(result.external_id);
        return newSet;
      });
    }
  };

  const handleSelect = (result: ExternalSearchResult) => {
    onSelect?.(result);
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

  const getSourceLabel = (source: string) => {
    const labels = {
      'tmdb': 'TMDB',
      'spotify': 'Spotify',
      'openlibrary': 'OpenLibrary',
      'google_books': 'Google Books'
    };
    return labels[source as keyof typeof labels] || source;
  };

  const formatDate = (dateString?: string) => {
    if (!dateString) return null;
    
    try {
      const date = new Date(dateString);
      return date.getFullYear().toString();
    } catch {
      return null;
    }
  };

  if (loading) {
    return (
      <Box>
        <Grid container spacing={2}>
          {Array.from({ length: 6 }).map((_, index) => (
            <Grid item xs={12} sm={6} md={4} key={index}>
              <Card>
                <Skeleton variant="rectangular" height={200} />
                <CardContent>
                  <Skeleton variant="text" width="80%" height={24} />
                  <Skeleton variant="text" width="60%" height={20} sx={{ mt: 1 }} />
                  <Skeleton variant="text" width="100%" height={40} sx={{ mt: 1 }} />
                </CardContent>
              </Card>
            </Grid>
          ))}
        </Grid>
      </Box>
    );
  }

  if (error) {
    return (
      <Alert severity="error" sx={{ mb: 2 }}>
        {error}
      </Alert>
    );
  }

  if (results.length === 0) {
    return (
      <Box sx={{ textAlign: 'center', py: 4 }}>
        <Typography variant="body1" color="text.secondary" gutterBottom>
          Aucun résultat trouvé pour "{query}"
        </Typography>
        <Typography variant="body2" color="text.secondary">
          Essayez avec d'autres mots-clés ou une catégorie différente
        </Typography>
      </Box>
    );
  }

  return (
    <Box>
      <Typography variant="h6" sx={{ mb: 2, display: 'flex', alignItems: 'center', gap: 1 }}>
        Résultats externes
        <Chip 
          label={`${results.length} résultat${results.length > 1 ? 's' : ''}`} 
          size="small" 
          color="primary" 
        />
      </Typography>
      
      <Grid container spacing={2}>
        {results.map((result) => (
          <Grid item xs={12} sm={6} md={4} key={result.external_id}>
            <Card 
              sx={{ 
                height: '100%',
                display: 'flex',
                flexDirection: 'column',
                transition: 'transform 0.2s, box-shadow 0.2s',
                cursor: 'pointer',
                '&:hover': {
                  transform: 'translateY(-4px)',
                  boxShadow: 4
                }
              }}
              onClick={() => handleSelect(result)}
            >
              {/* Poster/Image */}
              <CardMedia
                component="img"
                height="200"
                image={result.poster_url || '/placeholder-image.jpg'}
                alt={result.title}
                sx={{ objectFit: 'cover' }}
                onError={(e) => {
                  const target = e.target as HTMLImageElement;
                  target.src = '/placeholder-image.jpg';
                }}
              />
              
              <CardContent sx={{ flexGrow: 1, display: 'flex', flexDirection: 'column' }}>
                {/* En-tête avec titre et source */}
                <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', mb: 1 }}>
                  <Typography 
                    variant="h6" 
                    component="h3" 
                    sx={{ 
                      fontSize: '1rem',
                      fontWeight: 'medium',
                      lineHeight: 1.2,
                      flexGrow: 1,
                      mr: 1
                    }}
                  >
                    {result.title}
                  </Typography>
                  <Chip
                    label={getSourceLabel(result.source)}
                    size="small"
                    sx={{ 
                      fontSize: '0.7rem',
                      height: 20,
                      backgroundColor: getCategoryColor(result.category),
                      color: 'white'
                    }}
                  />
                </Box>

                {/* Métadonnées */}
                <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 1 }}>
                  {result.rating && (
                    <Box sx={{ display: 'flex', alignItems: 'center', gap: 0.5 }}>
                      <StarIcon sx={{ fontSize: 16, color: 'warning.main' }} />
                      <Typography variant="caption">
                        {result.rating.toFixed(1)}
                      </Typography>
                    </Box>
                  )}
                  
                  {result.release_date && (
                    <Box sx={{ display: 'flex', alignItems: 'center', gap: 0.5 }}>
                      <CalendarIcon sx={{ fontSize: 14, color: 'text.secondary' }} />
                      <Typography variant="caption" color="text.secondary">
                        {formatDate(result.release_date)}
                      </Typography>
                    </Box>
                  )}
                </Box>

                {/* Description */}
                <Typography 
                  variant="body2" 
                  color="text.secondary" 
                  sx={{ 
                    mb: 2,
                    flexGrow: 1,
                    display: '-webkit-box',
                    WebkitLineClamp: 3,
                    WebkitBoxOrient: 'vertical',
                    overflow: 'hidden'
                  }}
                >
                  {result.description || 'Aucune description disponible'}
                </Typography>

                {/* Actions */}
                <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                  <Chip
                    label={result.category_display}
                    size="small"
                    sx={{ 
                      backgroundColor: getCategoryColor(result.category),
                      color: 'white',
                      fontSize: '0.7rem'
                    }}
                  />
                  
                  <Box sx={{ display: 'flex', gap: 1 }}>
                    <Tooltip title="Voir les détails">
                      <IconButton size="small" onClick={(e) => {
                        e.stopPropagation();
                        handleSelect(result);
                      }}>
                        <InfoIcon fontSize="small" />
                      </IconButton>
                    </Tooltip>
                    
                    {onAdd && (
                      <Tooltip title="Ajouter à ma liste">
                        <IconButton 
                          size="small" 
                          color="primary"
                          disabled={addingIds.has(result.external_id)}
                          onClick={(e) => {
                            e.stopPropagation();
                            handleAdd(result);
                          }}
                        >
                          <AddIcon fontSize="small" />
                        </IconButton>
                      </Tooltip>
                    )}
                  </Box>
                </Box>
              </CardContent>
            </Card>
          </Grid>
        ))}
      </Grid>
    </Box>
  );
};

export default ExternalSearchResults;
