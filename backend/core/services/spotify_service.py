"""
Service pour l'intégration avec l'API Spotify
Gère la recherche et l'enrichissement de contenu musical
"""

import requests
import base64
from typing import Dict, List, Optional, Any
from django.conf import settings
from ..models import APICache
import hashlib
import logging

logger = logging.getLogger(__name__)


class SpotifyService:
    """Service pour l'API Spotify"""
    
    BASE_URL = "https://api.spotify.com/v1"
    TOKEN_URL = "https://accounts.spotify.com/api/token"
    
    def __init__(self):
        self.client_id = getattr(settings, 'SPOTIFY_CLIENT_ID', None)
        self.client_secret = getattr(settings, 'SPOTIFY_CLIENT_SECRET', None)
        
        if not self.client_id or not self.client_secret:
            logger.warning("Spotify credentials not configured in settings")
            # Utiliser des clés de démo pour les tests
            self.client_id = "demo_client_id"
            self.client_secret = "demo_client_secret"
        
        self._access_token = None
    
    def _get_access_token(self) -> Optional[str]:
        """Récupère un token d'accès via Client Credentials Flow"""
        # Vérifier le cache pour le token
        cache_key = "spotify_access_token"
        cached_token = APICache.get_cached_data(cache_key)
        if cached_token:
            self._access_token = cached_token
            return cached_token
        
        # Si pas de credentials valides, retourner None
        if self.client_id == "demo_client_id":
            return None
        
        try:
            # Encoder les credentials
            credentials = f"{self.client_id}:{self.client_secret}"
            encoded_credentials = base64.b64encode(credentials.encode()).decode()
            
            headers = {
                'Authorization': f'Basic {encoded_credentials}',
                'Content-Type': 'application/x-www-form-urlencoded'
            }
            
            data = {'grant_type': 'client_credentials'}
            
            response = requests.post(self.TOKEN_URL, headers=headers, data=data, timeout=10)
            response.raise_for_status()
            
            token_data = response.json()
            access_token = token_data.get('access_token')
            expires_in = token_data.get('expires_in', 3600)
            
            # Cacher le token (moins 5 min pour être sûr)
            APICache.set_cached_data(cache_key, access_token, ttl_hours=(expires_in - 300) / 3600)
            
            self._access_token = access_token
            return access_token
            
        except requests.RequestException as e:
            logger.error(f"Spotify token error: {e}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error getting Spotify token: {e}")
            return None
    
    def _make_request(self, endpoint: str, params: Dict = None) -> Optional[Dict]:
        """Effectue une requête vers l'API Spotify avec gestion d'erreur et cache"""
        # Récupérer le token d'accès
        token = self._get_access_token()
        if not token:
            # Retourner des données de démo si pas de token
            return self._get_demo_data(endpoint, params)
        
        if params is None:
            params = {}
        
        # Clé de cache
        cache_key = f"spotify_{hashlib.md5(f'{endpoint}_{str(params)}'.encode()).hexdigest()}"
        
        # Vérifier le cache
        cached_data = APICache.get_cached_data(cache_key)
        if cached_data:
            return cached_data
        
        try:
            headers = {'Authorization': f'Bearer {token}'}
            url = f"{self.BASE_URL}{endpoint}"
            
            response = requests.get(url, headers=headers, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            
            # Mettre en cache pour 2 heures
            APICache.set_cached_data(cache_key, data, ttl_hours=2)
            
            return data
            
        except requests.RequestException as e:
            logger.error(f"Spotify API error for {endpoint}: {e}")
            return self._get_demo_data(endpoint, params)
        except Exception as e:
            logger.error(f"Unexpected error with Spotify API: {e}")
            return self._get_demo_data(endpoint, params)
    
    def _get_demo_data(self, endpoint: str, params: Dict = None) -> Optional[Dict]:
        """Retourne des données de démo pour les tests"""
        if '/search' in endpoint:
            query = params.get('q', '') if params else ''
            return {
                'tracks': {
                    'items': [
                        {
                            'id': 'demo_track_1',
                            'name': f'Résultat démo pour "{query}"',
                            'artists': [{'name': 'Artiste Démo'}],
                            'album': {
                                'name': 'Album Démo',
                                'images': [
                                    {'url': 'https://via.placeholder.com/640x640?text=Demo+Album', 'height': 640, 'width': 640}
                                ],
                                'release_date': '2023-01-01'
                            },
                            'duration_ms': 210000,
                            'preview_url': None,
                            'popularity': 75,
                            'external_urls': {'spotify': 'https://open.spotify.com/track/demo'}
                        }
                    ]
                },
                'artists': {
                    'items': [
                        {
                            'id': 'demo_artist_1',
                            'name': f'Artiste démo "{query}"',
                            'images': [
                                {'url': 'https://via.placeholder.com/640x640?text=Demo+Artist', 'height': 640, 'width': 640}
                            ],
                            'genres': ['pop', 'demo'],
                            'popularity': 80,
                            'followers': {'total': 50000},
                            'external_urls': {'spotify': 'https://open.spotify.com/artist/demo'}
                        }
                    ]
                },
                'albums': {
                    'items': [
                        {
                            'id': 'demo_album_1',
                            'name': f'Album démo "{query}"',
                            'artists': [{'name': 'Artiste Démo'}],
                            'images': [
                                {'url': 'https://via.placeholder.com/640x640?text=Demo+Album', 'height': 640, 'width': 640}
                            ],
                            'release_date': '2023-01-01',
                            'total_tracks': 12,
                            'album_type': 'album',
                            'external_urls': {'spotify': 'https://open.spotify.com/album/demo'}
                        }
                    ]
                }
            }
        return None
    
    def search_music(self, query: str, limit: int = 10) -> List[Dict]:
        """Recherche de contenu musical (tracks, albums, artists)"""
        params = {
            'q': query,
            'type': 'track,artist,album',
            'limit': limit,
            'market': 'FR'
        }
        
        data = self._make_request('/search', params)
        if not data:
            return []
        
        results = []
        
        # Traiter les pistes
        for track in data.get('tracks', {}).get('items', []):
            results.append(self._format_track(track))
        
        # Traiter les artistes
        for artist in data.get('artists', {}).get('items', []):
            results.append(self._format_artist(artist))
        
        # Traiter les albums
        for album in data.get('albums', {}).get('items', []):
            results.append(self._format_album(album))
        
        return results[:limit]
    
    def search_tracks(self, query: str, limit: int = 10) -> List[Dict]:
        """Recherche spécifique de pistes"""
        params = {
            'q': query,
            'type': 'track',
            'limit': limit,
            'market': 'FR'
        }
        
        data = self._make_request('/search', params)
        if not data:
            return []
        
        results = []
        for track in data.get('tracks', {}).get('items', []):
            results.append(self._format_track(track))
        
        return results
    
    def search_artists(self, query: str, limit: int = 10) -> List[Dict]:
        """Recherche spécifique d'artistes"""
        params = {
            'q': query,
            'type': 'artist',
            'limit': limit
        }
        
        data = self._make_request('/search', params)
        if not data:
            return []
        
        results = []
        for artist in data.get('artists', {}).get('items', []):
            results.append(self._format_artist(artist))
        
        return results
    
    def search_albums(self, query: str, limit: int = 10) -> List[Dict]:
        """Recherche spécifique d'albums"""
        params = {
            'q': query,
            'type': 'album',
            'limit': limit,
            'market': 'FR'
        }
        
        data = self._make_request('/search', params)
        if not data:
            return []
        
        results = []
        for album in data.get('albums', {}).get('items', []):
            results.append(self._format_album(album))
        
        return results
    
    def get_track_details(self, track_id: str) -> Optional[Dict]:
        """Récupère les détails d'une piste"""
        data = self._make_request(f'/tracks/{track_id}')
        if data:
            return self._format_track(data)
        return None
    
    def get_artist_details(self, artist_id: str) -> Optional[Dict]:
        """Récupère les détails d'un artiste"""
        data = self._make_request(f'/artists/{artist_id}')
        if data:
            return self._format_artist(data)
        return None
    
    def get_album_details(self, album_id: str) -> Optional[Dict]:
        """Récupère les détails d'un album"""
        data = self._make_request(f'/albums/{album_id}')
        if data:
            return self._format_album(data)
        return None
    
    def get_artist_top_tracks(self, artist_id: str, country: str = 'FR', limit: int = 10) -> List[Dict]:
        """Récupère les meilleurs titres d'un artiste"""
        data = self._make_request(f'/artists/{artist_id}/top-tracks', {'country': country})
        if not data:
            return []
        
        results = []
        for track in data.get('tracks', [])[:limit]:
            results.append(self._format_track(track))
        
        return results
    
    def get_related_artists(self, artist_id: str, limit: int = 10) -> List[Dict]:
        """Récupère les artistes similaires"""
        data = self._make_request(f'/artists/{artist_id}/related-artists')
        if not data:
            return []
        
        results = []
        for artist in data.get('artists', [])[:limit]:
            results.append(self._format_artist(artist))
        
        return results
    
    def get_album_tracks(self, album_id: str, limit: int = 50) -> List[Dict]:
        """Récupère les pistes d'un album"""
        data = self._make_request(f'/albums/{album_id}/tracks', {'limit': limit})
        if not data:
            return []
        
        results = []
        for track in data.get('items', [])[:limit]:
            results.append(self._format_track(track))
        
        return results
    
    def get_featured_playlists(self, country: str = 'FR', limit: int = 20) -> List[Dict]:
        """Récupère les playlists en vedette"""
        data = self._make_request('/browse/featured-playlists', {
            'country': country,
            'limit': limit
        })
        if not data:
            return []
        
        results = []
        for playlist in data.get('playlists', {}).get('items', [])[:limit]:
            results.append({
                'external_id': playlist.get('id'),
                'title': playlist.get('name'),
                'description': playlist.get('description'),
                'poster_url': self._get_best_image(playlist.get('images', [])),
                'owner': playlist.get('owner', {}).get('display_name'),
                'track_count': playlist.get('tracks', {}).get('total'),
                'source': 'spotify',
                'type': 'playlist'
            })
        
        return results
    
    def get_new_releases(self, country: str = 'FR', limit: int = 20) -> List[Dict]:
        """Récupère les nouvelles sorties"""
        data = self._make_request('/browse/new-releases', {
            'country': country,
            'limit': limit
        })
        if not data:
            return []
        
        results = []
        for album in data.get('albums', {}).get('items', [])[:limit]:
            results.append(self._format_album(album))
        
        return results
    
    def _format_track(self, track_data: Dict) -> Dict:
        """Formate les données d'une piste pour usage interne"""
        album = track_data.get('album', {})
        artists = track_data.get('artists', [])
        
        return {
            'external_id': track_data.get('id'),
            'title': track_data.get('name', ''),
            'artists': [artist.get('name', '') for artist in artists],
            'album': album.get('name', ''),
            'description': f"{', '.join([a.get('name', '') for a in artists])} - {album.get('name', '')}",
            'poster_url': self._get_best_image(album.get('images', [])),
            'duration_ms': track_data.get('duration_ms'),
            'preview_url': track_data.get('preview_url'),
            'popularity': track_data.get('popularity'),
            'release_date': album.get('release_date'),
            'explicit': track_data.get('explicit', False),
            'external_urls': track_data.get('external_urls', {}),
            'source': 'spotify',
            'type': 'track'
        }
    
    def _format_artist(self, artist_data: Dict) -> Dict:
        """Formate les données d'un artiste pour usage interne"""
        return {
            'external_id': artist_data.get('id'),
            'title': artist_data.get('name', ''),
            'description': f"Artiste - {', '.join(artist_data.get('genres', [])[:3])}",
            'poster_url': self._get_best_image(artist_data.get('images', [])),
            'genres': artist_data.get('genres', []),
            'popularity': artist_data.get('popularity'),
            'followers': artist_data.get('followers', {}).get('total'),
            'external_urls': artist_data.get('external_urls', {}),
            'source': 'spotify',
            'type': 'artist'
        }
    
    def _format_album(self, album_data: Dict) -> Dict:
        """Formate les données d'un album pour usage interne"""
        artists = album_data.get('artists', [])
        
        return {
            'external_id': album_data.get('id'),
            'title': album_data.get('name', ''),
            'artists': [artist.get('name', '') for artist in artists],
            'description': f"Album - {', '.join([a.get('name', '') for a in artists])}",
            'poster_url': self._get_best_image(album_data.get('images', [])),
            'release_date': album_data.get('release_date'),
            'total_tracks': album_data.get('total_tracks'),
            'album_type': album_data.get('album_type'),
            'external_urls': album_data.get('external_urls', {}),
            'source': 'spotify',
            'type': 'album'
        }
    
    def _get_best_image(self, images: List[Dict]) -> Optional[str]:
        """Récupère la meilleure image disponible"""
        if not images:
            return None
        
        # Préférer les images de taille moyenne (640x640)
        for img in images:
            if img.get('height') == 640:
                return img.get('url')
        
        # Sinon prendre la première disponible
        return images[0].get('url') if images else None