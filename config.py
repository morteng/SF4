import os
from dotenv import load_dotenv

load_dotenv()

print(f"Loaded environment variables: {os.environ}")

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY', 'default_secret_key')
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL', 'sqlite:///site.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False

class DefaultConfig(Config):
    DEBUG = False
    TESTING = False

class DevelopmentConfig(Config):
    DEBUG = True

class TestingConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    WTF_CSRF_ENABLED = False  # Disable CSRF for testing

class ProductionConfig(Config):
    DEBUG = False
    TESTING = False

def get_config(config_name):
    config_map = {
        'default': DefaultConfig,
        'development': DevelopmentConfig,
        'testing': TestingConfig,
        'production': ProductionConfig
    }
    config_class = config_map.get(config_name)
    if not config_class:
        raise ValueError(f"Unknown configuration name: {config_name}")
    return config_class

print(f"Configuration map: {config_map}")
