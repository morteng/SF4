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
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL', 'sqlite:///:memory:')
    WTF_CSRF_ENABLED = True  # Ensure CSRF is enabled for testing
    SECRET_KEY = os.environ.get('SECRET_TEST_KEY', 'insecure-test-key')  # Change this in production

config_by_name = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    # Add other configurations as needed
}
