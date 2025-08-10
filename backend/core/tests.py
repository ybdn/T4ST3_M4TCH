from django.test import TestCase
from rest_framework.test import APITestCase
from rest_framework import status
from django.urls import reverse
from django.conf import settings
import os


class ConfigEndpointTestCase(APITestCase):
    """
    Tests pour l'endpoint de configuration /api/v1/config/
    """
    
    def test_config_endpoint_returns_200(self):
        """Test que l'endpoint renvoie un status 200"""
        url = reverse('api_config')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
    
    def test_config_endpoint_structure(self):
        """Test la structure de la réponse JSON"""
        url = reverse('api_config')
        response = self.client.get(url)
        
        # Vérifier la structure de la réponse
        self.assertIn('feature_flags', response.data)
        self.assertIn('build', response.data)
        self.assertIn('version', response.data)
        
        # Vérifier la structure des feature flags
        feature_flags = response.data['feature_flags']
        self.assertIsInstance(feature_flags, dict)
        self.assertIn('social_profile', feature_flags)
        self.assertIn('friend_system', feature_flags)
        self.assertIn('versus_match', feature_flags)
        self.assertIn('external_apis', feature_flags)
        self.assertIn('recommendations', feature_flags)
        
        # Vérifier la structure des infos build
        build_info = response.data['build']
        self.assertIn('hash', build_info)
        self.assertIn('timestamp', build_info)
        
        # Vérifier la version
        self.assertIsInstance(response.data['version'], str)
    
    def test_config_endpoint_with_git_sha_env(self):
        """Test que l'endpoint utilise GIT_SHA si disponible"""
        # Simuler la présence de GIT_SHA dans l'environnement
        test_hash = 'abc123def456'
        with self.settings():
            # Backup de l'env original
            original_git_sha = os.environ.get('GIT_SHA')
            
            # Définir GIT_SHA
            os.environ['GIT_SHA'] = test_hash
            
            try:
                url = reverse('api_config')
                response = self.client.get(url)
                
                self.assertEqual(response.data['build']['hash'], test_hash)
            finally:
                # Restaurer l'env original
                if original_git_sha is not None:
                    os.environ['GIT_SHA'] = original_git_sha
                else:
                    os.environ.pop('GIT_SHA', None)
    
    def test_config_endpoint_without_git_sha(self):
        """Test que l'endpoint utilise 'unknown' si GIT_SHA n'est pas disponible"""
        # S'assurer que GIT_SHA n'est pas défini
        original_git_sha = os.environ.get('GIT_SHA')
        if 'GIT_SHA' in os.environ:
            del os.environ['GIT_SHA']
        
        try:
            url = reverse('api_config')
            response = self.client.get(url)
            
            self.assertEqual(response.data['build']['hash'], 'unknown')
        finally:
            # Restaurer l'env original
            if original_git_sha is not None:
                os.environ['GIT_SHA'] = original_git_sha
    
    def test_config_endpoint_cache_headers(self):
        """Test que l'endpoint renvoie les bons headers de cache"""
        url = reverse('api_config')
        response = self.client.get(url)
        
        self.assertIn('Cache-Control', response)
        self.assertEqual(response['Cache-Control'], 'public, max-age=60')
    
    def test_config_endpoint_uses_default_flags(self):
        """Test que les flags par défaut sont utilisés si FEATURE_FLAGS n'est pas défini"""
        url = reverse('api_config')
        response = self.client.get(url)
        
        # Vérifier que tous les flags par défaut sont présents et True
        feature_flags = response.data['feature_flags']
        expected_flags = {
            'social_profile': True,
            'friend_system': True,
            'versus_match': True,
            'external_apis': True,
            'recommendations': True
        }
        
        for flag_name, expected_value in expected_flags.items():
            self.assertIn(flag_name, feature_flags)
            self.assertEqual(feature_flags[flag_name], expected_value)


