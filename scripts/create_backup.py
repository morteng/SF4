import os
import sys
import sqlite3
from datetime import datetime
from pathlib import Path

def create_db_backup(source_db: str, backup_path: str = None, timestamped: bool = False) -> bool:
    """Create a backup of the database with optional timestamp"""
    try:
        # Set backup path with timestamp if requested
        if timestamped:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            backup_path = f'backups/stipend_{timestamp}.db'
        elif backup_path is None:
            backup_path = 'backups/stipend_latest.db'
            
        # Ensure backup directory exists
        os.makedirs(os.path.dirname(backup_path), exist_ok=True)
        
        # Connect to source database and create backup
        conn = sqlite3.connect(source_db)
        with conn:
            conn.execute(f"VACUUM INTO '{backup_path}'")
            
        # Verify backup was created
        if not Path(backup_path).exists():
            raise RuntimeError("Backup file was not created")
            
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
