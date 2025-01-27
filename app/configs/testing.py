from .base import BaseConfig

class TestConfig(BaseConfig):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    WTF_CSRF_ENABLED = True
    WTF_CSRF_SECRET_KEY = 'test-secret-key'
    
    # Configure SQLite for testing
    SQLALCHEMY_ENGINE_OPTIONS = {
        'poolclass': 'StaticPool',
        'connect_args': {'check_same_thread': False}
    }
