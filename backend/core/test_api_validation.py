"""
Tests for strict API validation.
Validates that all API endpoints properly reject malformed inputs with 400 errors.
"""
from django.test import TestCase
from django.contrib.auth.models import User
from rest_framework.test import APIClient
from rest_framework import status
from django.urls import reverse
from .models import List, ListItem, ExternalReference


class APIValidationTestCase(TestCase):
    """Test strict validation for all API endpoints."""
    
    def setUp(self):
        """Set up test data."""
        self.client = APIClient()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.client.force_authenticate(user=self.user)
        
        # Create a test list
        self.test_list = List.objects.create(
            name='Test List',
            category=List.Category.FILMS,
            owner=self.user
        )

    def test_register_validation_required_fields(self):
        """Test that registration requires all mandatory fields."""
        # Test missing username
        response = self.client.post('/api/auth/register/', {
            'email': 'test@example.com', 
            'password': 'testpass123',
            'password2': 'testpass123'
        })
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('username', response.data)
        
        # Test missing email
        response = self.client.post('/api/auth/register/', {
            'username': 'testuser2',
            'password': 'testpass123', 
            'password2': 'testpass123'
        })
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('email', response.data)
        
        # Test missing password
        response = self.client.post('/api/auth/register/', {
            'username': 'testuser2',
            'email': 'test@example.com',
            'password2': 'testpass123'
        })
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('password', response.data)
        
        # Test missing password confirmation
        response = self.client.post('/api/auth/register/', {
            'username': 'testuser2',
            'email': 'test@example.com',
            'password': 'testpass123'
        })
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('password2', response.data)

    def test_register_validation_invalid_formats(self):
        """Test validation of field formats."""
        # Test invalid email format
        response = self.client.post('/api/auth/register/', {
            'username': 'testuser2',
            'email': 'invalid-email',
            'password': 'testpass123',
            'password2': 'testpass123'
        })
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('email', response.data)
        
        # Test password mismatch
        response = self.client.post('/api/auth/register/', {
            'username': 'testuser2',
            'email': 'test2@example.com',
            'password': 'testpass123',
            'password2': 'different'
        })
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('password', response.data)

    def test_register_validation_invalid_values(self):
        """Test validation of invalid values."""
        # Test empty strings
        response = self.client.post('/api/auth/register/', {
            'username': '',
            'email': 'test2@example.com',
            'password': 'testpass123',
            'password2': 'testpass123'
        })
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('username', response.data)
        
        # Test whitespace-only username
        response = self.client.post('/api/auth/register/', {
            'username': '   ',
            'email': 'test2@example.com',
            'password': 'testpass123',
            'password2': 'testpass123'
        })
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('username', response.data)

    def test_list_validation_invalid_category(self):
        """Test that list category validation works."""
        # Test invalid category
        response = self.client.post('/api/lists/', {
            'name': 'Test List',
            'category': 'INVALID_CATEGORY',
            'description': 'Test description'
        })
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('category', response.data)
        
        # Test empty category
        response = self.client.post('/api/lists/', {
            'name': 'Test List',
            'category': '',
            'description': 'Test description'
        })
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('category', response.data)

    def test_list_validation_required_fields(self):
        """Test list required field validation."""
        # Test missing category (should be required)
        response = self.client.post('/api/lists/', {
            'name': 'Test List',
            'description': 'Test description'
        })
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('category', response.data)

    def test_list_item_validation_required_fields(self):
        """Test list item required field validation."""
        # Test missing title
        response = self.client.post(f'/api/lists/{self.test_list.id}/items/', {
            'description': 'Test description',
            'position': 1
        })
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('title', response.data)
        
        # Test empty title
        response = self.client.post(f'/api/lists/{self.test_list.id}/items/', {
            'title': '',
            'description': 'Test description',
            'position': 1
        })
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('title', response.data)
        
        # Test whitespace-only title
        response = self.client.post(f'/api/lists/{self.test_list.id}/items/', {
            'title': '   ',
            'description': 'Test description',
            'position': 1
        })
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('title', response.data)

    def test_list_item_validation_invalid_types(self):
        """Test list item type validation."""
        # Test invalid position (negative)
        response = self.client.post(f'/api/lists/{self.test_list.id}/items/', {
            'title': 'Test Item',
            'description': 'Test description',
            'position': -1
        })
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('position', response.data)
        
        # Test invalid position (string)
        response = self.client.post(f'/api/lists/{self.test_list.id}/items/', {
            'title': 'Test Item',
            'description': 'Test description',
            'position': 'invalid'
        })
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        
        # Test invalid is_watched type
        response = self.client.post(f'/api/lists/{self.test_list.id}/items/', {
            'title': 'Test Item',
            'description': 'Test description',
            'position': 1,
            'is_watched': 'invalid'
        })
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_quick_add_validation(self):
        """Test quick add item validation."""
        # Test missing title
        response = self.client.post('/api/quick-add/', {
            'category': 'FILMS',
            'description': 'Test description'
        })
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('title', response.data)
        
        # Test invalid category
        response = self.client.post('/api/quick-add/', {
            'title': 'Test Item',
            'category': 'INVALID',
            'description': 'Test description'
        })
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('category', response.data)
        
        # Test missing category
        response = self.client.post('/api/quick-add/', {
            'title': 'Test Item',
            'description': 'Test description'
        })
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('category', response.data)

    def test_import_external_validation(self):
        """Test external import validation."""
        # Test missing external_id
        response = self.client.post('/api/import/external/', {
            'source': 'tmdb',
            'category': 'FILMS'
        })
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('external_id', response.data)
        
        # Test invalid source
        response = self.client.post('/api/import/external/', {
            'external_id': '123',
            'source': 'invalid_source',
            'category': 'FILMS'
        })
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('source', response.data)
        
        # Test invalid category
        response = self.client.post('/api/import/external/', {
            'external_id': '123',
            'source': 'tmdb',
            'category': 'INVALID'
        })
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('category', response.data)

    def test_field_length_validation(self):
        """Test field length constraints."""
        # Test title too long (over 200 chars)
        long_title = 'x' * 201
        response = self.client.post(f'/api/lists/{self.test_list.id}/items/', {
            'title': long_title,
            'description': 'Test description',
            'position': 1
        })
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('title', response.data)
        
        # Test list name too long (over 100 chars)
        long_name = 'x' * 101
        response = self.client.post('/api/lists/', {
            'name': long_name,
            'category': 'FILMS',
            'description': 'Test description'
        })
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('name', response.data)

    def test_unique_constraint_validation(self):
        """Test unique constraint validations."""
        # Try to create duplicate username
        response = self.client.post('/api/auth/register/', {
            'username': 'testuser',  # Already exists
            'email': 'test2@example.com',
            'password': 'testpass123',
            'password2': 'testpass123'
        })
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        
        # TODO: Add tests for list unique constraints once properly implemented

    def test_malformed_json_handling(self):
        """Test handling of malformed JSON."""
        response = self.client.post(
            '/api/auth/register/',
            data='{"invalid": json}',
            content_type='application/json'
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_extra_fields_rejection(self):
        """Test rejection of unexpected fields."""
        response = self.client.post('/api/auth/register/', {
            'username': 'testuser2',
            'email': 'test2@example.com',
            'password': 'testpass123',
            'password2': 'testpass123',
            'unexpected_field': 'should_be_ignored'
        })
        # Should succeed but ignore unexpected field
        # Or should return 400 if we want strict validation
        # This depends on our validation policy
        pass  # TODO: Define policy for extra fields

    def test_authentication_required(self):
        """Test that authentication is required for protected endpoints."""
        # Unauthenticated client
        unauth_client = APIClient()
        
        # Test creating list without auth
        response = unauth_client.post('/api/lists/', {
            'name': 'Test List',
            'category': 'FILMS',
            'description': 'Test description'
        })
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        
        # Test creating list item without auth
        response = unauth_client.post(f'/api/lists/{self.test_list.id}/items/', {
            'title': 'Test Item',
            'description': 'Test description'
        })
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)