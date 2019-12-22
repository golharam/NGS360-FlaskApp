import os

class Config(object):
    ''' Default config settings that can be overridden '''
    TESTING = os.getenv('TESTING', False)
    DEBUG = os.getenv('DEBUG', True)

