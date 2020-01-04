'''
This module defines the DefaultConfig the app expects.
The TestConfig class is used for unit test.  I'm not sure
it belongs here.

For production, a production config should be created outside
of the app source code in a file, pointed to by FLASK_CONFIG
env var.

# https://flask.palletsprojects.com/en/1.1.x/config/
'''
import os
from dotenv import load_dotenv

BASEDIR = os.path.abspath(os.path.dirname(__file__))
load_dotenv(os.path.join(BASEDIR, '.env'))

class DefaultConfig:
    ''' Default config settings that can be overridden '''
    APP_NAME = "NGS360"
    SECRET_KEY = os.environ.get('SECRET_KEY') or "changeme"
    PROJECTREGISTRY = os.environ.get("PROJECTREGISTRY") or None
    TESTING = False

    # For production, define this to a production database
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'sqlite:///' + os.path.join(BASEDIR, 'app.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # For production, define these env vars:
    # FLASK_LOG_FILE = /path/to/log/file
    # FLASK_LOG_LEVEL = INFO

    BASESPACE_TOKEN = os.environ.get('BASESPACE_TOKEN') or None
    SB_AUTH_TOKEN = os.environ.get('SB_AUTH_TOKEN') or None

    BCL2FASTQ_JOB = os.environ.get('BCL2FASTQ_JOB') or None
    BCL2FASTQ_QUEUE = os.environ.get('BCL2FASTQ_QUEUE') or None
    SCRNASEQ_LAMBDA_FN = os.environ.get('SCRNASEQ_LAMBDA_FN') or None

    BOTO3_SERVICES = ['batch', 'lambda', 'logs', 's3']

    JOB_DEFINITION = os.environ.get('NGS_JOB') or None
    JOB_QUEUE = os.environ.get('NGS_JOB_QUEUE') or None

    JIRA_SERVER = os.environ.get('JIRA_SERVER') or None
    JIRA_USER = os.environ.get('JIRA_USER') or None
    JIRA_PASSKEY = os.environ.get('JIRA_PASSKEY') or None
    JIRA_BOARD = os.environ.get('JIRA_BOARD') or None
    JIRA_PROJECTID_FIELD = os.environ.get('JIRA_PROJECTID_FIELD') or None

    # Email error log settings
    # MAIL_SERVER = mailserver
    # MAIL_PORT
    # MAIL_USERNAME = set to mail server login, if needed
    # MAIL_PASSWORD =
    # MAIL_USE_TLS = True
    # ADMINS = comma separate list of who should get emailed

    # JIRA_FEEDBACK =
    # JIRA_BUGREPORT =

    HELP_URL = os.environ.get("HELP_URL") or None
    XPRESS_RESTAPI_ENDPOINT = os.environ.get("XPRESS_RESTAPI_ENDPOINT") or None

class TestConfig(DefaultConfig):
    ''' Config settings for unit testing '''
    TESTING = True
    # Don't use sqllite in memory database since it runs in a different
    # thread.   Setting it up for unittests doesn't work.  Instead, use an
    # on disk file.
    # Ref: https://gehrcke.de/2015/05/in-memory-sqlite-database-and-flask-a-threading-trap/
    #SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"
    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(BASEDIR, 'test.db')

    WTF_CSRF_ENABLED = False
    # Bypassing logins makes front end testing easier, however
    # it means we may skip some functionality that needs to be
    # tested when a user is logged in.
    #LOGIN_DISABLED = True
