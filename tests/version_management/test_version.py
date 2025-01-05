import pytest
import sqlite3
from scripts.version import (
    validate_db_connection,
    get_db_version,
    validate_version,
    parse_version,
    create_db_backup,
    validate_production_environment,
    validate_version_file
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

def test_validate_version_file(tmp_path):
    """Test version file validation"""
    # Test with valid version file
    version_file = tmp_path / "version.txt"
    version_file.write_text("1.2.3")
    assert validate_version_file(str(version_file)) is True
    
    # Test with invalid version file
    invalid_file = tmp_path / "invalid.txt"
    invalid_file.write_text("invalid")
    assert validate_version_file(str(invalid_file)) is False
    
    # Test with missing file
    assert validate_version_file(str(tmp_path / "nonexistent.txt")) is False
    
    # Test with missing file
    assert validate_version_file(str(tmp_path / "nonexistent.txt")) is False
    
    # Test with invalid version file
    invalid_file = tmp_path / "invalid.txt"
    invalid_file.write_text("invalid")
    assert validate_version_file(str(invalid_file)) is False
    
    # Test with missing file
    assert validate_version_file(str(tmp_path / "nonexistent.txt")) is False

def test_validate_production_environment(monkeypatch):
    """Test production environment validation"""
    # Test missing environment variables
    monkeypatch.delenv('DATABASE_URL', raising=False)
    monkeypatch.delenv('SECRET_KEY', raising=False)
    monkeypatch.delenv('ADMIN_EMAIL', raising=False)
    assert validate_production_environment() is False
    
    # Test with all required variables
    monkeypatch.setenv('DATABASE_URL', 'sqlite:///test.db')
    monkeypatch.setenv('SECRET_KEY', 'test_key')
    monkeypatch.setenv('ADMIN_EMAIL', 'test@example.com')
    assert validate_production_environment() is True
