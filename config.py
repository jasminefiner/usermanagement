import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY')

class DevelopmentConfig(Config):
    DEBUG = True

class TestingConfig(Config):
    TESTING = True

config = {
    'testing': TestingConfig,
    'development': DevelopmentConfig,

    'default': DevelopmentConfig,
}
