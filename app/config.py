# app/config.py

import os
from dotenv import load_dotenv

load_dotenv()

class Config(object):
    SECRET_KEY = os.environ.get('SECRET_KEY')
    if not SECRET_KEY:
        raise ValueError("SECRET_KEY environment variable is required.")
    
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    WTF_CSRF_ENABLED = True  # Ensure CSRF protection is enabled

    @classmethod
    def validate_config(cls):
        required_vars = ["SECRET_KEY", "SQLALCHEMY_DATABASE_URI"]
        for var in required_vars:
            if not getattr(cls, var):
                raise ValueError(f"{var} environment variable is required.")
    # Add these lines
    RATELIMIT_STORAGE_URI = 'memory://'  # For development, use Redis in production
    RATELIMIT_STRATEGY = 'fixed-window'
    RATELIMIT_DEFAULT = "200 per day;50 per hour"

class DevelopmentConfig(Config):
    DEBUG = True
    TESTING = False
    SQLALCHEMY_DATABASE_URI = f"sqlite:///{os.path.abspath(os.path.join('instance', 'site.db'))}"

class TestingConfig(Config):
    DEBUG = False
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    WTF_CSRF_ENABLED = True  # Enable CSRF in testing to match production
    SERVER_NAME = 'localhost'
    APPLICATION_ROOT = '/'
    PREFERRED_URL_SCHEME = 'http'

class ProductionConfig(Config):
    DEBUG = False
    TESTING = False
    SQLALCHEMY_DATABASE_URI = f"sqlite:///{os.path.abspath(os.path.join('instance', 'site.db'))}"

config_by_name = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}
