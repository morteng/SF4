import pytest
from app.config import DevelopmentConfig, TestingConfig, ProductionConfig

def test_development_config():
    config = DevelopmentConfig()
    assert config.DEBUG is True
    assert config.TESTING is False
    assert config.SQLALCHEMY_DATABASE_URI.startswith('sqlite:///')

def test_testing_config():
    config = TestingConfig()
    assert config.DEBUG is False
    assert config.TESTING is True
    assert config.SQLALCHEMY_DATABASE_URI == 'sqlite:///:memory:'
    assert config.WTF_CSRF_ENABLED is True  # Changed from False to True

def test_production_config():
    config = ProductionConfig()
    assert config.DEBUG is False
    assert config.TESTING is False
    assert config.SQLALCHEMY_DATABASE_URI.startswith('sqlite:///')
