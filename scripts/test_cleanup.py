import os
import shutil
import logging
from pathlib import Path

logger = logging.getLogger(__name__)

def cleanup_test_environment():
    """Clean up test artifacts and environment"""
    try:
        # Remove test databases
        for db_file in Path('instance').glob('*.db'):
            if db_file.exists():
                db_file.unlink()
                logger.info(f"Removed test database: {db_file}")
                
        # Remove isolated test directories
        if os.getenv('TEST_ISOLATED') == 'true':
            test_dir = Path(os.getenv('TEST_DIR', 'tests/temp_env'))
            if test_dir.exists():
                shutil.rmtree(test_dir)
                logger.info(f"Removed isolated test directory: {test_dir}")
            
        # Remove coverage files
        for cov_file in Path('.').glob('.coverage*'):
            cov_file.unlink()
            logger.info(f"Removed coverage file: {cov_file}")
            
        # Remove test logs
        test_logs = Path('logs/tests.log')
        if test_logs.exists():
            test_logs.unlink()
            logger.info("Removed test logs")
            
        # Remove HTML coverage report
        html_cov = Path('htmlcov')
        if html_cov.exists():
            shutil.rmtree(html_cov)
            logger.info("Removed HTML coverage report")
            
        return True
    except Exception as e:
        logger.error(f"Test cleanup failed: {str(e)}")
        return False

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    if cleanup_test_environment():
        print("Test cleanup completed")
        exit(0)
    else:
        print("Test cleanup failed")
        exit(1)
