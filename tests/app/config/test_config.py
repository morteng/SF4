import pytest
from app.configs import (
    BaseConfig,
    DevelopmentConfig,
    ProductionConfig,
    TestingConfig
)

def test_base_config():
    config = BaseConfig()
    assert config.DEBUG == 'False'  # Inherit from BaseConfig
    assert not config.TESTING
    assert 'SQLALCHEMY_TRACK_MODIFICATIONS' in config

def test_development_config():
    config = DevelopmentConfig()
    assert config.DEBUG is True
    assert not config.TESTING
    assert config.SQLALCHEMY_DATABASE_URI == 'sqlite:///dev.db'

def test_production_config():
    config = ProductionConfig()
    assert not config.DEBUG
    assert not config.TESTING
    assert config.SQLALCHEMY_DATABASE_URI == 'sqlite:///prod.db'

def test_testing_config():
    config = TestingConfig()
    assert not config.DEBUG
    assert config.TESTING
    assert config.SQLALCHEMY_DATABASE_URI == 'sqlite:///:memory:'
    assert config.WTF_CSRF_ENABLED is True
