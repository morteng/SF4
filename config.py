import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY', 'default_secret_key')
    DATABASE_URL = os.environ.get('DATABASE_URL', 'sqlite:///site.db')
    SQLALCHEMY_DATABASE_URI = DATABASE_URL
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    WTF_CSRF_ENABLED = True

class TestingConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    WTF_CSRF_ENABLED = False
