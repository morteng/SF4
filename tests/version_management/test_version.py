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
    assert validate_version("1.2.3-alpha.1