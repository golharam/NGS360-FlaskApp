'''
Unit Tests for /api/v0/test
'''
import json
from unittest import TestCase
from app import create_app, DB as db
from config import TestConfig

class NotificationTests(TestCase):
    def setUp(self):
        self.app = create_app(TestConfig)
        self.app_context = self.app.app_context()
        self.app_context.push()
        self.client = self.app.test_client()

    def tearDown(self):
        self.client = None
        self.app_context.pop()

    def test_api_test(self):
        # Set up
        # Test
        response = self.client.get('/api/v0/test')
        # Check
        assert response.status_code == 200
