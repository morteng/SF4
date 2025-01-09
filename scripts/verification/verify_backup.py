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
    """Enhanced backup verification with schema validation and integrity checks"""
    try:
        if not Path(backup_path).exists():
            logger.error(f"Backup file missing: {backup_path}")
            return False
            
        # Verify file size
        file_size = Path(backup_path).stat().st_size
        if file_size < 1024:  # 1KB minimum
            logger.error("Backup file too small")
            return False
            
        # Verify schema
        conn = sqlite3.connect(backup_path)
        cursor = conn.cursor()
        
        # Check required tables
        required_tables = ['stipend', 'tag', 'organization', 'user']
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        existing_tables = [row[0] for row in cursor.fetchall()]
        
        missing_tables = [table for table in required_tables if table not in existing_tables]
        if missing_tables:
            logger.error(f"Missing required tables: {', '.join(missing_tables)}")
            return False
            
        # Verify foreign keys
        cursor.execute("PRAGMA foreign_key_check")
        errors = cursor.fetchall()
        if errors:
            logger.error(f"Foreign key errors: {errors}")
            return False
            
        # Verify data integrity
        cursor.execute("PRAGMA integrity_check")
        result = cursor.fetchone()[0]
        if result != 'ok':
            logger.error(f"Integrity check failed: {result}")
            return False
            
        logger.info("Backup verification passed")
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
