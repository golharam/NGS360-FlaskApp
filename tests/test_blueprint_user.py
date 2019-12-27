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

    def assert_flashes(self, expected_message, expected_category='message'):
        with self.client.session_transaction() as session:
            try:
                category, message = session['_flashes'][0]
            except KeyError:
                raise AssertionError('nothing flashed')
            assert expected_message in message
            assert expected_category == category

    def assert_in_session(self, key, value):
        with self.client.session_transaction() as session:
            assert key in session
            assert session[key] == value

    def assert_not_in_session(self, key):
        with self.client.session_transaction() as session:
            assert key not in session

    def test_login(self):
        res = self.client.get("/login")
        assert res.status_code == 200

    def test_login_submit_fails(self):
        self.client.post("/login", data=dict(
            username='testuser',
            password='testpass',
            remember_me='y'
        ), follow_redirects=False)
        self.assert_flashes("Invalid username or password")
        self.assert_not_in_session('user_id')

    def test_login_submit(self):
        user = User(username="testuser", email="testuser@someemail.com")
        user.set_password("testpass")
        db.session.add(user)
        db.session.commit()
        self.client.post("/login", data=dict(
            username='testuser',
            password='testpass',
            remember_me='y'
        ), follow_redirects=False)
        self.assert_in_session('user_id', '1')

    def test_login_already_authenticated(self):
        self.test_login_submit()
        res = self.client.get("/login", follow_redirects=False)
        assert res.status_code == 302

    def test_login_incorrectpassword(self):
        user = User(username="testuser", email="testuser@someemail.com")
        user.set_password("wrongpass")
        db.session.add(user)
        db.session.commit()
        self.client.post("/login", data=dict(
            username='testuser',
            password='testpass',
            remember_me='y'
        ), follow_redirects=False)
        self.assert_not_in_session('user_id')

    def test_logout(self):
        self.test_login_submit()
        self.client.get("/logout")
        self.assert_not_in_session('user_id')
