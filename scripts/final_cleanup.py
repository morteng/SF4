import os
import shutil
import logging
from pathlib import Path

def configure_logger():
    """Configure logger for cleanup scripts"""
    logger = logging.getLogger(__name__)
    if not logger.handlers:
        handler = logging.StreamHandler()
        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        logger.setLevel(logging.INFO)
    return logger

def cleanup():
    """Perform final cleanup tasks before deployment"""
    logger = configure_logger()
    
    # Define directories to clean
    temp_dirs = [
        'tmp',
        'build',
        'dist',
        '__pycache__',
        '.pytest_cache',
        'htmlcov',
        'migrations/versions/*.pyc',  # Clean compiled migration files
        'instance/*.db-wal',          # Clean SQLite write-ahead logs
        'instance/*.db-shm',          # Clean SQLite shared memory files
        'instance/*.db-journal',      # Add SQLite journal files
        'logs/*.log.*'                # Add rotated log files
    ]
    
    try:
        # Remove temporary directories
        for temp_dir in temp_dirs:
            path = Path(temp_dir)
            if path.exists():
                try:
                    if path.is_dir():
                        shutil.rmtree(path)
                    else:
                        path.unlink()
                    logger.info(f"Removed: {temp_dir}")
                except Exception as e:
                    logger.warning(f"Could not remove {temp_dir}: {str(e)}")

        # Remove .pyc files
        pyc_count = 0
        for pyc_file in Path('.').rglob('*.pyc'):
            try:
                pyc_file.unlink()
                pyc_count += 1
            except Exception as e:
                logger.warning(f"Failed to remove {pyc_file}: {str(e)}")
        logger.info(f"Removed {pyc_count} .pyc files")

        # Remove empty directories
        empty_count = 0
        for root, dirs, files in os.walk('.', topdown=False):
            for dir in dirs:
                dir_path = Path(root) / dir
                try:
                    if not any(dir_path.iterdir()):
                        dir_path.rmdir()
                        empty_count += 1
                except Exception as e:
                    logger.warning(f"Failed to remove {dir_path}: {str(e)}")
        logger.info(f"Removed {empty_count} empty directories")

        logger.info("Cleanup completed successfully")
        return True
        
    except Exception as e:
        logger.error(f"Cleanup failed: {str(e)}")
        return False

if __name__ == '__main__':
    cleanup()
