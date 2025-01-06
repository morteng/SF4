import pytest
import sqlite3
from datetime import datetime
from scripts.version import (
    __version__,
    validate_db_connection,
    get_db_version,
    validate_version,
    parse_version,
    create_db_backup,
    validate_production_environment,
    validate_version_file,
    create_version_history,
    bump_version,
    update_version_file
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
    """Test successful database connection with logging verification"""
    # Create test database
    db_path = tmp_path / "test.db"
    with sqlite3.connect(db_path):
        pass
    
    # Test connection
    assert validate_db_connection(str(db_path)) is True
    
    # Verify logging output
    log_dir = Path('logs/version_management')
    log_file = log_dir / 'connection.log'
    assert log_file.exists()
    
    with log_file.open() as f:
        log_content = f.read()
        assert "Database connection successful" in log_content
        assert str(db_path) in log_content
        assert str(db_path) in log_content
@pytest.fixture(scope="module")
def test_db():
    """Create and initialize a test database"""
    db_path = "instance/test_stipend.db"
    if os.path.exists(db_path):
        os.remove(db_path)
        
    # Initialize database with schema
    from alembic import command
    from alembic.config import Config
    alembic_cfg = Config("migrations/alembic.ini")
    alembic_cfg.set_main_option("sqlalchemy.url", f"sqlite:///{db_path}")
    
    # Run migrations
    command.upgrade(alembic_cfg, "head")
    
    yield db_path
    
    # Cleanup
    if os.path.exists(db_path):
        os.remove(db_path)


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

def test_bump_version(tmp_path):
    """Test version bump functionality"""
    # Setup test version file
    version_file = tmp_path / "test_version.py"
    version_file.write_text('__version__ = "0.2.0"\n')
    
    # Test patch bump
    assert bump_version("patch", current_version="0.2.0") == "0.2.1"
    
    # Test minor bump
    assert bump_version("minor", current_version="0.2.0") == "0.3.0"
    
    # Test major bump
    assert bump_version("major", current_version="0.2.0") == "1.0.0"
    
    # Test invalid bump type
    with pytest.raises(ValueError):
        bump_version("invalid")
        
    # Test version validation after bump
    assert validate_version(bump_version("patch", current_version="0.2.0"))

def test_update_version_file(tmp_path):
    """Test updating version file"""
    # Create test version file
    test_file = tmp_path / "test_version.py"
    content = """__version__ = "1.2.3"
def validate_version():
    pass
def bump_version():
    pass
def create_db_backup():
    pass"""
    test_file.write_text(content)
    
    # Update version
    assert update_version_file("1.2.4", str(test_file)) is True
    
    # Verify update
    new_content = test_file.read_text()
    assert '__version__ = "1.2.4"' in new_content
    # Verify other content remains unchanged
    assert 'def validate_version()' in new_content
    assert 'def bump_version()' in new_content
    assert 'def create_db_backup()' in new_content

def test_create_db_backup(test_db_path, tmp_path):
    """Test database backup creation"""
    backup_path = str(tmp_path / "test_backup.db")
    backup_result = create_db_backup(test_db_path, backup_path)
    assert backup_result is True
    assert Path(backup_path).exists()

def test_validate_version_file(tmp_path: Path) -> None:
    """Test version file validation with various scenarios"""
    """Test version file validation"""
    # Create a valid version file
    valid_file = tmp_path / "version.py"
    content = """
__version__ = "1.2.3"
def validate_version(version: str) -> bool:
    pass
def bump_version(version_type="patch") -> str:
    pass
def create_db_backup(db_path: str) -> bool:
    pass
"""
    valid_file.write_text(content)
    assert validate_version_file(str(valid_file)) is True
    
    # Test with missing required functions
    invalid_file = tmp_path / "invalid.py"
    invalid_file.write_text("__version__ = '1.2.3'")
    assert validate_version_file(str(invalid_file)) is False
    
    # Test with missing file
    assert validate_version_file(str(tmp_path / "nonexistent.py")) is False
    
    # Test with invalid content
    invalid_file.write_text("invalid content")
    assert validate_version_file(str(invalid_file)) is False

def test_create_version_history(tmp_path):
    """Test version history creation"""
    version_file = tmp_path / "VERSION_HISTORY.md"
    create_version_history("1.2.3", history_path=str(version_file))
    
    assert version_file.exists()
    content = version_file.read_text()
    assert "## 1.2.3 - " in content
    assert "- Version bump" in content
    assert "- Fixed version management tests" in content
    assert "- Improved version history tracking" in content
    content = version_file.read_text()
    assert "1.2.3" in content
    assert datetime.now().strftime('%Y-%m-%d') in content

def test_validate_production_environment(monkeypatch, tmp_path):
    """Test production environment validation"""
    # Setup test environment
    monkeypatch.setenv('SQLALCHEMY_DATABASE_URI', 'sqlite:///test.db')  # Updated to match .env
    monkeypatch.setenv('SECRET_KEY', 'a' * 32)  # 32 character minimum
    monkeypatch.setenv('ADMIN_EMAIL', 'test@example.com')
    monkeypatch.setenv('ADMIN_PASSWORD', 'securepassword')
    monkeypatch.setenv('FLASK_ENV', 'production')
    monkeypatch.setenv('FLASK_DEBUG', '0')
    
    # Test validation
    assert validate_production_environment() is True
    
    # Test missing variables
    monkeypatch.delenv('SQLALCHEMY_DATABASE_URI')  # Updated to match .env
    assert validate_production_environment() is False
    
    # Test invalid types
    monkeypatch.setenv('SQLALCHEMY_DATABASE_URI', 'sqlite:///test.db')
    monkeypatch.setenv('SECRET_KEY', 12345)
    assert validate_production_environment() is False
    
    # Test SECRET_KEY length validation
    monkeypatch.setenv('SECRET_KEY', 'short')
    assert validate_production_environment() is False
    
    # Test FLASK_DEBUG validation
    monkeypatch.setenv('SECRET_KEY', 'a' * 32)
    monkeypatch.setenv('FLASK_DEBUG', 'invalid')
    assert validate_production_environment() is False

def test_validate_production_environment_complex(monkeypatch):
    """Test SECRET_KEY complexity requirements"""
    # Setup valid environment
    monkeypatch.setenv('SQLALCHEMY_DATABASE_URI', 'sqlite:///test.db')
    monkeypatch.setenv('SECRET_KEY', 'A'*64)  # Only uppercase
    monkeypatch.setenv('ADMIN_EMAIL', 'test@example.com')
    monkeypatch.setenv('ADMIN_PASSWORD', 'securepassword123!')
    monkeypatch.setenv('FLASK_ENV', 'production')
    monkeypatch.setenv('FLASK_DEBUG', '0')
    
    assert validate_production_environment() is False
    
    # Test with valid complex key
    monkeypatch.setenv('SECRET_KEY', 'Aa1!Bb2@Cc3#Dd4$'*4)
    assert validate_production_environment() is True

def test_validate_production_environment_lengths(monkeypatch):
    """Test minimum length requirements"""
    # Test SECRET_KEY too short
    monkeypatch.setenv('SECRET_KEY', 'short')
    assert validate_production_environment() is False
    
    # Test ADMIN_PASSWORD too short
    monkeypatch.setenv('ADMIN_PASSWORD', 'short')
    assert validate_production_environment() is False
