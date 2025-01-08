import os
import logging
from pathlib import Path

def configure_logger():
    """Configure logging for test cleanup verification"""
    logger = logging.getLogger('test_cleanup')
    if not logger.handlers:
        handler = logging.StreamHandler()
        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        logger.setLevel(logging.INFO)
    return logger

def verify_test_cleanup():
    """Verify test environment cleanup"""
    logger = configure_logger()
    
    try:
        # Check for leftover test files
        test_files = list(Path('tests').rglob('*.tmp'))
        if test_files:
            logger.error(f"Found leftover test files: {len(test_files)}")
            return False
            
        # Check test database cleanup
        test_db = Path('instance/test.db')
        if test_db.exists():
            logger.error("Test database not cleaned up")
            return False
            
        # Check test logs cleanup
        test_logs = list(Path('logs').glob('test_*.log'))
        if test_logs:
            logger.error(f"Found leftover test logs: {len(test_logs)}")
            return False
            
        logger.info("Test environment cleanup verified")
        return True
        
    except Exception as e:
        logger.error(f"Test cleanup verification failed: {str(e)}")
        return False

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    if verify_test_cleanup():
        print("Test cleanup verification passed")
        exit(0)
    else:
        print("Test cleanup verification failed")
        exit(1)
