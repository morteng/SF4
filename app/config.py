import os

class DefaultConfig:
    """Default configuration for the application."""
    
    # General Config
    SECRET_KEY = os.environ.get('SECRET_KEY', 'your_secret_key_here')
    DEBUG = False
    TESTING = False
    
    # Database Config
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL', 'sqlite:///instance/site.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False

class DevelopmentConfig(DefaultConfig):
    """Development configuration."""
    
    DEBUG = True

class TestingConfig(DefaultConfig):
    """Testing configuration."""
    
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    WTF_CSRF_ENABLED = False  # Disable CSRF for testing

class ProductionConfig(DefaultConfig):
    """Production configuration."""
    
    DEBUG = False
    TESTING = False
