'''
NGS360 Main Application package
Author: Ryan Golhar <ryan.golhar@bms.com>
'''
import os

from flask import Flask
from config import DefaultConfig

def create_app(config_class=DefaultConfig):
    '''
    Application factory
    '''
    app = Flask(__name__)

    # https://flask.palletsprojects.com/en/1.1.x/config/
    app.config.from_object(config_class)
    app.config.from_envvar('FLASK_CONFIG', silent=True)

    from app.blueprints.main import BP as main_bp
    app.register_blueprint(main_bp)
    return app
