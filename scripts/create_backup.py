import os
import sys
import sqlite3
from datetime import datetime
from pathlib import Path

def create_db_backup(source_db: str, backup_path: str = None, timestamped: bool = False, verify: bool = False) -> bool:
    """Create a backup of the database with enhanced validation"""
    try:
        # Validate source database exists
        if not Path(source_db).exists():
            logger.error(f"Source database not found: {source_db}")
            return False
            
        # Verify git state first
        from scripts.verify_git_state import verify_git_state
        if not verify_git_state():
            logger.error("Cannot create backup with uncommitted changes")
            return False
            
        # Set backup path with timestamp if requested
        if timestamped:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            backup_path = f'backups/stipend_{timestamp}.db'
        elif backup_path is None:
            backup_path = 'backups/stipend_latest.db'
            
        # Ensure backup directory exists
        backup_dir = Path(backup_path).parent
        backup_dir.mkdir(parents=True, exist_ok=True)
        
        # Connect to source database and create backup
        conn = sqlite3.connect(source_db)
        with conn:
            # Enable foreign key constraints
            conn.execute("PRAGMA foreign_keys = ON")
            # Create backup using VACUUM INTO
            conn.execute(f"VACUUM INTO '{backup_path}'")
            
        # Verify backup was created and is valid
        if not Path(backup_path).exists():
            raise RuntimeError("Backup file was not created")
            
        # Verify backup integrity
        try:
            backup_conn = sqlite3.connect(backup_path)
            backup_conn.execute("PRAGMA integrity_check")
            backup_conn.close()
        except sqlite3.Error as e:
            print(f"Backup integrity check failed: {str(e)}")
            return False
            
        print(f"Database backup created: {source_db} -> {backup_path}")
        return True
    except Exception as e:
        print(f"Database backup failed: {str(e)}")
        return False

if __name__ == "__main__":
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    backup_file = f'backups/stipend_{timestamp}.db'
    if create_db_backup('instance/stipend.db', backup_file):
        print(f"Created backup: {backup_file}")
        exit(0)
    else:
        print("Backup failed")
        exit(1)
