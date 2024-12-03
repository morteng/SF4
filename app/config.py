import os

class Config:
    DEBUG = False
    TESTING = False
    project_dir = os.path.dirname(os.path.abspath(__file__))
    database_file = os.path.join(project_dir, 'instance', 'site.db')
    SQLALCHEMY_DATABASE_URI = f"sqlite:///{database_file}"
    WTF_CSRF_ENABLED = True
    SECRET_KEY = os.environ.get('SECRET_KEY', 'insecure-key-for-testing')  # Change this in production

class DevelopmentConfig(Config):
    DEBUG = True
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
    SECRET_KEY = os.environ.get('SECRET_PROD_KEY', 'insecure-prod-key')  

config_by_name = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig  
}
