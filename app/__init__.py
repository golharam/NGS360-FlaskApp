'''
NGS360 Main Application package
Author: Ryan Golhar <ryan.golhar@bms.com>
'''
# pylint: disable=C0415
import logging
from logging.handlers import TimedRotatingFileHandler, SMTPHandler
import os

from flask import Flask
from flask_boto3 import Boto3
from flask_login import LoginManager
from flask_migrate import Migrate
from flask_restplus import Api
from flask_sqlalchemy import SQLAlchemy

from config import DefaultConfig
from app.base_space import BaseSpace
from app.seven_bridges import SevenBridges

DB = SQLAlchemy()
MIGRATE = Migrate()

API = Api()
BASESPACE = BaseSpace()
BOTO3 = Boto3()
LOGINMANAGER = LoginManager()
SEVENBRIDGES = SevenBridges()

def create_app(config_class=DefaultConfig):
    '''
    Application factory
    '''
    app = Flask(__name__)

    # https://flask.palletsprojects.com/en/1.1.x/config/
    app.config.from_object(config_class)
    app.config.from_envvar('FLASK_CONFIG', silent=True)
    app.logger.info('%s loading', app.config['APP_NAME'])
    app.logger.info("Connect to database %s", app.config['SQLALCHEMY_DATABASE_URI'])
    app.logger.info("ProjectRegister URL: %s", app.config['PROJECTREGISTRY'])
    app.logger.info("BaseSpace Token: %s", app.config['BASESPACE_TOKEN'])
    app.logger.info("SevenBridges Token: %s", app.config['SB_AUTH_TOKEN'])
    app.logger.info("AWS Batch Job Definition: %s", app.config['JOB_DEFINITION'])
    app.logger.info("AWS Batch Job Queue: %s", app.config['JOB_QUEUE'])

    DB.init_app(app)
    MIGRATE.init_app(app, DB)

    BASESPACE.init_app(app)
    BOTO3.init_app(app)
    LOGINMANAGER.init_app(app)
    LOGINMANAGER.login_view = 'user.login'
    SEVENBRIDGES.init_app(app)

    if not app.debug and not app.testing:
        # If FLASK_LOG_FILE and FLASK_LOG_LEVEL env vars defined, set up logging.
        if 'FLASK_LOG_FILE' in app.config and 'FLASK_LOG_LEVEL' in app.config and \
            app.config['FLASK_LOG_FILE'] is not None:
            app.logger.info("Setting up file logging to %s", app.config['FLASK_LOG_FILE'])
            file_handler = TimedRotatingFileHandler(app.config['FLASK_LOG_FILE'], when='midnight',
                                                    backupCount=10)
            file_handler.setFormatter(logging.Formatter(
                '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'))
            file_handler.setLevel(app.config['FLASK_LOG_LEVEL'])
            app.logger.addHandler(file_handler)

        # Send emails on critical errors
        if 'MAIL_SERVER' in app.config and app.config['MAIL_SERVER'] is not None:
            auth = None
            app.logger.info("Setting up email logger")
            if 'MAIL_USERNAME' in app.config or 'MAIL_PASSWORD' in app.config:
                auth = (app.config['MAIL_USERNAME'], app.config['MAIL_PASSWORD'])
            secure = None
            if 'MAIL_USE_TLS' in app.config:
                secure = ()
            mail_handler = SMTPHandler(
                mailhost=(app.config['MAIL_SERVER'], app.config['MAIL_PORT']),
                fromaddr='no-reply@' + app.config['MAIL_SERVER'],
                toaddrs=app.config['ADMINS'], subject='%s Failure' % app.config['APP_NAME'],
                credentials=auth, secure=secure)
            mail_handler.setLevel(logging.ERROR)
            app.logger.addHandler(mail_handler)

    from app.blueprints.main import BP as main_bp
    app.register_blueprint(main_bp)

    from app.api import BLUEPRINT as api_bp
    app.register_blueprint(api_bp)

    from app.blueprints.user import BP as user_bp
    app.register_blueprint(user_bp)

    from app.blueprints.basespace import BP as basespace_bp
    app.register_blueprint(basespace_bp)

    from app.blueprints.aws_batch import BP as aws_batch_bp
    app.register_blueprint(aws_batch_bp)

    app.logger.info('%s loaded.', app.config['APP_NAME'])
    return app
