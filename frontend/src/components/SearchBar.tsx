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
  CircularProgress
} from '@mui/material';
import {
  Search as SearchIcon,
  Clear as ClearIcon,
  Add as AddIcon
} from '@mui/icons-material';

interface SearchResult {
  title: string;
  description: string;
  category: string;
  category_display: string;
  popularity: number;
}

interface SearchBarProps {
  category?: string;
  onSelect?: (result: SearchResult) => void;
  onQuickAdd?: (result: SearchResult) => void;
  placeholder?: string;
  autoFocus?: boolean;
}

const SearchBar: React.FC<SearchBarProps> = ({
  category,
  onSelect,
  onQuickAdd,
  placeholder = "Rechercher...",
  autoFocus = false
}) => {
  const [query, setQuery] = useState('');
  const [results, setResults] = useState<SearchResult[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [showResults, setShowResults] = useState(false);
  const [error, setError] = useState('');
  
  const searchTimeoutRef = useRef<NodeJS.Timeout>();
  const inputRef = useRef<HTMLInputElement>();

  // Debounced search function
  const searchItems = useCallback(async (searchQuery: string) => {
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
        limit: '8'
      });
      
      if (category) {
        params.append('category', category);
      }

      const response = await fetch(`http://localhost:8000/api/search/?${params}`, {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });

      if (!response.ok) {
        throw new Error('Erreur lors de la recherche');
      }

      const data = await response.json();
      setResults(data.results || []);
      setShowResults(true);
    } catch (err) {
      console.error('Search error:', err);
      setError('Erreur lors de la recherche');
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
      searchItems(query);
    }, 300);

    return () => {
      if (searchTimeoutRef.current) {
        clearTimeout(searchTimeoutRef.current);
      }
    };
  }, [query, searchItems]);

  const handleInputChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    setQuery(event.target.value);
  };

  const handleResultClick = (result: SearchResult) => {
    onSelect?.(result);
    setQuery(result.title);
    setShowResults(false);
  };

  const handleQuickAdd = (event: React.MouseEvent, result: SearchResult) => {
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

  const getCategoryColor = (cat: string) => {
    const colors = {
      'FILMS': '#e53e3e',
      'SERIES': '#3182ce', 
      'MUSIQUE': '#38a169',
      'LIVRES': '#d69e2e'
    };
    return colors[cat as keyof typeof colors] || '#718096';
  };

  return (
    <Box sx={{ position: 'relative', width: '100%' }}>
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
            '& .MuiOutlinedInput-root': {
              '&:hover fieldset': {
                borderColor: 'primary.main',
              },
              '&.Mui-focused fieldset': {
                borderWidth: 2,
              }
            }
          }
        }}
      />

      {/* Search Results Dropdown */}
      {showResults && (results.length > 0 || error) && (
        <Paper
          elevation={4}
          sx={{
            position: 'absolute',
            top: '100%',
            left: 0,
            right: 0,
            zIndex: 1000,
            maxHeight: 300,
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
                  key={index}
                  button
                  onClick={() => handleResultClick(result)}
                  sx={{
                    py: 1,
                    px: 2,
                    borderBottom: index < results.length - 1 ? '1px solid' : 'none',
                    borderBottomColor: 'divider',
                    '&:hover': {
                      backgroundColor: 'action.hover'
                    }
                  }}
                >
                  <ListItemText
                    primary={
                      <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
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
                              fontSize: '0.75rem',
                              height: 20,
                              backgroundColor: getCategoryColor(result.category),
                              color: 'white',
                              '& .MuiChip-label': {
                                px: 1
                              }
                            }}
                          />
                        )}
                        {result.popularity > 1 && (
                          <Typography
                            variant="caption"
                            sx={{
                              color: 'text.secondary',
                              fontSize: '0.7rem',
                              fontStyle: 'italic'
                            }}
                          >
                            ({result.popularity} utilisateurs)
                          </Typography>
                        )}
                      </Box>
                    }
                    secondary={result.description && (
                      <Typography
                        variant="body2"
                        sx={{
                          fontSize: { xs: '0.75rem', sm: '0.875rem' },
                          color: 'text.secondary',
                          mt: 0.5
                        }}
                      >
                        {result.description}
                      </Typography>
                    )}
                  />
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

export default SearchBar;