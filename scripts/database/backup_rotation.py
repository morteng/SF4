import os
import sys
import shutil
from datetime import datetime
from pathlib import Path
import logging

# Add project root to Python path
root_dir = Path(__file__).parent.parent.parent
sys.path.append(str(root_dir))

logger = logging.getLogger(__name__)

def rotate_backups(max_backups=5):
    """Rotate database backups keeping only max_backups"""
    try:
        backup_dir = Path('backups')
        if not backup_dir.exists():
            backup_dir.mkdir()
            
        backups = sorted(backup_dir.glob('*.db'), key=os.path.getmtime)
        while len(backups) > max_backups:
            oldest = backups.pop(0)
            logger.info(f"Removing old backup: {oldest}")
            oldest.unlink()
        return True
    except Exception as e:
        logger.error(f"Backup rotation failed: {str(e)}")
        return False

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    if rotate_backups():
        print("Backup rotation completed")
        exit(0)
    else:
        print("Backup rotation failed")
        exit(1)
