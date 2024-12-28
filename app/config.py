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
    RATELIMIT_USER_MANAGEMENT = "10 per minute"  # Rate limit for user management endpoints

class TestConfig(Config):
    DEBUG = False
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    WTF_CSRF_ENABLED = True  # Enable CSRF in testing to match production
    WTF_CSRF_SECRET_KEY = 'test-secret-key'  # Add a test CSRF secret key
    SERVER_NAME = 'localhost'
    APPLICATION_ROOT = '/'
    PREFERRED_URL_SCHEME = 'http'
    # Completely disable rate limiting in tests
    RATELIMIT_ENABLED = False
    RATELIMIT_STORAGE_URI = 'memory://'
    RATELIMIT_DEFAULT = "9999999 per second"  # Effectively disable rate limits
    RATELIMIT_USER_MANAGEMENT = "9999999 per second"
    RATELIMIT_BOT_OPERATIONS = "9999999 per second"
    RATELIMIT_LOGIN = "9999999 per second"  # Add specific login rate limit override

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
