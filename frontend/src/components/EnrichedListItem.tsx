import React, { useState } from 'react';
import {
  Card,
  CardContent,
  CardMedia,
  Typography,
  Box,
  Chip,
  Rating,
  IconButton,
  Tooltip,
  Badge,
  Button,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  CircularProgress
} from '@mui/material';
import {
  Edit as EditIcon,
  Delete as DeleteIcon,
  Star as StarIcon,
  Refresh as RefreshIcon,
  OpenInNew as OpenInNewIcon,
  Movie as MovieIcon,
  Tv as TvIcon,
  MusicNote as MusicIcon,
  MenuBook as BookIcon
} from '@mui/icons-material';

interface ExternalReference {
  source: string;
  poster_url?: string;
  backdrop_url?: string;
  rating?: number;
  release_date?: string;
  metadata?: Record<string, any>;
}

interface EnrichedListItemProps {
  id: number;
  title: string;
  description: string;
  position: number;
  category: string;
  external_ref?: ExternalReference;
  onEdit?: () => void;
  onDelete?: () => void;
  onEnrich?: () => void;
  isEnriching?: boolean;
}

const EnrichedListItem: React.FC<EnrichedListItemProps> = ({
  id,
  title,
  description,
  position,
  category,
  external_ref,
  onEdit,
  onDelete,
  onEnrich,
  isEnriching = false
}) => {
  const [imageError, setImageError] = useState(false);
  const [detailsOpen, setDetailsOpen] = useState(false);

  const getCategoryIcon = () => {
    switch (category) {
      case 'FILMS':
        return <MovieIcon />;
      case 'SERIES':
        return <TvIcon />;
      case 'MUSIQUE':
        return <MusicIcon />;
      case 'LIVRES':
        return <BookIcon />;
      default:
        return null;
    }
  };

  const getCategoryColor = () => {
    const colors = {
      'FILMS': '#e53e3e',
      'SERIES': '#3182ce',
      'MUSIQUE': '#38a169',
      'LIVRES': '#d69e2e'
    };
    return colors[category as keyof typeof colors] || '#718096';
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

  const formatReleaseDate = (dateStr?: string) => {
    if (!dateStr) return null;
    try {
      const date = new Date(dateStr);
      return date.getFullYear();
    } catch {
      return dateStr;
    }
  };

  const renderMetadataDetails = () => {
    if (!external_ref?.metadata) return null;

    const metadata = external_ref.metadata;
    return (
      <Box sx={{ mt: 2 }}>
        {metadata.genres && (
          <Box sx={{ mb: 1 }}>
            <Typography variant="body2" color="text.secondary" gutterBottom>
              Genres:
            </Typography>
            <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 0.5 }}>
              {metadata.genres.slice(0, 4).map((genre: string, index: number) => (
                <Chip
                  key={index}
                  label={genre}
                  size="small"
                  variant="outlined"
                  sx={{ fontSize: '0.7rem' }}
                />
              ))}
            </Box>
          </Box>
        )}

        {metadata.runtime && (
          <Typography variant="body2" color="text.secondary">
            Durée: {metadata.runtime} min
          </Typography>
        )}

        {metadata.artists && (
          <Typography variant="body2" color="text.secondary">
            Artistes: {Array.isArray(metadata.artists) ? metadata.artists.join(', ') : metadata.artists}
          </Typography>
        )}

        {metadata.page_count && (
          <Typography variant="body2" color="text.secondary">
            Pages: {metadata.page_count}
          </Typography>
        )}

        {metadata.vote_count && (
          <Typography variant="body2" color="text.secondary">
            {metadata.vote_count} votes
          </Typography>
        )}
      </Box>
    );
  };

  return (
    <>
      <Card 
        sx={{ 
          display: 'flex',
          mb: 2,
          position: 'relative',
          transition: 'transform 0.2s, box-shadow 0.2s',
          '&:hover': {
            transform: 'translateY(-2px)',
            boxShadow: 4
          }
        }}
      >
        {/* Image/Poster */}
        <Box sx={{ position: 'relative', flexShrink: 0 }}>
          {external_ref?.poster_url && !imageError ? (
            <CardMedia
              component="img"
              sx={{ 
                width: { xs: 80, sm: 120 },
                height: { xs: 120, sm: 180 },
                objectFit: 'cover'
              }}
              image={external_ref.poster_url}
              alt={title}
              onError={() => setImageError(true)}
            />
          ) : (
            <Box
              sx={{
                width: { xs: 80, sm: 120 },
                height: { xs: 120, sm: 180 },
                backgroundColor: 'grey.200',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                color: getCategoryColor()
              }}
            >
              {getCategoryIcon()}
            </Box>
          )}

          {/* Position badge */}
          <Box
            sx={{
              position: 'absolute',
              top: 8,
              left: 8,
              backgroundColor: 'primary.main',
              color: 'white',
              borderRadius: '50%',
              width: 24,
              height: 24,
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              fontSize: '0.75rem',
              fontWeight: 'bold'
            }}
          >
            {position}
          </Box>

          {/* External source badge */}
          {external_ref && (
            <Tooltip title={`Enrichi par ${getSourceLabel(external_ref.source)}`}>
              <Box
                sx={{
                  position: 'absolute',
                  bottom: 4,
                  left: 4,
                  backgroundColor: 'success.main',
                  color: 'white',
                  borderRadius: 1,
                  px: 0.5,
                  py: 0.25,
                  fontSize: '0.6rem',
                  fontWeight: 'bold'
                }}
              >
                {getSourceLabel(external_ref.source)}
              </Box>
            </Tooltip>
          )}
        </Box>

        {/* Content */}
        <CardContent sx={{ flex: 1, position: 'relative', py: 1 }}>
          <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', mb: 1 }}>
            <Typography 
              variant="h6" 
              component="h3"
              sx={{ 
                fontSize: { xs: '0.9rem', sm: '1.1rem' },
                fontWeight: 'medium',
                lineHeight: 1.2,
                mr: 1
              }}
            >
              {title}
            </Typography>

            {/* Actions */}
            <Box sx={{ display: 'flex', gap: 0.5 }}>
              {onEnrich && (
                <Tooltip title="Enrichir avec des métadonnées">
                  <IconButton
                    size="small"
                    onClick={onEnrich}
                    disabled={isEnriching}
                    color="primary"
                  >
                    {isEnriching ? <CircularProgress size={16} /> : <RefreshIcon />}
                  </IconButton>
                </Tooltip>
              )}
              
              {onEdit && (
                <IconButton size="small" onClick={onEdit} color="primary">
                  <EditIcon fontSize="small" />
                </IconButton>
              )}
              
              {onDelete && (
                <IconButton size="small" onClick={onDelete} color="error">
                  <DeleteIcon fontSize="small" />
                </IconButton>
              )}
            </Box>
          </Box>

          {/* Rating and Release Date */}
          {external_ref && (
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 1 }}>
              {external_ref.rating && (
                <Box sx={{ display: 'flex', alignItems: 'center', gap: 0.5 }}>
                  <Rating
                    value={external_ref.rating / 2}
                    readOnly
                    size="small"
                    precision={0.1}
                    max={5}
                  />
                  <Typography variant="caption" color="text.secondary">
                    ({external_ref.rating.toFixed(1)})
                  </Typography>
                </Box>
              )}

              {external_ref.release_date && (
                <Typography variant="caption" color="text.secondary">
                  {formatReleaseDate(external_ref.release_date)}
                </Typography>
              )}
            </Box>
          )}

          {/* Description */}
          <Typography 
            variant="body2" 
            color="text.secondary"
            sx={{ 
              fontSize: { xs: '0.75rem', sm: '0.875rem' },
              lineHeight: 1.4,
              display: '-webkit-box',
              WebkitLineClamp: { xs: 2, sm: 3 },
              WebkitBoxOrient: 'vertical',
              overflow: 'hidden',
              mb: external_ref?.metadata ? 1 : 0
            }}
          >
            {description}
          </Typography>

          {/* Quick metadata preview */}
          {external_ref?.metadata && (
            <Box sx={{ mt: 1 }}>
              {external_ref.metadata.genres && (
                <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 0.5, mb: 0.5 }}>
                  {external_ref.metadata.genres.slice(0, 3).map((genre: string, index: number) => (
                    <Chip
                      key={index}
                      label={genre}
                      size="small"
                      variant="outlined"
                      sx={{ fontSize: '0.65rem', height: 20 }}
                    />
                  ))}
                </Box>
              )}
              
              <Button
                size="small"
                onClick={() => setDetailsOpen(true)}
                startIcon={<OpenInNewIcon />}
                sx={{ fontSize: '0.7rem', p: 0.5 }}
              >
                Voir détails
              </Button>
            </Box>
          )}
        </CardContent>
      </Card>

      {/* Details Dialog */}
      <Dialog
        open={detailsOpen}
        onClose={() => setDetailsOpen(false)}
        maxWidth="sm"
        fullWidth
      >
        <DialogTitle>
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
            {getCategoryIcon()}
            {title}
            {external_ref && (
              <Chip
                label={getSourceLabel(external_ref.source)}
                size="small"
                color="primary"
              />
            )}
          </Box>
        </DialogTitle>
        
        <DialogContent>
          {external_ref?.backdrop_url && !imageError && (
            <Box sx={{ mb: 2 }}>
              <img
                src={external_ref.backdrop_url}
                alt={`${title} backdrop`}
                style={{
                  width: '100%',
                  maxHeight: 200,
                  objectFit: 'cover',
                  borderRadius: 8
                }}
                onError={() => setImageError(true)}
              />
            </Box>
          )}

          <Typography variant="body1" paragraph>
            {description}
          </Typography>

          {renderMetadataDetails()}
        </DialogContent>
        
        <DialogActions>
          <Button onClick={() => setDetailsOpen(false)}>
            Fermer
          </Button>
        </DialogActions>
      </Dialog>
    </>
  );
};

export default EnrichedListItem;