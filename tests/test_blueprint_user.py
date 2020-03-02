from unittest import TestCase
from application import create_app, DB as db
from app.models import User
from config import TestConfig

class BlueprintUserTests(TestCase):
    def setUp(self):
        self.app = create_app(TestConfig)
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()
        self.client = self.app.test_client()
        self.client.testing = True

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.client = None
        self.app_context.pop()

    def test_login(self):
        res = self.client.get("/login")
        assert res.status_code == 200

    def test_logout(self):
        res = self.client.get("/logout")
        assert res.status_code == 302

    def test_get_register(self):
        res = self.client.get("/register")
        assert res.status_code == 200