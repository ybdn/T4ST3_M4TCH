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
