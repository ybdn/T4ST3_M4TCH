import React, { useState, useEffect, useRef, useCallback } from 'react';
import {
  TextField,
  Box,
  List,
  ListItem,
  ListItemText,
  Paper,
  Typography,
  Chip,
  IconButton,
  InputAdornment,
  CircularProgress,
  Avatar,
  Button,
  FormControl,
  Select,
  MenuItem,
  InputLabel
} from '@mui/material';
import {
  Search as SearchIcon,
  Clear as ClearIcon,
  Add as AddIcon,
  Star as StarIcon,
  Movie as MovieIcon,
  Tv as TvIcon,
  MusicNote as MusicIcon,
  MenuBook as BookIcon
} from '@mui/icons-material';

interface ExternalSearchResult {
  external_id: string;
  title: string;
  description: string;
  poster_url?: string;
  rating?: number;
  source: string;
  type: string;
  category: string;
  category_display: string;
  artists?: string[];
  genres?: string[];
  release_date?: string;
  popularity?: number;
}

interface ExternalSearchBarProps {
  category?: string;
  onSelect?: (result: ExternalSearchResult) => void;
  onQuickAdd?: (result: ExternalSearchResult) => void;
  placeholder?: string;
  autoFocus?: boolean;
  showSourceFilter?: boolean;
}

