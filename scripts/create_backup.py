import os
import sys
import sqlite3
from datetime import datetime
from pathlib import Path

def create_db_backup(source_db: str, backup_path: str) -> bool:
    """Create a timestamped backup of the database"""
    try:
        # Ensure backup directory exists
        os.makedirs(os.path.dirname(backup_path), exist_ok=True)
        
        # Connect to source database and create backup
        conn = sqlite3.connect(source_db)
        with conn:
            conn.execute(f"VACUUM INTO '{backup_path}'")
        print(f"Database backup created: {source_db} -> {backup_path}")
        return True
    except sqlite3.Error as e:
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
