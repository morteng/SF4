from dotenv import load_dotenv
import os

load_dotenv()

class BaseConfig:
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    JSONIFY_PRETTYPRINT_REGULAR = True
    BUNDLE_ERRORS = True
    MAX_CONTENT_LENGTH = 25 * 1024 * 1024  # 25MB
    DEBUG = os.getenv('DEBUG', 'False').lower() in ('true', 'on', '1')
    SECRET_KEY = os.getenv('SECRET_KEY', 'your-secret-key-here')
    
    def init_app(self, app):
        """Base configuration initialization"""
        app.jinja_env.trim_blocks = True
        app.jinja_env.lstrip_blocks = True

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
