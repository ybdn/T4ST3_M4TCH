"""
Tests unitaires pour RecommendationService.
Couvre les cas de succès multi-sources, sources vides, et cache hit/miss.
"""

from django.test import TestCase
from django.contrib.auth.models import User
from unittest.mock import Mock, MagicMock, patch
from datetime import datetime, timedelta
from django.utils import timezone

from core.models import List, ListItem, ExternalReference, APICache
from core.services.recommendation_service import RecommendationService


class RecommendationServiceTestCase(TestCase):
    """Tests pour le service de recommandations"""
    
    def setUp(self):
        """Configuration des tests"""
        # Créer un utilisateur de test
        self.user = User.objects.create_user(username='testuser', password='testpass')
        
        # Créer des listes de test pour chaque catégorie
        self.film_list = List.objects.create(
            owner=self.user,
            category='FILMS',
            name='Mes Films',
            description='Test films list'
        )
        
        self.series_list = List.objects.create(
            owner=self.user,
            category='SERIES', 
            name='Mes Séries',
            description='Test series list'
        )
        
        self.music_list = List.objects.create(
            owner=self.user,
            category='MUSIQUE',
            name='Ma Musique', 
            description='Test music list'
        )
        
        self.books_list = List.objects.create(
            owner=self.user,
            category='LIVRES',
            name='Mes Livres',
            description='Test books list'
        )
        
        # Créer des éléments de test
        self.film_item = ListItem.objects.create(
            title='Inception',
            description='Film de test',
            list=self.film_list,
            position=1
        )
        
        self.series_item = ListItem.objects.create(
            title='Breaking Bad',
            description='Série de test', 
            list=self.series_list,
            position=1
        )
        
        self.music_item = ListItem.objects.create(
            title='The Beatles',
            description='Artiste de test',
            list=self.music_list,
            position=1
        )
        
        self.book_item = ListItem.objects.create(
            title='1984',
            description='Livre de test',
            list=self.books_list,
            position=1
        )
        
        # Mocker les services externes
        self.mock_tmdb = Mock()
        self.mock_spotify = Mock()
        self.mock_books = Mock()
        
        # Créer le service avec les mocks
        self.service = RecommendationService(
            tmdb_service=self.mock_tmdb,
            spotify_service=self.mock_spotify,
            books_service=self.mock_books
        )
    
    def tearDown(self):
        """Nettoyage après les tests"""
        APICache.objects.all().delete()
    
    def test_init_with_services(self):
        """Test d'initialisation avec les services fournis"""
        service = RecommendationService(
            tmdb_service=self.mock_tmdb,
            spotify_service=self.mock_spotify, 
            books_service=self.mock_books
        )
        
        self.assertEqual(service.tmdb_service, self.mock_tmdb)
        self.assertEqual(service.spotify_service, self.mock_spotify)
        self.assertEqual(service.books_service, self.mock_books)
    
    @patch('core.services.tmdb_service.TMDBService')
    @patch('core.services.spotify_service.SpotifyService') 
    @patch('core.services.books_service.BooksService')
    def test_init_without_services(self, mock_books_cls, mock_spotify_cls, mock_tmdb_cls):
        """Test d'initialisation avec lazy loading des services"""
        service = RecommendationService()
        
        mock_tmdb_cls.assert_called_once()
        mock_spotify_cls.assert_called_once()
        mock_books_cls.assert_called_once()
    
    def test_get_recommendations_for_item_without_external_ref(self):
        """Test recommandations pour item sans référence externe"""
        # Mock du contenu tendance
        mock_trending = [
            {'external_id': '1', 'title': 'Film tendance', 'category': 'FILMS'},
            {'external_id': '2', 'title': 'Film populaire', 'category': 'FILMS'}
        ]
        
        with patch.object(self.service, 'get_trending_content', return_value=mock_trending):
            result = self.service.get_recommendations_for_item(self.film_item, limit=5)
        
        self.assertEqual(len(result), 2)
        self.assertEqual(result[0]['title'], 'Film tendance')
    
    def test_get_recommendations_for_item_with_tmdb_ref(self):
        """Test recommandations pour item avec référence TMDB"""
        # Créer une référence externe TMDB
        external_ref = ExternalReference.objects.create(
            list_item=self.film_item,
            external_id='12345',
            external_source='tmdb'
        )
        
        # Mock des recommandations TMDB
        mock_recommendations = [
            {'external_id': '67890', 'title': 'Similar Movie', 'type': 'movie'}
        ]
        mock_similar = [
            {'external_id': '54321', 'title': 'Another Movie', 'type': 'movie'}
        ]
        
        self.mock_tmdb.get_recommendations_movies.return_value = mock_recommendations
        self.mock_tmdb.get_similar_movies.return_value = mock_similar
        
        result = self.service.get_recommendations_for_item(self.film_item, limit=10)
        
        # Vérifier que les méthodes TMDB ont été appelées
        self.mock_tmdb.get_recommendations_movies.assert_called_once_with(12345, 5)
        self.mock_tmdb.get_similar_movies.assert_called_once_with(12345, 5)
        
        # Vérifier les résultats
        self.assertEqual(len(result), 2)
        self.assertEqual(result[0]['category'], 'FILMS')
    
    def test_get_recommendations_for_item_with_spotify_ref(self):
        """Test recommandations pour item avec référence Spotify"""
        # Créer une référence externe Spotify
        external_ref = ExternalReference.objects.create(
            list_item=self.music_item,
            external_id='spotify123',
            external_source='spotify',
            metadata={'type': 'artist'}
        )
        
        # Mock des recommandations Spotify
        mock_related = [{'external_id': 'artist1', 'name': 'Related Artist'}]
        mock_top_tracks = [{'external_id': 'track1', 'name': 'Top Track'}]
        
        self.mock_spotify.get_related_artists.return_value = mock_related
        self.mock_spotify.get_artist_top_tracks.return_value = mock_top_tracks
        
        result = self.service.get_recommendations_for_item(self.music_item, limit=10)
        
        # Vérifier les appels
        self.mock_spotify.get_related_artists.assert_called_once_with('spotify123', 5)
        self.mock_spotify.get_artist_top_tracks.assert_called_once_with('spotify123', limit=5)
        
        # Vérifier les résultats
        self.assertEqual(len(result), 2)
        for item in result:
            self.assertEqual(item['category'], 'MUSIQUE')
    
    def test_get_recommendations_for_item_exception_handling(self):
        """Test gestion d'erreur lors des recommandations"""
        # Créer référence externe qui va lever une exception
        external_ref = ExternalReference.objects.create(
            list_item=self.film_item,
            external_id='invalid',
            external_source='tmdb'
        )
        
        # Mock qui lève une exception
        self.mock_tmdb.get_recommendations_movies.side_effect = Exception("API Error")
        self.mock_tmdb.get_similar_movies.side_effect = Exception("API Error")
        
        # Mock du fallback - le fallback doit être appelé dans le catch
        mock_trending = [{'external_id': '1', 'title': 'Fallback Movie'}]
        self.mock_tmdb.get_trending_movies.return_value = mock_trending
        self.mock_tmdb.get_trending_tv_shows.return_value = []
        self.mock_spotify.get_new_releases.return_value = []
        self.mock_spotify.get_featured_playlists.return_value = []
        self.mock_books.get_popular_books.return_value = []
        
        result = self.service.get_recommendations_for_item(self.film_item)
        
        # Devrait retourner le contenu tendance en fallback
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]['title'], 'Fallback Movie')
    
    def test_get_similar_content_success(self):
        """Test récupération de contenu similaire avec succès"""
        # Créer référence externe
        external_ref = ExternalReference.objects.create(
            list_item=self.series_item,
            external_id='54321', 
            external_source='tmdb'
        )
        
        # Mock du contenu similaire
        mock_similar = [
            {'external_id': '99999', 'name': 'Similar Show', 'type': 'tv'}
        ]
        
        self.mock_tmdb.get_similar_tv_shows.return_value = mock_similar
        
        result = self.service.get_similar_content(self.series_item, limit=5)
        
        self.mock_tmdb.get_similar_tv_shows.assert_called_once_with(54321, 5)
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]['category'], 'SERIES')
    
    def test_get_trending_content_all_categories(self):
        """Test récupération de contenu tendance pour toutes les catégories"""
        # Mock du contenu tendance pour chaque service
        mock_movies = [{'external_id': '1', 'title': 'Trending Movie'}]
        mock_shows = [{'external_id': '2', 'name': 'Trending Show'}]
        mock_music = [{'external_id': '3', 'name': 'Trending Song'}]
        mock_books = [{'external_id': '4', 'title': 'Trending Book'}]
        
        self.mock_tmdb.get_trending_movies.return_value = mock_movies
        self.mock_tmdb.get_trending_tv_shows.return_value = mock_shows
        self.mock_spotify.get_new_releases.return_value = mock_music[:1]
        self.mock_spotify.get_featured_playlists.return_value = []
        self.mock_books.get_popular_books.return_value = mock_books
        
        result = self.service.get_trending_content(limit=20)
        
        # Vérifier que tous les services sont appelés
        self.mock_tmdb.get_trending_movies.assert_called_once()
        self.mock_tmdb.get_trending_tv_shows.assert_called_once()
        self.mock_spotify.get_new_releases.assert_called_once()
        self.mock_books.get_popular_books.assert_called_once()
        
        # Vérifier les catégories ajoutées
        self.assertEqual(len(result), 4)
        categories = [item['category'] for item in result]
        self.assertIn('FILMS', categories)
        self.assertIn('SERIES', categories)
        self.assertIn('MUSIQUE', categories)
        self.assertIn('LIVRES', categories)
    
    def test_get_trending_content_specific_category(self):
        """Test récupération de contenu tendance pour une catégorie spécifique"""
        mock_movies = [
            {'external_id': '1', 'title': 'Movie 1'},
            {'external_id': '2', 'title': 'Movie 2'}
        ]
        
        self.mock_tmdb.get_trending_movies.return_value = mock_movies
        
        result = self.service.get_trending_content(category='FILMS', limit=10)
        
        # Seul le service de films devrait être appelé
        self.mock_tmdb.get_trending_movies.assert_called_once_with(limit=5)
        self.mock_tmdb.get_trending_tv_shows.assert_not_called()
        
        self.assertEqual(len(result), 2)
        for movie in result:
            self.assertEqual(movie['category'], 'FILMS')
    
    def test_get_trending_content_empty_sources(self):
        """Test avec sources vides - cas de sources ne retournant rien"""
        # Mock de services retournant des listes vides
        self.mock_tmdb.get_trending_movies.return_value = []
        self.mock_tmdb.get_trending_tv_shows.return_value = []
        self.mock_spotify.get_new_releases.return_value = []
        self.mock_spotify.get_featured_playlists.return_value = []
        self.mock_books.get_popular_books.return_value = []
        
        result = self.service.get_trending_content(limit=20)
        
        # Devrait retourner une liste vide
        self.assertEqual(len(result), 0)
        
        # Vérifier que tous les services ont été appelés malgré tout
        self.mock_tmdb.get_trending_movies.assert_called_once()
        self.mock_tmdb.get_trending_tv_shows.assert_called_once()
        self.mock_spotify.get_new_releases.assert_called_once()
        self.mock_books.get_popular_books.assert_called_once()
    
    def test_get_trending_content_service_exceptions(self):
        """Test avec exceptions des services externes"""
        # Mock de services levant des exceptions
        self.mock_tmdb.get_trending_movies.side_effect = Exception("TMDB Error")
        self.mock_tmdb.get_trending_tv_shows.side_effect = Exception("TMDB Error")
        self.mock_spotify.get_new_releases.side_effect = Exception("Spotify Error")
        self.mock_spotify.get_featured_playlists.return_value = []
        self.mock_books.get_popular_books.side_effect = Exception("Books Error")
        
        result = self.service.get_trending_content(limit=20)
        
        # Devrait gérer les erreurs gracieusement et retourner une liste vide
        self.assertEqual(len(result), 0)
    
    def test_get_multi_source_recommendations_success(self):
        """Test recommandations multi-sources avec succès"""
        user_preferences = {
            'FILMS': {'genres': ['action', 'thriller']},
            'MUSIQUE': {'artists': ['The Beatles', 'Queen']}
        }
        
        # Mock du contenu tendance pour chaque catégorie
        mock_films = [{'external_id': '1', 'title': 'Action Movie', 'category': 'FILMS'}]
        mock_music = [{'external_id': '2', 'name': 'Rock Song', 'category': 'MUSIQUE'}]
        
        with patch.object(self.service, 'get_trending_content') as mock_trending:
            mock_trending.side_effect = [mock_films, mock_music]
            
            result = self.service.get_multi_source_recommendations(user_preferences, limit=10)
        
        # Vérifier que get_trending_content est appelé pour chaque catégorie
        self.assertEqual(mock_trending.call_count, 2)
        
        # Vérifier les résultats
        self.assertEqual(len(result), 2)
        categories = [item['category'] for item in result]
        self.assertIn('FILMS', categories)
        self.assertIn('MUSIQUE', categories)
    
    def test_get_multi_source_recommendations_empty_preferences(self):
        """Test recommandations multi-sources avec préférences vides"""
        result = self.service.get_multi_source_recommendations({}, limit=10)
        
        # Devrait retourner une liste vide
        self.assertEqual(len(result), 0)
    
    def test_get_multi_source_recommendations_category_error(self):
        """Test recommandations multi-sources avec erreur sur une catégorie"""
        user_preferences = {
            'FILMS': {'genres': ['action']},
            'MUSIQUE': {'artists': ['Beatles']}
        }
        
        with patch.object(self.service, '_get_category_recommendations') as mock_cat_recs:
            # Première catégorie réussit, deuxième échoue
            mock_cat_recs.side_effect = [
                [{'external_id': '1', 'title': 'Movie'}],
                Exception("Category error")
            ]
            
            result = self.service.get_multi_source_recommendations(user_preferences, limit=10)
        
        # Devrait retourner seulement les recommandations qui ont réussi
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]['title'], 'Movie')
    
    def test_deduplicate_by_id(self):
        """Test de déduplication par ID externe"""
        items = [
            {'external_id': '123', 'title': 'Item 1'},
            {'external_id': '456', 'title': 'Item 2'}, 
            {'external_id': '123', 'title': 'Item 1 Duplicate'},
            {'external_id': '789', 'title': 'Item 3'},
            {'title': 'Item without ID'}  # Sans external_id
        ]
        
        result = self.service._deduplicate_by_id(items)
        
        # Devrait garder seulement les items uniques avec external_id
        self.assertEqual(len(result), 3)
        external_ids = [item.get('external_id') for item in result if item.get('external_id')]
        self.assertEqual(sorted(external_ids), ['123', '456', '789'])
    
    def test_clear_cache_specific_category(self):
        """Test nettoyage du cache pour une catégorie spécifique"""
        # Créer des entrées de cache
        APICache.objects.create(
            cache_key='tmdb_films_trending',
            data={'test': 'data'},
            expires_at=timezone.now() + timedelta(hours=1)
        )
        APICache.objects.create(
            cache_key='spotify_musique_popular',
            data={'test': 'data'},
            expires_at=timezone.now() + timedelta(hours=1)
        )
        
        result = self.service.clear_cache(category='FILMS')
        
        # Devrait supprimer seulement les entrées contenant "films" (insensible à la casse)
        self.assertEqual(result, 1)
        self.assertEqual(APICache.objects.filter(cache_key__icontains='films').count(), 0)
        self.assertEqual(APICache.objects.filter(cache_key__icontains='musique').count(), 1)
    
    def test_clear_cache_all_expired(self):
        """Test nettoyage de tout le cache expiré"""
        # Créer des entrées expirées et non-expirées
        APICache.objects.create(
            cache_key='expired_entry',
            data={'test': 'data'},
            expires_at=timezone.now() - timedelta(hours=1)  # Expirée
        )
        APICache.objects.create(
            cache_key='active_entry',
            data={'test': 'data'},
            expires_at=timezone.now() + timedelta(hours=1)  # Active
        )
        
        result = self.service.clear_cache()
        
        # Devrait supprimer seulement l'entrée expirée
        self.assertEqual(result, 1)
        self.assertEqual(APICache.objects.filter(cache_key='active_entry').count(), 1)
        self.assertEqual(APICache.objects.filter(cache_key='expired_entry').count(), 0)
    
    def test_clear_cache_exception_handling(self):
        """Test gestion d'erreur lors du nettoyage du cache"""
        with patch.object(APICache.objects, 'filter') as mock_filter:
            mock_filter.side_effect = Exception("Database error")
            
            result = self.service.clear_cache()
            
            # Devrait retourner 0 en cas d'erreur
            self.assertEqual(result, 0)
    
    def test_get_cache_stats_success(self):
        """Test récupération des statistiques de cache avec succès"""
        # Créer des entrées de cache
        APICache.objects.create(
            cache_key='active1',
            data={'test': 'data'},
            expires_at=timezone.now() + timedelta(hours=1)
        )
        APICache.objects.create(
            cache_key='active2',
            data={'test': 'data'},
            expires_at=timezone.now() + timedelta(hours=1)
        )
        APICache.objects.create(
            cache_key='expired1',
            data={'test': 'data'},
            expires_at=timezone.now() - timedelta(hours=1)
        )
        
        stats = self.service.get_cache_stats()
        
        self.assertEqual(stats['total_entries'], 3)
        self.assertEqual(stats['active_entries'], 2)
        self.assertEqual(stats['expired_entries'], 1)
    
    def test_get_cache_stats_exception_handling(self):
        """Test gestion d'erreur lors de la récupération des stats"""
        with patch.object(APICache.objects, 'count') as mock_count:
            mock_count.side_effect = Exception("Database error")
            
            stats = self.service.get_cache_stats()
            
            # Devrait retourner des valeurs par défaut
            expected_stats = {'total_entries': 0, 'active_entries': 0, 'expired_entries': 0}
            self.assertEqual(stats, expected_stats)
    
    def test_tmdb_recommendations_films(self):
        """Test recommandations TMDB pour films"""
        external_ref = ExternalReference.objects.create(
            list_item=self.film_item,
            external_id='12345',
            external_source='tmdb'
        )
        
        # Mock des réponses TMDB
        mock_recs = [{'external_id': '1', 'title': 'Recommended Film'}]
        mock_similar = [{'external_id': '2', 'title': 'Similar Film'}]
        
        self.mock_tmdb.get_recommendations_movies.return_value = mock_recs
        self.mock_tmdb.get_similar_movies.return_value = mock_similar
        
        result = self.service._get_tmdb_recommendations('12345', 'FILMS', 10)
        
        self.assertEqual(len(result), 2)
        # Vérifier que les catégories sont ajoutées
        for item in result:
            self.assertEqual(item['category'], 'FILMS')
            self.assertEqual(item['category_display'], 'Films')
    
    def test_tmdb_recommendations_series(self):
        """Test recommandations TMDB pour séries"""
        mock_recs = [{'external_id': '1', 'name': 'Recommended Series'}]
        mock_similar = [{'external_id': '2', 'name': 'Similar Series'}]
        
        self.mock_tmdb.get_recommendations_tv_shows.return_value = mock_recs
        self.mock_tmdb.get_similar_tv_shows.return_value = mock_similar
        
        result = self.service._get_tmdb_recommendations('12345', 'SERIES', 10)
        
        self.assertEqual(len(result), 2)
        for item in result:
            self.assertEqual(item['category'], 'SERIES')
    
    def test_spotify_recommendations_artist(self):
        """Test recommandations Spotify pour artiste"""
        metadata = {'type': 'artist'}
        
        mock_related = [{'external_id': '1', 'name': 'Related Artist'}]
        mock_tracks = [{'external_id': '2', 'name': 'Top Track'}]
        
        self.mock_spotify.get_related_artists.return_value = mock_related
        self.mock_spotify.get_artist_top_tracks.return_value = mock_tracks
        
        result = self.service._get_spotify_recommendations('artist123', metadata, 10)
        
        self.assertEqual(len(result), 2)
        for item in result:
            self.assertEqual(item['category'], 'MUSIQUE')
    
    def test_spotify_recommendations_non_artist(self):
        """Test recommandations Spotify pour non-artiste (fallback)"""
        metadata = {'type': 'track'}
        
        with patch.object(self.service, '_get_trending_music') as mock_trending:
            mock_trending.return_value = [{'external_id': '1', 'name': 'Trending Song'}]
            
            result = self.service._get_spotify_recommendations('track123', metadata, 10)
            
            mock_trending.assert_called_once_with(10)
            self.assertEqual(len(result), 1)
    
    def test_books_recommendations_fallback(self):
        """Test recommandations livres (fallback vers tendance)"""
        with patch.object(self.service, '_get_trending_books') as mock_trending:
            mock_trending.return_value = [{'external_id': '1', 'title': 'Popular Book'}]
            
            result = self.service._get_books_recommendations('book123', 10)
            
            mock_trending.assert_called_once_with(10)
            self.assertEqual(len(result), 1)
    
    def test_get_recommendations_unknown_source(self):
        """Test recommandations avec source inconnue"""
        external_ref = ExternalReference.objects.create(
            list_item=self.film_item,
            external_id='12345',
            external_source='unknown_source'
        )
        
        with patch.object(self.service, 'get_trending_content') as mock_trending:
            mock_trending.return_value = [{'external_id': '1', 'title': 'Fallback Content'}]
            
            result = self.service._get_recommendations_by_source(external_ref, 'FILMS', 10)
            
            mock_trending.assert_called_once_with('FILMS', 10)
            self.assertEqual(len(result), 1)
    
    # Tests de cache hit/miss avec mock
    def test_cache_hit_scenario(self):
        """Test scénario de cache hit"""
        # Simuler une entrée de cache existante et valide
        cache_key = 'test_cache_key'
        cached_data = [{'external_id': '1', 'title': 'Cached Movie'}]
        
        APICache.objects.create(
            cache_key=cache_key,
            data=cached_data,
            expires_at=timezone.now() + timedelta(hours=1)
        )
        
        # Récupérer depuis le cache
        result = APICache.get_cached_data(cache_key)
        
        self.assertEqual(result, cached_data)
    
    def test_cache_miss_scenario(self):
        """Test scénario de cache miss"""
        # Tenter de récupérer une clé qui n'existe pas
        result = APICache.get_cached_data('non_existent_key')
        
        self.assertIsNone(result)
    
    def test_cache_expired_scenario(self):
        """Test scénario de cache expiré"""
        cache_key = 'expired_cache_key'
        
        # Créer une entrée expirée
        APICache.objects.create(
            cache_key=cache_key,
            data={'test': 'data'},
            expires_at=timezone.now() - timedelta(hours=1)
        )
        
        # Devrait retourner None et supprimer l'entrée
        result = APICache.get_cached_data(cache_key)
        
        self.assertIsNone(result)
        self.assertFalse(APICache.objects.filter(cache_key=cache_key).exists())
    
    def test_service_method_error_recovery(self):
        """Test récupération d'erreur dans les méthodes de service"""
        # Test que les erreurs dans les services externes sont gérées
        self.mock_tmdb.get_trending_movies.side_effect = Exception("Network error")
        
        result = self.service._get_trending_movies(10)
        
        # Devrait retourner une liste vide en cas d'erreur
        self.assertEqual(result, [])
    
    def test_empty_metadata_handling(self):
        """Test gestion des métadonnées vides"""
        # Test avec métadonnées vides pour Spotify
        result = self.service._get_spotify_recommendations('artist123', {}, 10)
        
        # Devrait utiliser 'track' comme type par défaut
        with patch.object(self.service, '_get_trending_music') as mock_trending:
            mock_trending.return_value = []
            result = self.service._get_spotify_recommendations('artist123', {}, 10)
            mock_trending.assert_called_once()