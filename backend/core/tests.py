from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from .models import List, ListItem


class HealthCheckTestCase(TestCase):
    """Test pour vérifier que l'endpoint health check fonctionne"""
    
    def test_health_check_endpoint(self):
        """Vérifier que l'endpoint /api/health/ retourne 200"""
        response = self.client.get('/api/health/')
        self.assertEqual(response.status_code, 200)
        self.assertIn('status', response.json())


class AuthenticationTestCase(APITestCase):
    """Tests pour l'authentification JWT"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        
    def test_register_user(self):
        """Test d'inscription d'un nouvel utilisateur"""
        url = reverse('auth_register')
        data = {
            'username': 'newuser',
            'email': 'newuser@example.com',
            'password': 'newpass123',
            'password2': 'newpass123'
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn('username', response.json())
        
    def test_login_user(self):
        """Test de connexion avec JWT"""
        url = reverse('token_obtain_pair')
        data = {
            'username': 'testuser',
            'password': 'testpass123'
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.json())
        self.assertIn('refresh', response.json())
        
    def test_token_refresh(self):
        """Test de rafraîchissement du token"""
        refresh = RefreshToken.for_user(self.user)
        url = reverse('token_refresh')
        data = {'refresh': str(refresh)}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.json())


class UserProfileTestCase(APITestCase):
    """Tests pour le profil utilisateur"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.client = APIClient()
        refresh = RefreshToken.for_user(self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {refresh.access_token}')
        
    def test_get_user_profile(self):
        """Test de récupération du profil utilisateur"""
        url = reverse('user_profile')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json()['username'], 'testuser')


class ListsTestCase(APITestCase):
    """Tests pour la gestion des listes"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.client = APIClient()
        refresh = RefreshToken.for_user(self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {refresh.access_token}')
        
    def test_get_user_lists(self):
        """Test de récupération des listes utilisateur"""
        # Créer une liste pour l'utilisateur
        list_obj = List.objects.create(
            owner=self.user,
            name='Ma Liste Films',
            category=List.Category.FILMS
        )
        
        url = reverse('list-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(len(response.json()), 1)
        
    def test_create_list_disabled(self):
        """Test que la création directe de listes est désactivée (405)"""
        url = reverse('list-list')
        data = {
            'name': 'Nouvelle Liste',
            'category': List.Category.LIVRES,
            'description': 'Ma liste de livres préférés'
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)
        self.assertIn('création de listes', response.json()['detail'])


class ExternalApisTestCase(APITestCase):
    """Tests pour les APIs externes"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.client = APIClient()
        refresh = RefreshToken.for_user(self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {refresh.access_token}')
        
    def test_search_external_endpoint(self):
        """Test de l'endpoint de recherche externe (format de réponse)"""
        url = reverse('search_external')
        params = {'query': 'test', 'type': 'movie'}
        response = self.client.get(url, params)
        # Vérifier que l'endpoint répond (même sans clés API configurées)
        self.assertIn(response.status_code, [200, 400, 503])  # 200 si clés OK, 400/503 sinon
        
    def test_trending_external_endpoint(self):
        """Test de l'endpoint de contenu tendance externe"""
        url = reverse('get_trending_external')
        params = {'type': 'movie'}
        response = self.client.get(url, params)
        # Vérifier que l'endpoint répond
        self.assertIn(response.status_code, [200, 400, 503])


class EndpointSecurityTestCase(APITestCase):
    """Tests de sécurité des endpoints"""
    
    def test_protected_endpoints_require_authentication(self):
        """Vérifier que les endpoints protégés nécessitent une authentification"""
        protected_urls = [
            reverse('user_profile'),
            reverse('list-list'),
            reverse('search_external'),
        ]
        
        for url in protected_urls:
            response = self.client.get(url)
            self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
            
    def test_public_endpoints_accessible(self):
        """Vérifier que les endpoints publics sont accessibles"""
        public_urls = [
            '/api/health/',
            reverse('auth_register'),
            reverse('token_obtain_pair'),
        ]
        
        for url in public_urls:
            response = self.client.get(url) if url == '/api/health/' else self.client.post(url, {})
            # Les endpoints publics ne doivent pas retourner 401
            self.assertNotEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
