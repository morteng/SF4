import pytest
from scripts.verification.verify_deployment import verify_deployment
from scripts.verification.verify_db_connection import verify_db_connection
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

def test_final_verification(setup_test_env):
    """Test final deployment verification"""
    assert verify_deployment() is True
    assert verify_db_connection() is True
    assert initialize_admin_user() is True
