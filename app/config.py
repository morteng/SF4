# app/config.py
import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key'
    SQLALCHEMY_DATABASE_URI = os.environ.get('SQLALCHEMY_DATABASE_URI') or 'sqlite:///app.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    WTF_CSRF_ENABLED = True
    WTF_CSRF_SECRET_KEY = os.environ.get('WTF_CSRF_SECRET_KEY') or SECRET_KEY
    
    # Rate limiting configuration
    RATELIMIT_STORAGE_URI = 'memory://'
    RATELIMIT_STRATEGY = 'fixed-window'
    RATELIMIT_DEFAULT = "200 per day;50 per hour"
    RATELIMIT_ENABLED = True

class TestConfig(Config):
    DEBUG = False
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    WTF_CSRF_ENABLED = True  # Enable CSRF in testing to match production
    WTF_CSRF_SECRET_KEY = 'test-secret-key'  # Add a test CSRF secret key
    SERVER_NAME = 'localhost'
    APPLICATION_ROOT = '/'
    PREFERRED_URL_SCHEME = 'http'
    
    # Ensure migrations run for in-memory database
    @classmethod
    def init_app(cls, app):
        super().init_app(app)
        with app.app_context():
            from flask_migrate import upgrade
            upgrade()
    
    # Disable all rate limiting in tests
    RATELIMIT_ENABLED = False
    RATELIMIT_STORAGE_URI = 'memory://'
    RATELIMIT_DEFAULT = "9999999 per second"
    RATELIMIT_USER_MANAGEMENT = "9999999 per second"
    RATELIMIT_BOT_OPERATIONS = "9999999 per second"
    RATELIMIT_LOGIN = "9999999 per second"
    RATELIMIT_GLOBAL = "9999999 per second"
    RATELIMIT_HEADERS_ENABLED = False
    RATELIMIT_IN_MEMORY_FALLBACK_ENABLED = True
    RATELIMIT_STRATEGY = 'fixed-window-elastic-expiry'
    
    # Enable detailed error logging for tests
    LOGGING_LEVEL = 'DEBUG'
    LOGGING_FORMAT = '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
    
    # Enable detailed error logging for tests
    LOGGING_LEVEL = 'DEBUG'
    LOGGING_FORMAT = '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
    
    # Notification settings
    NOTIFICATION_MAX_COUNT = 1000  # Increase for testing
    NOTIFICATION_CLEANUP_INTERVAL = 0  # Disable cleanup during tests

    @classmethod
    def init_app(cls, app):
        """Initialize the test application"""
        super().init_app(app)
        # Reset rate limiter storage before each test
        from flask_limiter import Limiter
        limiter = Limiter(app=app)
        limiter.storage.reset()

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
