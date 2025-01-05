import pytest
import sqlite3
from scripts.version import (
    validate_db_connection,
    get_db_version,
    validate_version,
    parse_version,
    create_db_backup,
    validate_production_environment
)
import os
from pathlib import Path

@pytest.fixture
def test_db_path(tmp_path):
    db_path = tmp_path / "test.db"
    # Create a test database
    with sqlite3.connect(db_path) as conn:
        conn.execute("CREATE TABLE test (id INTEGER PRIMARY KEY)")
    return str(db_path)

def test_validate_db_connection_success(tmp_path):
    db_path = tmp_path / "test.db"
    with sqlite3.connect(db_path):
        pass
    assert validate_db_connection(str(db_path)) is True

def test_validate_db_connection_failure():
    assert validate_db_connection("/invalid/path/test.db") is False

def test_get_db_version(tmp_path):
    db_path = tmp_path / "test.db"
    with sqlite3.connect(db_path) as conn:
        conn.execute("PRAGMA user_version=123")
    assert get_db_version(str(db_path)) == "123"

def test_validate_version():
    """Test version validation"""
    # Test valid versions
    assert validate_version("1.2.3") is True
    assert validate_version("1.2.3-alpha") is True
    assert validate_version("1.2.3+build.123") is True
    assert validate_version("1.2.3-alpha.1+build.123") is True
    assert validate_version("1.2.3+build.123.456") is True
    
    # Test invalid versions
    assert validate_version("invalid") is False
    assert validate_version("1.2") is False
    assert validate_version("1.2.3+") is False
    assert validate_version("1.2.3-") is False

def test_create_db_backup(test_db_path):
    """Test database backup creation"""
    backup_result = create_db_backup(test_db_path)
    assert backup_result is True
    assert len(list(Path(test_db_path).parent.glob("*.backup_*.db"))) == 1

def test_validate_version_file():
    """Test version file validation"""
    assert validate_version_file() is True

def test_validate_production_environment(monkeypatch):
    """Test production environment validation"""
    # Test missing environment variables
    assert validate_production_environment() is False
    
    # Test with all required variables
    monkeypatch.setenv('DATABASE_URL', 'sqlite:///test.db')
    monkeypatch.setenv('SECRET_KEY', 'test_key')
    monkeypatch.setenv('ADMIN_EMAIL', 'test@example.com')
    assert validate_production_environment() is True
