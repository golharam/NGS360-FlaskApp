import pytest
from unittest import TestCase
from app import *

class TestConfig(object):
    TESTING = True
    DEBUG = False

class BasicTests(TestCase):
    def setUp(self):
        self.app = create_app(TestConfig)
        self.app_context = self.app.app_context()
        self.app_context.push()
        self.client = self.app.test_client()

    def tearDown(self):
        self.client = None
        self.app_context.pop()

    def test_root(self):
        """Test the default route."""
        res = self.client.get('/')
        assert b'Hello!' in res.data
        assert b'<b>Testing:</b> True' in res.data
        assert b'<b>Debug:</b> False' in res.data

