import os
import sqlite3
from pathlib import Path
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def verify_backup_integrity(backup_path):
    """Verify backup file integrity"""
    try:
        if not Path(backup_path).exists():
            logger.error(f"Backup file not found: {backup_path}")
            return False
            
        # Connect to backup database
        conn = sqlite3.connect(backup_path)
        cursor = conn.cursor()
        
        # Check schema version
        cursor.execute("PRAGMA user_version")
        version = cursor.fetchone()[0]
        if version < 1:
            logger.error("Invalid schema version in backup")
            return False
            
        # Verify core tables exist
        required_tables = ['stipend', 'tag', 'organization', 'user']
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        existing_tables = [row[0] for row in cursor.fetchall()]
        
        missing_tables = [table for table in required_tables if table not in existing_tables]
        if missing_tables:
            logger.error(f"Missing tables in backup: {', '.join(missing_tables)}")
            return False
            
        # Verify foreign key constraints
        cursor.execute("PRAGMA foreign_key_check")
        errors = cursor.fetchall()
        if errors:
            logger.error(f"Foreign key constraint violations found: {errors}")
            return False
            
        # Verify data integrity
        cursor.execute("PRAGMA integrity_check")
        integrity_check = cursor.fetchone()[0]
        if integrity_check != 'ok':
            logger.error(f"Database integrity check failed: {integrity_check}")
            return False
            
        logger.info(f"Backup verification passed: {backup_path}")
        return True
        
    except Exception as e:
        logger.error(f"Backup verification failed: {str(e)}")
        return False
    finally:
        if 'conn' in locals():
            conn.close()

if __name__ == "__main__":
    # Get latest backup
    backup_files = sorted(Path('backups').glob('stipend_*.db'), reverse=True)
    if not backup_files:
        print("No backups found")
        exit(1)
        
    if verify_backup_integrity(backup_files[0]):
        print("Backup verification passed")
        exit(0)
    else:
        print("Backup verification failed")
        exit(1)
