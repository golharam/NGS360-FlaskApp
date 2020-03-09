'''
Test server-side endpoints in app.blueprint.main
'''
from unittest import TestCase
from testfixtures import LogCapture
from config import TestConfig
from app import create_app, DB as db
from app.models import User

class BlueprintMainTests(TestCase):
    ''' Basic test cases '''
    def setUp(self):
        test_config = TestConfig()
        self.app = create_app(test_config)
        self.app_context = self.app.app_context()
        self.app_context.push()
        self.client = self.app.test_client()
        db.create_all()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.client = None
        self.app_context.pop()

    def login(self):
        user = User(username='testuser',
                    email='testuser@nowhere.com')
        user.set_password('password')
        db.session.add(user)
        db.session.commit()

        return self.client.post('/login', data=dict(
            username='testuser',
            password='password'
        ), follow_redirects=True)

    def test_index(self):
        ''' Test / '''
        self.login()
        res = self.client.get('/')
        assert b'<title>NGS 360</title>' in res.data

    def test_basespace(self):
        ''' Test /basespace '''
        rv = self.login()
        res = self.client.get('/basespace')
        assert res.status_code == 200

    def test_basespace_archiverun(self):
        self.skipTest("Not yet implemented")

    def test_projects(self):
        ''' Test /projects '''
        self.login()
        res = self.client.get('/projects')
        assert res.status_code == 200

    def test_project(self):
        ''' Test /projects/P-1 '''
        self.login()
        res = self.client.get('/projects/P-1')
        assert res.status_code == 200

    def test_jobs(self):
        ''' Test /jobs '''
        self.login()
        res = self.client.get('/jobs')
        assert res.status_code == 200

    def test_jobs_user_in_request(self):
        ''' Test /jobs '''
        self.login()
        res = self.client.get('/jobs?username=testuser')
        assert res.status_code == 200

    def test_illumina_runs(self):
        ''' Test /illumina_runs '''
        self.login()
        res = self.client.get('/illumina_runs')
        assert res.status_code == 200

def test_file_logging():
    ''' Make sure file logging is set up '''
    file_config = TestConfig()
    file_config.TESTING = False
    file_config.FLASK_LOG_FILE = "/dev/null"
    file_config.FLASK_LOG_LEVEL = "INFO"
    with LogCapture() as test_logger:
        create_app(file_config)
        test_logger.check_present(
            ('app', 'INFO', 'NGS360 loading'),
            ('app', 'INFO', 'Setting up file logging to /dev/null'),
            ('app', 'INFO', 'NGS360 loaded.')
        )

def test_email_logging():
    ''' Make sure email logging is set up '''
    email_config = TestConfig()
    email_config.TESTING = False
    email_config.MAIL_SERVER = "xyz"
    email_config.MAIL_PORT = 1
    email_config.MAIL_USERNAME = "someone"
    email_config.MAIL_PASSWORD = ''
    email_config.MAIL_USE_TLS = 1
    email_config.ADMINS = "abc"
    with LogCapture() as test_logger:
        create_app(email_config)
        test_logger.check_present(
            ('app', 'INFO', 'NGS360 loading'),
            ('app', 'INFO', 'Setting up email logger'),
            ('app', 'INFO', 'NGS360 loaded.')
        )
