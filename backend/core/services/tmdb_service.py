"""
Service pour l'intégration avec l'API TMDB (The Movie Database)
Gère la recherche et l'enrichissement de films et séries
"""

import requests
from typing import Dict, List, Optional, Any
from django.conf import settings
from ..models import APICache
import hashlib
import logging

logger = logging.getLogger(__name__)


class TMDBService:
    """Service pour l'API TMDB"""
    
    BASE_URL = "https://api.themoviedb.org/3"
    IMAGE_BASE_URL = "https://image.tmdb.org/t/p"
    
    def __init__(self):
        self.api_key = getattr(settings, 'TMDB_API_KEY', None)
        if not self.api_key:
            logger.warning("TMDB_API_KEY not configured in settings")
            self.api_key = "demo_key"  # Pour les tests
    
    def _make_request(self, endpoint: str, params: Dict = None) -> Optional[Dict]:
        """Effectue une requête vers l'API TMDB avec gestion d'erreur et cache"""
        if params is None:
            params = {}
        
        params['api_key'] = self.api_key
        params['language'] = 'fr-FR'  # Priorité au français
        
        # Clé de cache basée sur l'endpoint et les paramètres
        cache_key = f"tmdb_{hashlib.md5(f'{endpoint}_{str(params)}'.encode()).hexdigest()}"
        
        # Vérifier le cache d'abord
        cached_data = APICache.get_cached_data(cache_key)
        if cached_data:
            return cached_data
        
        try:
            url = f"{self.BASE_URL}{endpoint}"
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            
            # Mettre en cache pour 6 heures
            APICache.set_cached_data(cache_key, data, ttl_hours=6)
            
            return data
            
        except requests.RequestException as e:
            logger.error(f"TMDB API error for {endpoint}: {e}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error with TMDB API: {e}")
            return None
    
    def search_movies(self, query: str, limit: int = 10) -> List[Dict]:
        """Recherche de films"""
        data = self._make_request('/search/movie', {'query': query})
        if not data:
            return []
        
        results = []
        for movie in data.get('results', [])[:limit]:
            results.append(self._format_movie(movie))
        
        return results
    
    def search_tv_shows(self, query: str, limit: int = 10) -> List[Dict]:
        """Recherche de séries TV"""
        data = self._make_request('/search/tv', {'query': query})
        if not data:
            return []
        
        results = []
        for show in data.get('results', [])[:limit]:
            results.append(self._format_tv_show(show))
        
        return results
    
    def get_movie_details(self, movie_id: int) -> Optional[Dict]:
        """Récupère les détails complets d'un film"""
        data = self._make_request(f'/movie/{movie_id}')
        if data:
            return self._format_movie_details(data)
        return None
    
    def get_tv_show_details(self, tv_id: int) -> Optional[Dict]:
        """Récupère les détails complets d'une série"""
        data = self._make_request(f'/tv/{tv_id}')
        if data:
            return self._format_tv_show_details(data)
        return None
    
    def get_trending_movies(self, time_window: str = 'week', limit: int = 20) -> List[Dict]:
        """Récupère les films tendance"""
        data = self._make_request(f'/trending/movie/{time_window}')
        if not data:
            return []
        
        results = []
        for movie in data.get('results', [])[:limit]:
            results.append(self._format_movie(movie))
        
        return results
    
    def get_trending_tv_shows(self, time_window: str = 'week', limit: int = 20) -> List[Dict]:
        """Récupère les séries tendance"""
        data = self._make_request(f'/trending/tv/{time_window}')
        if not data:
            return []
        
        results = []
        for show in data.get('results', [])[:limit]:
            results.append(self._format_tv_show(show))
        
        return results
    
    def get_similar_movies(self, movie_id: int, limit: int = 10) -> List[Dict]:
        """Récupère les films similaires"""
        data = self._make_request(f'/movie/{movie_id}/similar')
        if not data:
            return []
        
        results = []
        for movie in data.get('results', [])[:limit]:
            results.append(self._format_movie(movie))
        
        return results
    
    def get_similar_tv_shows(self, tv_id: int, limit: int = 10) -> List[Dict]:
        """Récupère les séries similaires"""
        data = self._make_request(f'/tv/{tv_id}/similar')
        if not data:
            return []
        
        results = []
        for show in data.get('results', [])[:limit]:
            results.append(self._format_tv_show(show))
        
        return results
    
    def get_recommendations_movies(self, movie_id: int, limit: int = 10) -> List[Dict]:
        """Récupère les recommandations de films basées sur TMDB"""
        data = self._make_request(f'/movie/{movie_id}/recommendations')
        if not data:
            return []
        
        results = []
        for movie in data.get('results', [])[:limit]:
            results.append(self._format_movie(movie))
        
        return results
    
    def get_recommendations_tv_shows(self, tv_id: int, limit: int = 10) -> List[Dict]:
        """Récupère les recommandations de séries basées sur TMDB"""
        data = self._make_request(f'/tv/{tv_id}/recommendations')
        if not data:
            return []
        
        results = []
        for show in data.get('results', [])[:limit]:
            results.append(self._format_tv_show(show))
        
        return results
    
    def _format_movie(self, movie_data: Dict) -> Dict:
        """Formate les données d'un film pour usage interne"""
        return {
            'external_id': str(movie_data.get('id')),
            'title': movie_data.get('title', ''),
            'original_title': movie_data.get('original_title', ''),
            'description': movie_data.get('overview', ''),
            'poster_url': self._get_image_url(movie_data.get('poster_path'), 'w500'),
            'backdrop_url': self._get_image_url(movie_data.get('backdrop_path'), 'w1280'),
            'rating': movie_data.get('vote_average'),
            'vote_count': movie_data.get('vote_count'),
            'release_date': movie_data.get('release_date'),
            'genre_ids': movie_data.get('genre_ids', []),
            'popularity': movie_data.get('popularity'),
            'adult': movie_data.get('adult', False),
            'source': 'tmdb',
            'type': 'movie'
        }
    
    def _format_tv_show(self, show_data: Dict) -> Dict:
        """Formate les données d'une série pour usage interne"""
        return {
            'external_id': str(show_data.get('id')),
            'title': show_data.get('name', ''),
            'original_title': show_data.get('original_name', ''),
            'description': show_data.get('overview', ''),
            'poster_url': self._get_image_url(show_data.get('poster_path'), 'w500'),
            'backdrop_url': self._get_image_url(show_data.get('backdrop_path'), 'w1280'),
            'rating': show_data.get('vote_average'),
            'vote_count': show_data.get('vote_count'),
            'first_air_date': show_data.get('first_air_date'),
            'genre_ids': show_data.get('genre_ids', []),
            'popularity': show_data.get('popularity'),
            'origin_country': show_data.get('origin_country', []),
            'source': 'tmdb',
            'type': 'tv'
        }
    
    def _format_movie_details(self, movie_data: Dict) -> Dict:
        """Formate les détails complets d'un film"""
        base_info = self._format_movie(movie_data)
        
        # Informations détaillées supplémentaires
        base_info.update({
            'runtime': movie_data.get('runtime'),
            'budget': movie_data.get('budget'),
            'revenue': movie_data.get('revenue'),
            'genres': [g['name'] for g in movie_data.get('genres', [])],
            'production_companies': [c['name'] for c in movie_data.get('production_companies', [])],
            'production_countries': [c['name'] for c in movie_data.get('production_countries', [])],
            'spoken_languages': [l['name'] for l in movie_data.get('spoken_languages', [])],
            'status': movie_data.get('status'),
            'tagline': movie_data.get('tagline'),
            'homepage': movie_data.get('homepage'),
            'imdb_id': movie_data.get('imdb_id')
        })
        
        return base_info
    
    def _format_tv_show_details(self, show_data: Dict) -> Dict:
        """Formate les détails complets d'une série"""
        base_info = self._format_tv_show(show_data)
        
        # Informations détaillées supplémentaires
        base_info.update({
            'number_of_episodes': show_data.get('number_of_episodes'),
            'number_of_seasons': show_data.get('number_of_seasons'),
            'episode_run_time': show_data.get('episode_run_time', []),
            'genres': [g['name'] for g in show_data.get('genres', [])],
            'networks': [n['name'] for n in show_data.get('networks', [])],
            'production_companies': [c['name'] for c in show_data.get('production_companies', [])],
            'created_by': [c['name'] for c in show_data.get('created_by', [])],
            'status': show_data.get('status'),
            'type': show_data.get('type'),
            'homepage': show_data.get('homepage'),
            'last_air_date': show_data.get('last_air_date'),
            'in_production': show_data.get('in_production', False)
        })
        
        return base_info
    
    def _get_image_url(self, path: Optional[str], size: str = 'w500') -> Optional[str]:
        """Construit l'URL complète pour une image TMDB"""
        if not path:
            return None
        return f"{self.IMAGE_BASE_URL}/{size}{path}"
    
    def get_genres_mapping(self, media_type: str = 'movie') -> Dict[int, str]:
        """Récupère la liste des genres TMDB"""
        data = self._make_request(f'/genre/{media_type}/list')
        if not data:
            return {}
        
        return {genre['id']: genre['name'] for genre in data.get('genres', [])}