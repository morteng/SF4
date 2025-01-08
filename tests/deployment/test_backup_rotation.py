import os
from pathlib import Path
import pytest
from scripts.backup_rotation import rotate_backups

@pytest.fixture
def setup_backups(tmp_path):
    backup_dir = tmp_path / "backups"
    backup_dir.mkdir()
    
    # Create test backup files
    for i in range(10):
        (backup_dir / f"backup_{i}.db").touch()
    
    return backup_dir

def test_backup_rotation(setup_backups):
    # Test rotation keeps only 5 backups
    rotate_backups(max_backups=5)
    
    backups = sorted(setup_backups.glob("*.db"))
    assert len(backups) == 5
    assert all(f"backup_{i}.db" in backups[-1].name for i in range(5,10))

def test_backup_rotation_empty_dir(tmp_path):
    # Test rotation with empty directory
    backup_dir = tmp_path / "empty_backups"
    backup_dir.mkdir()
    
    rotate_backups(max_backups=5)
    assert len(list(backup_dir.glob("*.db"))) == 0

def test_backup_rotation_insufficient_backups(setup_backups):
    # Test rotation when fewer than max backups exist
    rotate_backups(max_backups=15)
    backups = sorted(setup_backups.glob("*.db"))
    assert len(backups) == 10
