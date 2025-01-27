import os
from flask import Config

class BaseConfig(Config):
    # Directory structure
    ROOT_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
    LOGS_PATH = os.path.join(ROOT_PATH, 'instance', 'logs')
    
    # Basic configuration
    SECRET_KEY = os.environ.get('SECRET_KEY', 'your-secret-key-here')
    DEBUG = False
    TESTING = False
    
    # Database configuration
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL', 'sqlite:///:memory:')
    
    def init_app(self, app):
        """Initialize Flask app with this configuration."""
        super().init_app(app)
        # Set root path
        app.root_path = self.ROOT_PATH
        # Add any additional initialization steps here
