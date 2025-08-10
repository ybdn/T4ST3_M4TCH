from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User
from rest_framework.test import APITestCase
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken


class MetricsTestCase(TestCase):
    def test_metrics_endpoint_accessible(self):
        """Test that the metrics endpoint is accessible and returns Prometheus format"""
        response = self.client.get('/metrics')
        self.assertEqual(response.status_code, 200)
        self.assertIn('# HELP', response.content.decode())
        self.assertIn('# TYPE', response.content.decode())


class RecommendationMetricsTestCase(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser', 
            password='testpass123',
            email='test@example.com'
        )
        refresh = RefreshToken.for_user(self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {refresh.access_token}')

    def test_suggestions_endpoint_generates_metrics(self):
        """Test that calling suggestions endpoint generates custom metrics"""
        # Call the suggestions endpoint
        response = self.client.get('/api/suggestions/?category=FILMS&limit=5')
        self.assertEqual(response.status_code, 200)
        
        # Check that metrics endpoint shows our custom metrics
        metrics_response = self.client.get('/metrics')
        metrics_content = metrics_response.content.decode()
        
        # Verify custom metrics are present
        self.assertIn('recommendation_requests_total', metrics_content)
        self.assertIn('recommendation_latency_seconds', metrics_content)
        self.assertIn('recommendation_type="suggestions"', metrics_content)
        self.assertIn('category="FILMS"', metrics_content)
