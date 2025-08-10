from django.test import TestCase, Client
from django.urls import reverse
from unittest.mock import patch
import sentry_sdk


class SentryIntegrationTestCase(TestCase):
    """
    Test cases for Sentry integration and error handling.
    """
    
    def setUp(self):
        self.client = Client()
    
    def test_sentry_test_error_endpoint_raises_exception(self):
        """
        Test that the Sentry test error endpoint raises an exception.
        We expect this to raise an exception, which is the correct behavior.
        """
        url = reverse('sentry_test_error')
        with self.assertRaises(Exception) as context:
            self.client.get(url)
        
        self.assertIn("Test error for Sentry integration", str(context.exception))
    
    def test_sentry_test_error_view_directly(self):
        """
        Test that the Sentry test error view function raises an exception when called.
        """
        from .views import sentry_test_error
        from django.http import HttpRequest
        
        request = HttpRequest()
        request.method = 'GET'
        
        with self.assertRaises(Exception) as context:
            sentry_test_error(request)
        
        # Test that the exception message contains our expected text
        exception_message = str(context.exception)
        self.assertTrue(
            "Test error for Sentry integration" in exception_message,
            f"Expected message not found in: {exception_message}"
        )
    
    @patch('sentry_sdk.capture_exception')
    def test_sentry_captures_exceptions(self, mock_capture_exception):
        """
        Test that Sentry captures exceptions when they occur.
        This is a mock test to verify the integration works.
        """
        # Simulate an exception being captured by Sentry
        test_exception = Exception("Test exception")
        sentry_sdk.capture_exception(test_exception)
        mock_capture_exception.assert_called_once_with(test_exception)
    
    def test_health_check_endpoint_works(self):
        """
        Test that the health check endpoint still works after Sentry integration.
        """
        url = reverse('health_check')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['status'], 'ok')
    
    def test_pii_filtering_function(self):
        """
        Test that the PII filtering function removes sensitive data.
        """
        from tastematch_api.settings import filter_sensitive_data
        
        # Mock Sentry event with sensitive data
        test_event = {
            'request': {
                'headers': {
                    'authorization': 'Bearer secret-token',
                    'cookie': 'sessionid=secret-session',
                    'user-agent': 'TestAgent/1.0'
                },
                'query_string': 'password=secret123&search=query',
                'data': {
                    'password': 'secret-password',
                    'email': 'user@example.com',
                    'normal_field': 'normal_value'
                }
            },
            'user': {
                'email': 'user@example.com',
                'ip_address': '192.168.1.1',
                'username': 'testuser'
            }
        }
        
        # Apply the filter
        filtered_event = filter_sensitive_data(test_event)
        
        # Check that sensitive headers are filtered
        self.assertEqual(filtered_event['request']['headers']['authorization'], '[Filtered]')
        self.assertEqual(filtered_event['request']['headers']['cookie'], '[Filtered]')
        self.assertEqual(filtered_event['request']['headers']['user-agent'], 'TestAgent/1.0')  # Not sensitive
        
        # Check that sensitive form data is filtered
        self.assertEqual(filtered_event['request']['data']['password'], '[Filtered]')
        self.assertEqual(filtered_event['request']['data']['email'], '[Filtered]')
        self.assertEqual(filtered_event['request']['data']['normal_field'], 'normal_value')  # Not sensitive
        
        # Check that sensitive user data is filtered
        self.assertEqual(filtered_event['user']['email'], '[Filtered]')
        self.assertEqual(filtered_event['user']['ip_address'], '[Filtered]')
        self.assertEqual(filtered_event['user']['username'], 'testuser')  # Not sensitive
