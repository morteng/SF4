import os
import shutil
from pathlib import Path

def cleanup():
    """Perform final cleanup tasks before deployment"""
    logger = logging.getLogger(__name__)
    
    # Define directories to clean
    temp_dirs = [
        'tmp',
        'build',
        'dist',
        '__pycache__',
        '.pytest_cache',
        '.coverage',
        'htmlcov'
    ]
    
    try:
        # Remove temporary directories
        for temp_dir in temp_dirs:
            if os.path.exists(temp_dir):
                shutil.rmtree(temp_dir)
                logger.info(f"Removed directory: {temp_dir}")

        # Remove .pyc files
        pyc_count = 0
        for pyc_file in Path('.').rglob('*.pyc'):
            try:
                pyc_file.unlink()
                pyc_count += 1
            except Exception as e:
                logger.error(f"Failed to remove {pyc_file}: {str(e)}")
        logger.info(f"Removed {pyc_count} .pyc files")

        # Remove empty directories
        empty_count = 0
        for root, dirs, files in os.walk('.', topdown=False):
            for dir in dirs:
                dir_path = os.path.join(root, dir)
                try:
                    if not os.listdir(dir_path):
                        os.rmdir(dir_path)
                        empty_count += 1
                except OSError as e:
                    logger.error(f"Failed to remove {dir_path}: {str(e)}")
        logger.info(f"Removed {empty_count} empty directories")

        # Verify cleanup
        from scripts.verify_test_cleanup import verify_test_cleanup
        if not verify_test_cleanup():
            raise Exception("Cleanup verification failed")

        logger.info("Cleanup completed successfully")
        return True
        
    except Exception as e:
        logger.error(f"Cleanup failed: {str(e)}")
        return False

if __name__ == '__main__':
    cleanup()
