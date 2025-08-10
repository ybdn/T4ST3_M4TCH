from . import tmdb_service  # noqa: F401
from . import spotify_service  # noqa: F401
from . import books_service  # noqa: F401

# Ne pas ré-exporter RecommendationService ici pour éviter l'import circulaire
__all__ = []

