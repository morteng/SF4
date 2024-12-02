import os

class Config:
    DEBUG = False
    TESTING = False
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL', 'your_default_database_uri')
    WTF_CSRF_ENABLED = True
    SECRET_KEY = os.environ.get('SECRET_KEY', 'insecure-key-for-testing')  # Change this in production

class DevelopmentConfig(Config):
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL', 'your_dev_database_uri')
    SECRET_KEY = os.environ.get('SECRET_DEV_KEY', 'insecure-dev-key')  # Change this in production

class TestingConfig(Config):
    DEBUG = False
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    WTF_CSRF_ENABLED = False  # Disable CSRF for testing
    SQLALCHEMY_ECHO = False  
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECRET_KEY = os.environ.get('SECRET_TEST_KEY', 'insecure-test-key')  

class ProductionConfig(Config):
    DEBUG = False
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL', 'your_prod_database_uri')
    SECRET_KEY = os.environ.get('SECRET_PROD_KEY', 'insecure-prod-key')  

config_by_name = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig  
}
