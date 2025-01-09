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
        # Check for leftover files
        cleanup_checks = [
            (list(Path('tests').rglob('*.tmp')), "test files"),
            ([Path('instance/test.db')], "test database"),
            (list(Path('logs').glob('test_*.log')), "test logs")
        ]
        
        for files, description in cleanup_checks:
            if any(f.exists() for f in files):
                logger.error(f"Found leftover {description}")
                return False
                
        # Verify environment reset
        if os.getenv('TESTING') == 'true':
            logger.error("Testing environment not reset")
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
