import pytest
from scripts.verification.verify_deployment import verify_deployment
from scripts.verification.verify_db_connection import validate_db_connection
from scripts.startup.init_admin import initialize_admin_user
import os

@pytest.fixture
def setup_test_env(monkeypatch):
    """Setup test environment variables"""
    monkeypatch.setenv('SQLALCHEMY_DATABASE_URI', 'sqlite:///:memory:')
    monkeypatch.setenv('SECRET_KEY', 'TestSecretKey1234567890!@#$%^&*()')
    monkeypatch.setenv('ADMIN_USERNAME', 'testadmin')
    monkeypatch.setenv('ADMIN_EMAIL', 'test@example.com')
    monkeypatch.setenv('ADMIN_PASSWORD', 'TestPassword123!')
    monkeypatch.setenv('FLASK_ENV', 'testing')

def test_verify_deployment(setup_test_env):
    """Test full deployment verification"""
    assert verify_deployment() is True

def test_verify_db_connection(setup_test_env):
    """Test database connection verification"""
    assert validate_db_connection(os.getenv('SQLALCHEMY_DATABASE_URI')) is True

def test_initialize_admin_user(setup_test_env):
    """Test admin user initialization"""
    assert initialize_admin_user() is True