class FeatureFlagsServiceTestCase(APITestCase):
    """
    Tests pour le service FeatureFlagsService
    """
    
    def setUp(self):
        """Configuration des tests"""
        from .models import FeatureFlag
        from django.core.cache import cache
        
        # Nettoyer le cache avant chaque test
        cache.clear()
        
        # Créer quelques feature flags de test
        self.flag_enabled = FeatureFlag.objects.create(
            name='test_enabled',
            enabled=True,
            rollout_percentage=100,
            description='Flag toujours activé'
        )
        
        self.flag_disabled = FeatureFlag.objects.create(
            name='test_disabled', 
            enabled=False,
            rollout_percentage=0,
            description='Flag toujours désactivé'
        )
        
        self.flag_rollout = FeatureFlag.objects.create(
            name='test_rollout',
            enabled=True,
            rollout_percentage=50,
            description='Flag à 50% de rollout'
        )
    
    def test_is_enabled_basic(self):
        """Test des cas basiques de is_enabled"""
        from .services.feature_flags_service import FeatureFlagsService
        
        # Flag activé
        self.assertTrue(FeatureFlagsService.is_enabled('test_enabled'))
        
        # Flag désactivé
        self.assertFalse(FeatureFlagsService.is_enabled('test_disabled'))
        
        # Flag inexistant
        self.assertFalse(FeatureFlagsService.is_enabled('nonexistent_flag'))
    
    def test_is_enabled_with_rollout(self):
        """Test du rollout progressif"""
        from .services.feature_flags_service import FeatureFlagsService
        
        # Test avec différents user_ids pour voir la distribution
        results = []
        for user_id in range(100):
            result = FeatureFlagsService.is_enabled('test_rollout', user_id)
            results.append(result)
        
        # On s'attend à environ 50% d'activation (avec une marge d'erreur)
        activation_rate = sum(results) / len(results)
        self.assertGreater(activation_rate, 0.3)  # Au moins 30%
        self.assertLess(activation_rate, 0.7)     # Au plus 70%
        
        # Le même utilisateur doit toujours avoir le même résultat
        user_123_result1 = FeatureFlagsService.is_enabled('test_rollout', 123)
        user_123_result2 = FeatureFlagsService.is_enabled('test_rollout', 123)
        self.assertEqual(user_123_result1, user_123_result2)
    
    def test_get_all_flags(self):
        """Test de la récupération de tous les flags"""
        from .services.feature_flags_service import FeatureFlagsService
        
        all_flags = FeatureFlagsService.get_all_flags()
        
        # Vérifier que tous nos flags de test sont présents
        self.assertIn('test_enabled', all_flags)
        self.assertIn('test_disabled', all_flags)
        self.assertIn('test_rollout', all_flags)
        
        # Vérifier les valeurs
        self.assertTrue(all_flags['test_enabled'])
        self.assertFalse(all_flags['test_disabled'])
        self.assertTrue(all_flags['test_rollout'])  # Rollout n'affecte pas get_all_flags
    
    def test_cache_functionality(self):
        """Test du cache des feature flags"""
        from .services.feature_flags_service import FeatureFlagsService
        from django.core.cache import cache
        
        # Premier appel - doit charger depuis la DB
        result1 = FeatureFlagsService.is_enabled('test_enabled')
        self.assertTrue(result1)
        
        # Vérifier que le cache est peuplé
        cache_key = f"{FeatureFlagsService.CACHE_PREFIX}test_enabled"
        cached_data = cache.get(cache_key)
        self.assertIsNotNone(cached_data)
        self.assertTrue(cached_data['enabled'])
        
        # Modifier directement la DB sans passer par le modèle Django (évite les signaux)
        from django.db import connection
        with connection.cursor() as cursor:
            cursor.execute(
                "UPDATE core_featureflag SET enabled = %s WHERE name = %s",
                [False, 'test_enabled']
            )
        
        # Le résultat doit toujours venir du cache (ancien)
        result2 = FeatureFlagsService.is_enabled('test_enabled')
        self.assertTrue(result2)  # Cache pas encore invalidé
        
        # Invalider manuellement le cache
        FeatureFlagsService.invalidate_cache('test_enabled')
        
        # Maintenant le résultat doit venir de la DB (nouveau)
        result3 = FeatureFlagsService.is_enabled('test_enabled')
        self.assertFalse(result3)
    
    def test_cache_invalidation_signals(self):
        """Test de l'invalidation automatique du cache via signaux"""
        from .services.feature_flags_service import FeatureFlagsService
        from .models import FeatureFlag
        
        # Créer un nouveau flag
        new_flag = FeatureFlag.objects.create(
            name='test_signal',
            enabled=True,
            description='Test des signaux'
        )
        
        # Vérifier qu'il est activé
        self.assertTrue(FeatureFlagsService.is_enabled('test_signal'))
        
        # Modifier le flag (doit déclencher le signal)
        new_flag.enabled = False
        new_flag.save()
        
        # Le cache doit être invalidé automatiquement
        self.assertFalse(FeatureFlagsService.is_enabled('test_signal'))
        
        # Supprimer le flag (doit aussi déclencher le signal)
        new_flag.delete()
        
        # Le flag ne doit plus être trouvé
        self.assertFalse(FeatureFlagsService.is_enabled('test_signal'))
    
    def test_model_validation(self):
        """Test de la validation du modèle FeatureFlag"""
        from .models import FeatureFlag
        from django.core.exceptions import ValidationError
        
        # Tester rollout_percentage valide
        flag = FeatureFlag(name='test_validation', enabled=True, rollout_percentage=50)
        flag.clean()  # Ne doit pas lever d'exception
        
        # Tester rollout_percentage invalide (>100)
        flag.rollout_percentage = 150
        with self.assertRaises(ValidationError):
            flag.clean()
        
        # Tester rollout_percentage invalide (<0)
        flag.rollout_percentage = -10
        with self.assertRaises(ValidationError):
            flag.clean()
    
    def test_config_endpoint_with_db_flags(self):
        """Test de l'endpoint config avec les flags de la DB"""
        url = reverse('api_config')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        feature_flags = response.data['feature_flags']
        
        # Les flags de la DB doivent être présents
        self.assertIn('test_enabled', feature_flags)
        self.assertIn('test_disabled', feature_flags)
        self.assertIn('test_rollout', feature_flags)
        
        # Vérifier les valeurs
        self.assertTrue(feature_flags['test_enabled'])
        self.assertFalse(feature_flags['test_disabled'])
        self.assertTrue(feature_flags['test_rollout'])
        
        # Les flags par défaut doivent toujours être présents
        self.assertIn('social_profile', feature_flags)
        self.assertIn('friend_system', feature_flags)