const ExternalSearchBar: React.FC<ExternalSearchBarProps> = ({
  category,
  onSelect,
  onQuickAdd,
  placeholder = "Rechercher dans les bases de données externes...",
  autoFocus = false,
  showSourceFilter = true
}) => {
  const [query, setQuery] = useState('');
  const [results, setResults] = useState<ExternalSearchResult[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [showResults, setShowResults] = useState(false);
  const [error, setError] = useState('');
  const [selectedSource, setSelectedSource] = useState('');
  
  const searchTimeoutRef = useRef<NodeJS.Timeout>();
  const inputRef = useRef<HTMLInputElement>();

  const sources = [
    { value: '', label: 'Toutes les sources' },
    { value: 'tmdb', label: 'TMDB (Films/Séries)', icon: '🎬' },
    { value: 'spotify', label: 'Spotify (Musique)', icon: '🎵' },
    { value: 'books', label: 'Livres (OpenLibrary/Google)', icon: '📚' }
  ];

  // Debounced search function
  const searchExternal = useCallback(async (searchQuery: string, source: string = '') => {
    if (!searchQuery.trim() || searchQuery.length < 2) {
      setResults([]);
      setShowResults(false);
      return;
    }

    setIsLoading(true);
    setError('');

    try {
      const token = localStorage.getItem('access_token');
      const params = new URLSearchParams({
        q: searchQuery,
        limit: '10'
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
      setResults(data.results || []);
      setShowResults(true);
    } catch (err) {
      console.error('External search error:', err);
      setError('Erreur lors de la recherche externe');
      setResults([]);
    } finally {
      setIsLoading(false);
    }
  }, [category]);

  // Debounce search queries
  useEffect(() => {
    if (searchTimeoutRef.current) {
      clearTimeout(searchTimeoutRef.current);
    }

    searchTimeoutRef.current = setTimeout(() => {
      searchExternal(query, selectedSource);
    }, 500); // Plus long délai pour APIs externes

    return () => {
      if (searchTimeoutRef.current) {
        clearTimeout(searchTimeoutRef.current);
      }
    };
  }, [query, selectedSource, searchExternal]);

  const handleInputChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    setQuery(event.target.value);
  };

  const handleResultClick = (result: ExternalSearchResult) => {
    onSelect?.(result);
    setQuery(result.title);
    setShowResults(false);
  };

  const handleQuickAdd = (event: React.MouseEvent, result: ExternalSearchResult) => {
    event.stopPropagation();
    onQuickAdd?.(result);
  };

  const handleClear = () => {
    setQuery('');
    setResults([]);
    setShowResults(false);
    inputRef.current?.focus();
  };

  const handleFocus = () => {
    if (results.length > 0) {
      setShowResults(true);
    }
  };

  const handleBlur = () => {
    // Delay hiding results to allow clicks on result items
    setTimeout(() => {
      setShowResults(false);
    }, 200);
  };

  const getCategoryIcon = (cat: string) => {
    const icons = {
      'FILMS': <MovieIcon fontSize="small" />,
      'SERIES': <TvIcon fontSize="small" />,
      'MUSIQUE': <MusicIcon fontSize="small" />,
      'LIVRES': <BookIcon fontSize="small" />
    };
    return icons[cat as keyof typeof icons] || null;
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

  const getSourceBadgeColor = (source: string) => {
    const colors = {
      'tmdb': '#0d7377',
      'spotify': '#1db954',
      'openlibrary': '#f39c12',
      'google_books': '#4285f4'
    };
    return colors[source as keyof typeof colors] || '#718096';
  };

  return (
    <Box sx={{ position: 'relative', width: '100%' }}>
      {/* Source Filter */}
      {showSourceFilter && (
        <FormControl fullWidth sx={{ mb: 2 }}>
          <InputLabel>Source de recherche</InputLabel>
          <Select
            value={selectedSource}
            onChange={(e) => setSelectedSource(e.target.value)}
            label="Source de recherche"
          >
            {sources.map((source) => (
              <MenuItem key={source.value} value={source.value}>
                <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                  {source.icon && <span>{source.icon}</span>}
                  {source.label}
                </Box>
              </MenuItem>
            ))}
          </Select>
        </FormControl>
      )}

      {/* Search Input */}
      <TextField
        ref={inputRef}
        fullWidth
        value={query}
        onChange={handleInputChange}
        onFocus={handleFocus}
        onBlur={handleBlur}
        placeholder={placeholder}
        autoFocus={autoFocus}
        variant="outlined"
        InputProps={{
          startAdornment: (
            <InputAdornment position="start">
              {isLoading ? (
                <CircularProgress size={20} />
              ) : (
                <SearchIcon color="action" />
              )}
            </InputAdornment>
          ),
          endAdornment: query && (
            <InputAdornment position="end">
              <IconButton
                size="small"
                onClick={handleClear}
                edge="end"
                aria-label="clear"
              >
                <ClearIcon />
              </IconButton>
            </InputAdornment>
          ),
          sx: {
            fontSize: { xs: '0.875rem', sm: '1rem' },
          }
        }}
      />

      {/* Search Results Dropdown */}
      {showResults && (results.length > 0 || error) && (
        <Paper
          elevation={4}
          sx={{
            position: 'absolute',
            top: showSourceFilter ? 'calc(100% + 60px)' : '100%',
            left: 0,
            right: 0,
            zIndex: 1000,
            maxHeight: 400,
            overflow: 'auto',
            mt: 1,
            border: '1px solid',
            borderColor: 'divider'
          }}
        >
          {error ? (
            <Box sx={{ p: 2, textAlign: 'center' }}>
              <Typography variant="body2" color="error">
                {error}
              </Typography>
            </Box>
          ) : (
            <List sx={{ py: 0 }}>
              {results.map((result, index) => (
                <ListItem
                  key={`${result.source}-${result.external_id}-${index}`}
                  button
                  onClick={() => handleResultClick(result)}
                  sx={{
                    py: 1.5,
                    px: 2,
                    borderBottom: index < results.length - 1 ? '1px solid' : 'none',
                    borderBottomColor: 'divider',
                    '&:hover': {
                      backgroundColor: 'action.hover'
                    }
                  }}
                >
                  {/* Poster/Image */}
                  <Box sx={{ mr: 2, flexShrink: 0 }}>
                    {result.poster_url ? (
                      <Avatar
                        src={result.poster_url}
                        alt={result.title}
                        variant="rounded"
                        sx={{
                          width: 50,
                          height: 75,
                          bgcolor: getCategoryColor(result.category)
                        }}
                      />
                    ) : (
                      <Avatar
                        variant="rounded"
                        sx={{
                          width: 50,
                          height: 75,
                          bgcolor: getCategoryColor(result.category)
                        }}
                      >
                        {getCategoryIcon(result.category)}
                      </Avatar>
                    )}
                  </Box>

                  {/* Content */}
                  <ListItemText
                    primary={
                      <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 0.5 }}>
                        <Typography 
                          variant="body1" 
                          sx={{ 
                            fontSize: { xs: '0.875rem', sm: '1rem' },
                            fontWeight: 'medium'
                          }}
                        >
                          {result.title}
                        </Typography>
                        
                        {!category && (
                          <Chip
                            label={result.category_display}
                            size="small"
                            sx={{
                              fontSize: '0.7rem',
                              height: 18,
                              backgroundColor: getCategoryColor(result.category),
                              color: 'white'
                            }}
                          />
                        )}

                        {/* Rating */}
                        {result.rating && (
                          <Box sx={{ display: 'flex', alignItems: 'center', gap: 0.5 }}>
                            <StarIcon sx={{ fontSize: 14, color: 'gold' }} />
                            <Typography variant="caption">
                              {result.rating.toFixed(1)}
                            </Typography>
                          </Box>
                        )}
                      </Box>
                    }
                    secondary={
                      <Box>
                        <Typography
                          variant="body2"
                          sx={{
                            fontSize: { xs: '0.75rem', sm: '0.875rem' },
                            color: 'text.secondary',
                            mb: 0.5,
                            display: '-webkit-box',
                            WebkitLineClamp: 2,
                            WebkitBoxOrient: 'vertical',
                            overflow: 'hidden'
                          }}
                        >
                          {result.description}
                        </Typography>

                        {/* Additional info */}
                        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mt: 0.5 }}>
                          <Chip
                            label={result.source.toUpperCase()}
                            size="small"
                            sx={{
                              fontSize: '0.65rem',
                              height: 16,
                              backgroundColor: getSourceBadgeColor(result.source),
                              color: 'white'
                            }}
                          />
                          
                          {result.release_date && (
                            <Typography variant="caption" color="text.secondary">
                              {new Date(result.release_date).getFullYear()}
                            </Typography>
                          )}

                          {result.artists && (
                            <Typography variant="caption" color="text.secondary">
                              par {result.artists.slice(0, 2).join(', ')}
                            </Typography>
                          )}
                        </Box>
                      </Box>
                    }
                  />

                  {/* Quick Add Button */}
                  {onQuickAdd && (
                    <IconButton
                      size="small"
                      color="primary"
                      onClick={(e) => handleQuickAdd(e, result)}
                      sx={{
                        ml: 1,
                        '&:hover': {
                          backgroundColor: 'primary.main',
                          color: 'white'
                        }
                      }}
                    >
                      <AddIcon fontSize="small" />
                    </IconButton>
                  )}
                </ListItem>
              ))}
            </List>
          )}
        </Paper>
      )}
    </Box>
  );
};

export default ExternalSearchBar;