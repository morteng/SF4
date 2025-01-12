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
from scripts.init_logging import configure_logging

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
    log_file = log_dir / 'version_management.log'
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
    assert validate_version("1.2.3-alpha.1") is True
    assert validate_version("1.2.3+build.123.456") is True

    # Test invalid versions
    assert validate_version("1.2") is False
    assert validate_version("1.2.3-") is False
    assert validate_version("1.2.3+") is False
    assert validate_version("1.2.3-alpha.") is False
    assert validate_version("1.2.3+build.") is False
    assert validate_version("1.a.3") is False
    assert validate_version("1.2.a") is False
    assert validate_version("a.2.3") is False
    assert validate_version("-1.2.3") is False
    assert validate_version("1.-2.3") is False
    assert validate_version("1.2.-3") is False

def test_parse_version():
    """Test version parsing"""
    assert parse_version("1.2.3") == (1, 2, 3, None)
    assert parse_version("1.2.3-alpha") == (1, 2, 3, "alpha")
    
def test_create_db_backup(test_db):
    """Test database backup creation"""
    backup_path = create_db_backup(test_db)
    assert backup_path is not None
    assert os.path.exists(backup_path)
    
    # Cleanup
    os.remove(backup_path)

def test_validate_production_environment():
    """Test production environment validation"""
    # Set valid environment variables
    os.environ['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    os.environ['SECRET_KEY'] = 'TestSecretKey1234567890!@#$%^&*()_+-=[]{};:\'",.<>/?'
    os.environ['ADMIN_EMAIL'] = 'test@example.com'
    os.environ['ADMIN_PASSWORD'] = 'TestPassword123!'
    os.environ['FLASK_ENV'] = 'production'
    os.environ['FLASK_DEBUG'] = '0'
    
    assert validate_production_environment() is True
    
    # Test missing variables
    del os.environ['SQLALCHEMY_DATABASE_URI']
    assert validate_production_environment() is False
    os.environ['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    
    # Test invalid secret key length
    os.environ['SECRET_KEY'] = 'short'
    assert validate_production_environment() is False
    os.environ['SECRET_KEY'] = 'TestSecretKey1234567890!@#$%^&*()_+-=[]{};:\'",.<>/?'
    
    # Test invalid admin password length
    os.environ['ADMIN_PASSWORD'] = 'short'
    assert validate_production_environment() is False
    os.environ['ADMIN_PASSWORD'] = 'TestPassword123!'
    
    # Test invalid secret key complexity
    os.environ['SECRET_KEY'] = 'lowercaseonly123'
    assert validate_production_environment() is False
    os.environ['SECRET_KEY'] = 'TestSecretKey1234567890!@#$%^&*()_+-=[]{};:\'",.<>/?'
    
    os.environ['SECRET_KEY'] = 'UPPERCASEONLY123'
    assert validate_production_environment() is False
    os.environ['SECRET_KEY'] = 'TestSecretKey1234567890!@#$%^&*()_+-=[]{};:\'",.<>/?'
    
    os.environ['SECRET_KEY'] = 'NoSpecialChars123'
    assert validate_production_environment() is False
    os.environ['SECRET_KEY'] = 'TestSecretKey1234567890!@#$%^&*()_+-=[]{};:\'",.<>/?'
    
    os.environ['SECRET_KEY'] = 'NoNumbersHere'
    assert validate_production_environment() is False
    os.environ['SECRET_KEY'] = 'TestSecretKey1234567890!@#$%^&*()_+-=[]{};:\'",.<>/?'

def test_validate_version_file():
    """Test version file validation"""
    assert validate_version_file() is True
    
    # Create a dummy file without required content
    dummy_file = Path('dummy_version.py')
    dummy_file.write_text("print('hello')")
    assert validate_version_file(str(dummy_file)) is False
    dummy_file.unlink()

def test_create_version_history():
    """Test version history creation"""
    new_version = "1.2.4"
    create_version_history(new_version)
    history_file = Path('VERSION_HISTORY.md')
    assert history_file.exists()
    with history_file.open() as f:
        content = f.read()
        assert f"## {new_version}" in content
    history_file.unlink()

def test_bump_version():
    """Test version bumping"""
    assert bump_version("patch", "1.2.3") == "1.2.4"
    assert bump_version("minor", "1.2.3") == "1.3.0"
    assert bump_version("major", "1.2.3") == "2.0.0"
    
    with pytest.raises(ValueError):
        bump_version("invalid", "1.2.3")

def test_update_version_file():
    """Test version file update"""
    new_version = "1.2.5"
    assert update_version_file(new_version) is True
    from scripts.version import __version__
    assert __version__ == new_version
    
    # Test with a specific file path
    test_file = Path('test_version.py')
    test_file.write_text('__version__ = "1.2.3"')
    assert update_version_file(new_version, str(test_file)) is True
    with test_file.open() as f:
        content = f.read()
        assert f'__version__ = "{new_version}"' in content
    test_file.unlink()
