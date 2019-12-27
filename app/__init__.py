'''
NGS360 Main Application package
Author: Ryan Golhar <ryan.golhar@bms.com>
'''
import logging
from logging.handlers import TimedRotatingFileHandler, SMTPHandler
import os

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager

from config import DefaultConfig

DB = SQLAlchemy()
MIGRATE = Migrate()
LOGINMANAGER = LoginManager()

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

    # Connect to Database
    DB.init_app(app)
    MIGRATE.init_app(app, DB)
    LOGINMANAGER.init_app(app)
    LOGINMANAGER.login_view = 'user.login'

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

    from app.blueprints.api import BP as api_bp
    app.register_blueprint(api_bp)

    from app.blueprints.user import BP as user_bp
    app.register_blueprint(user_bp)

    app.logger.info('%s loaded.', app.config['APP_NAME'])
    return app
