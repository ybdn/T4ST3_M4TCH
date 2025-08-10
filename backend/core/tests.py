import unittest
from unittest.mock import patch, Mock
from django.test import TestCase
from django.contrib.auth.models import User
from core.services.cached_external_api_service import CachedExternalAPIService, CacheMetrics
from core.services.tmdb_service import TMDBService
from core.services.spotify_service import SpotifyService
from core.services.books_service import BooksService
from core.models import APICache, List, ListItem


class CachedExternalAPIServiceTests(TestCase):
    """Tests pour le service de cache des APIs externes"""
    
    def setUp(self):
        self.cache_service = CachedExternalAPIService('test')
        # Nettoyer les métriques pour chaque test
        CachedExternalAPIService.reset_global_metrics()
        # Nettoyer le cache existant
        APICache.objects.all().delete()
    
    def test_cache_key_generation(self):
        """Test de génération des clés de cache"""
        url = "https://api.example.com/test"
        params = {"query": "test", "limit": 10}
        headers = {"Authorization": "Bearer token", "User-Agent": "test"}
        
        key1 = self.cache_service._generate_cache_key(url, params, headers)
        key2 = self.cache_service._generate_cache_key(url, params, headers)
        
        # Les clés doivent être identiques pour les mêmes paramètres
        self.assertEqual(key1, key2)
        
        # Les headers sensibles ne doivent pas être inclus
        headers_with_auth = {"Authorization": "Bearer different", "User-Agent": "test"}
        key3 = self.cache_service._generate_cache_key(url, params, headers_with_auth)
        self.assertEqual(key1, key3)  # Authorization ignoré
    
    @patch('requests.get')
    def test_cache_miss_then_hit(self, mock_get):
        """Test d'un cache miss suivi d'un cache hit"""
        # Configuration du mock
        mock_response = Mock()
        mock_response.json.return_value = {"test": "data"}
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response
        
        url = "https://api.example.com/test"
        params = {"query": "test"}
        
        # Première requête - devrait être un cache miss
        result1 = self.cache_service.get_external(url, params)
        self.assertEqual(result1, {"test": "data"})
        self.assertEqual(mock_get.call_count, 1)
        
        # Deuxième requête - devrait être un cache hit
        result2 = self.cache_service.get_external(url, params)
        self.assertEqual(result2, {"test": "data"})
        self.assertEqual(mock_get.call_count, 1)  # Pas d'appel supplémentaire
        
        # Vérifier les métriques
        metrics = CachedExternalAPIService.get_global_metrics()
        self.assertEqual(metrics['total_requests'], 2)
        self.assertEqual(metrics['hits'], 1)
        self.assertEqual(metrics['misses'], 1)
        self.assertEqual(metrics['hit_rate'], 50.0)
    
    @patch('requests.get')
    def test_cache_hit_rate_calculation(self, mock_get):
        """Test du calcul du taux de cache hit"""
        # Configuration du mock
        mock_response = Mock()
        mock_response.json.return_value = {"test": "data"}
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response
        
        url = "https://api.example.com/test"
        
        # Première requête (miss)
        self.cache_service.get_external(url, {"id": "1"})
        
        # Cinq requêtes identiques (hits)
        for _ in range(5):
            self.cache_service.get_external(url, {"id": "1"})
        
        # Vérifier les métriques
        metrics = CachedExternalAPIService.get_global_metrics()
        self.assertEqual(metrics['total_requests'], 6)
        self.assertEqual(metrics['hits'], 5)
        self.assertEqual(metrics['misses'], 1)
        self.assertEqual(metrics['hit_rate'], 83.33)  # 5/6 * 100
    
    def test_ttl_configuration(self):
        """Test de configuration TTL"""
        tmdb_service = CachedExternalAPIService('tmdb')
        spotify_service = CachedExternalAPIService('spotify')
        books_service = CachedExternalAPIService('books')
        
        # Vérifier que les TTL par défaut sont corrects
        ttl_config = tmdb_service._get_ttl_config()
        self.assertIn('tmdb', ttl_config)
        self.assertIn('spotify', ttl_config)
        self.assertIn('books', ttl_config)
        self.assertIn('default', ttl_config)


