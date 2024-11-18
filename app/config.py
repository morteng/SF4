import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'default_secret_key'
    DATABASE_URL = os.environ.get('DATABASE_URL') or 'sqlite:///site.db'

class DevelopmentConfig(Config):
    DEBUG = True

class TestingConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    WTF_CSRF_ENABLED = False  # Disable CSRF for testing

class ProductionConfig(Config):
    DEBUG = False

def get_config(config_name):
    if config_name == 'development':
        return DevelopmentConfig
    elif config_name == 'testing':
        return TestingConfig
    elif config_name == 'production':
        return ProductionConfig
    else:
        raise ValueError(f"Unknown configuration name: {config_name}")