class RecommendationServiceTestCase(TestCase):
    """
    Tests pour le service RecommendationService
    """
    
    def setUp(self):
        """Configuration des tests"""
        from django.contrib.auth.models import User
        from .models import UserPreference, List as TasteList, ListItem, ExternalReference, APICache
        
        # Créer un utilisateur de test
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        
        # Nettoyer le cache API
        APICache.objects.all().delete()
        
        # Créer quelques préférences utilisateur pour filtrage
        UserPreference.objects.create(
            user=self.user,
            external_id='liked_movie_123',
            content_type='FILMS',
            source='tmdb',
            action='liked',
            title='Film Aimé'
        )
        
        UserPreference.objects.create(
            user=self.user,
            external_id='disliked_movie_456',
            content_type='FILMS',
            source='tmdb', 
            action='disliked',
            title='Film Pas Aimé'
        )
        
        # Créer une liste avec un contenu
        taste_list = TasteList.objects.create(
            name='Ma Liste Films',
            category='FILMS',
            owner=self.user
        )
        
        list_item = ListItem.objects.create(
            title='Film dans Liste',
            list=taste_list
        )
        
        ExternalReference.objects.create(
            list_item=list_item,
            external_id='in_list_movie_789',
            external_source='tmdb'
        )
    
    def test_get_recommendations_returns_non_empty_list(self):
        """Test que get_recommendations retourne une liste non vide"""
        from .match_services import RecommendationService
        
        service = RecommendationService()
        recommendations = service.get_recommendations(self.user, count=10)
        
        # Vérifier qu'on a des recommandations
        self.assertGreater(len(recommendations), 0)
        self.assertLessEqual(len(recommendations), 10)
    
    def test_get_recommendations_by_category(self):
        """Test des recommandations par catégorie spécifique"""
        from .match_services import RecommendationService
        
        service = RecommendationService()
        
        # Tester chaque catégorie
        for category in ['FILMS', 'SERIES', 'MUSIQUE', 'LIVRES']:
            with self.subTest(category=category):
                recommendations = service.get_recommendations(self.user, category=category, count=5)
                
                # Vérifier qu'on a des recommandations
                self.assertGreater(len(recommendations), 0)
                
                # Vérifier que toutes les recommandations sont de la bonne catégorie
                for item in recommendations:
                    self.assertEqual(item['content_type'], category)
    
    def test_recommendations_have_required_fields(self):
        """Test que les recommandations ont tous les champs requis"""
        from .match_services import RecommendationService
        
        service = RecommendationService()
        recommendations = service.get_recommendations(self.user, count=5)
        
        required_fields = ['external_id', 'content_type', 'source', 'title', 'compatibility_score']
        
        for item in recommendations:
            for field in required_fields:
                self.assertIn(field, item)
                self.assertIsNotNone(item[field])
    
    def test_no_duplicate_external_ids(self):
        """Test qu'il n'y a pas de doublons d'external_id"""
        from .match_services import RecommendationService
        
        service = RecommendationService()
        recommendations = service.get_recommendations(self.user, count=20)
        
        external_ids = [item['external_id'] for item in recommendations]
        unique_ids = set(external_ids)
        
        # Pas de doublons (critère d'acceptation)
        self.assertEqual(len(external_ids), len(unique_ids))
    
    def test_filter_user_content_excludes_seen_items(self):
        """Test que _filter_user_content exclut correctement le contenu vu"""
        from .match_services import RecommendationService
        
        service = RecommendationService()
        
        # Créer une liste d'items de test incluant du contenu déjà vu
        test_items = [
            {
                'external_id': 'liked_movie_123',  # Déjà aimé
                'content_type': 'FILMS',
                'source': 'tmdb',
                'title': 'Film Test 1'
            },
            {
                'external_id': 'disliked_movie_456',  # Déjà pas aimé
                'content_type': 'FILMS', 
                'source': 'tmdb',
                'title': 'Film Test 2'
            },
            {
                'external_id': 'in_list_movie_789',  # Déjà dans une liste
                'content_type': 'FILMS',
                'source': 'tmdb', 
                'title': 'Film Test 3'
            },
            {
                'external_id': 'new_movie_999',  # Nouveau contenu
                'content_type': 'FILMS',
                'source': 'tmdb',
                'title': 'Film Test 4'
            }
        ]
        
        filtered_items = service._filter_user_content(self.user, test_items)
        
        # Seul le nouveau contenu doit rester
        self.assertEqual(len(filtered_items), 1)
        self.assertEqual(filtered_items[0]['external_id'], 'new_movie_999')
    
    def test_compatibility_score_present(self):
        """Test que le score de compatibilité est présent (placeholder acceptable)"""
        from .match_services import RecommendationService
        
        service = RecommendationService()
        recommendations = service.get_recommendations(self.user, count=5)
        
        for item in recommendations:
            # Score présent et dans une fourchette raisonnable
            self.assertIn('compatibility_score', item)
            score = item['compatibility_score']
            self.assertIsInstance(score, (int, float))
            self.assertGreaterEqual(score, 0)
            self.assertLessEqual(score, 100)
    
    def test_music_recommendations_return_mock_data(self):
        """Test que les recommandations musique retournent des données mockées"""
        from .match_services import RecommendationService
        
        service = RecommendationService()
        music_items = service._get_music_recommendations(self.user, 5)
        
        # Vérifier qu'on a des données
        self.assertGreater(len(music_items), 0)
        
        # Vérifier que c'est du contenu musical
        for item in music_items:
            self.assertEqual(item['content_type'], 'MUSIQUE')
            self.assertEqual(item['source'], 'spotify')
            self.assertIn('external_id', item)
            self.assertIn('title', item)
    
    def test_fallback_data_when_no_api_keys(self):
        """Test que les données de fallback sont utilisées quand les clés API ne sont pas disponibles"""
        from .match_services import RecommendationService
        
        # Créer un service sans clés API
        service = RecommendationService()
        service.tmdb_api_key = ''
        service.google_books_api_key = ''
        
        # Tester les films (devrait utiliser fallback)
        movies = service._get_movie_recommendations(self.user, 3)
        self.assertGreater(len(movies), 0)
        for movie in movies:
            self.assertEqual(movie['content_type'], 'FILMS')
        
        # Tester les livres (devrait utiliser fallback) 
        books = service._get_book_recommendations(self.user, 3)
        self.assertGreater(len(books), 0)
        for book in books:
            self.assertEqual(book['content_type'], 'LIVRES')
    
    def test_heterogeneous_recommendations(self):
        """Test que les recommandations mélangent différentes catégories"""
        from .match_services import RecommendationService
        
        service = RecommendationService()
        recommendations = service.get_recommendations(self.user, count=12)
        
        # Vérifier qu'on a plusieurs catégories différentes
        categories = set(item['content_type'] for item in recommendations)
        self.assertGreater(len(categories), 1)  # Au moins 2 catégories différentes
        
        # Les catégories devraient être interleaved (pas toutes les mêmes en bloc)
        first_half_categories = set(item['content_type'] for item in recommendations[:6])
        second_half_categories = set(item['content_type'] for item in recommendations[6:])
        
        # Les deux moitiés devraient contenir des catégories variées
        if len(recommendations) >= 8:  # Seulement si on a assez de recommandations
            self.assertGreater(len(first_half_categories.intersection(second_half_categories)), 0)