class IntegrationCacheTests(TestCase):
    """Tests d'intégration pour valider le cache avec les vrais services"""
    
    def setUp(self):
        # Nettoyer les métriques et le cache
        CachedExternalAPIService.reset_global_metrics()
        APICache.objects.all().delete()
        
        # Créer un utilisateur et des listes de test
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
    
    @patch('requests.get')
    def test_tmdb_service_caching(self, mock_get):
        """Test du cache pour TMDBService"""
        # Mock de réponse TMDB
        mock_response = Mock()
        mock_response.json.return_value = {
            "results": [{
                "id": 123,
                "title": "Test Movie",
                "overview": "Test description",
                "vote_average": 8.5,
                "release_date": "2023-01-01",
                "poster_path": "/test.jpg"
            }]
        }
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response
        
        tmdb = TMDBService()
        
        # Première recherche (miss)
        results1 = tmdb.search_movies("test movie")
        self.assertEqual(len(results1), 1)
        self.assertEqual(results1[0]['title'], "Test Movie")
        
        # Deuxième recherche identique (hit)
        results2 = tmdb.search_movies("test movie")
        self.assertEqual(len(results2), 1)
        self.assertEqual(results2[0]['title'], "Test Movie")
        
        # Vérifier qu'une seule requête HTTP a été faite
        self.assertEqual(mock_get.call_count, 1)
    
    @patch('requests.post')
    @patch('requests.get')
    def test_spotify_service_caching(self, mock_get, mock_post):
        """Test du cache pour SpotifyService"""
        # Mock pour le token
        mock_token_response = Mock()
        mock_token_response.json.return_value = {
            "access_token": "test_token",
            "expires_in": 3600
        }
        mock_token_response.raise_for_status.return_value = None
        mock_post.return_value = mock_token_response
        
        # Mock pour la recherche
        mock_search_response = Mock()
        mock_search_response.json.return_value = {
            "tracks": {
                "items": [{
                    "id": "test_track_id",
                    "name": "Test Song",
                    "artists": [{"name": "Test Artist"}],
                    "album": {
                        "name": "Test Album",
                        "images": [{"url": "test.jpg", "height": 640}],
                        "release_date": "2023-01-01"
                    },
                    "duration_ms": 180000,
                    "popularity": 75
                }]
            }
        }
        mock_search_response.raise_for_status.return_value = None
        mock_get.return_value = mock_search_response
        
        # Utiliser de vraies credentials pour ce test
        with patch.object(SpotifyService, '__init__', lambda self: None):
            spotify = SpotifyService()
            spotify.client_id = "test_client"
            spotify.client_secret = "test_secret"
            spotify._access_token = None
            spotify.cache_service = CachedExternalAPIService('spotify')
            
            # Première recherche (miss)
            results1 = spotify.search_music("test song")
            self.assertEqual(len(results1), 1)
            
            # Deuxième recherche identique (hit)
            results2 = spotify.search_music("test song")
            self.assertEqual(len(results2), 1)
            
            # Vérifier le cache
            self.assertEqual(mock_get.call_count, 1)  # Une seule requête de recherche
    
    def test_cache_hit_rate_target(self):
        """Test pour valider l'objectif de >40% de hit rate"""
        service = CachedExternalAPIService('test')
        
        # Simuler des requêtes avec du cache
        with patch('requests.get') as mock_get:
            mock_response = Mock()
            mock_response.json.return_value = {"data": "test"}
            mock_response.raise_for_status.return_value = None
            mock_get.return_value = mock_response
            
            # 3 requêtes différentes (3 misses)
            service.get_external("https://api.test.com/1", {"id": "1"})
            service.get_external("https://api.test.com/2", {"id": "2"})
            service.get_external("https://api.test.com/3", {"id": "3"})
            
            # 7 requêtes répétées (7 hits)
            for _ in range(7):
                service.get_external("https://api.test.com/1", {"id": "1"})
            
            metrics = CachedExternalAPIService.get_global_metrics()
            
            # Vérifier que l'objectif est atteint
            self.assertGreaterEqual(metrics['hit_rate'], 40.0)
            self.assertEqual(metrics['total_requests'], 10)
            self.assertEqual(metrics['hits'], 7)
            self.assertEqual(metrics['misses'], 3)
            self.assertEqual(metrics['hit_rate'], 70.0)


class CacheMetricsTests(TestCase):
    """Tests pour la classe CacheMetrics"""
    
    def test_metrics_initialization(self):
        """Test d'initialisation des métriques"""
        metrics = CacheMetrics()
        stats = metrics.get_stats()
        
        self.assertEqual(stats['hits'], 0)
        self.assertEqual(stats['misses'], 0)
        self.assertEqual(stats['total_requests'], 0)
        self.assertEqual(stats['hit_rate'], 0.0)
    
    def test_metrics_recording(self):
        """Test d'enregistrement des métriques"""
        metrics = CacheMetrics()
        
        # Enregistrer quelques hits et misses
        metrics.record_hit()
        metrics.record_hit()
        metrics.record_miss()
        
        stats = metrics.get_stats()
        self.assertEqual(stats['hits'], 2)
        self.assertEqual(stats['misses'], 1)
        self.assertEqual(stats['total_requests'], 3)
        self.assertEqual(stats['hit_rate'], 66.67)
    
    def test_metrics_reset(self):
        """Test de remise à zéro des métriques"""
        metrics = CacheMetrics()
        
        # Ajouter quelques données
        metrics.record_hit()
        metrics.record_miss()
        
        # Reset
        metrics.reset()
        
        stats = metrics.get_stats()
        self.assertEqual(stats['hits'], 0)
        self.assertEqual(stats['misses'], 0)
        self.assertEqual(stats['total_requests'], 0)
        self.assertEqual(stats['hit_rate'], 0.0)
