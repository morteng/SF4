import sys
import subprocess
import logging
from pathlib import Path

def configure_test_logging():
    """Configure logging for test verification"""
    logger = logging.getLogger('test_verification')
    if not logger.handlers:
        handler = logging.StreamHandler()
        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        logger.setLevel(logging.INFO)
    return logger

def configure_logger():
    """Configure the logger for test verification"""
    logger = logging.getLogger('test_verification')
    if not logger.handlers:
        handler = logging.StreamHandler()
        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        logger.setLevel(logging.INFO)
    return logger

def verify_tests():
    """Verify all tests pass with proper configuration"""
    # Configure logger at module level
    global logger
    logger = configure_logger()
    
    try:
        # Setup test environment first
        from scripts.setup_test_env import setup_test_paths
        if not setup_test_paths():
            raise RuntimeError("Failed to setup test paths")
        
        # Verify test environment
        from scripts.setup_test_env import setup_test_paths
        if not setup_test_paths():
            logger.error("Failed to setup test paths")
            return False
        
        # Run core test suites
        test_suites = [
            'tests/models/test_relationships.py',
            'tests/version_management/test_version.py',
            'tests/services/test_admin_creation.py',
            'tests/deployment/test_deployment_verification.py'
        ]
        
        # Run each test suite
        for suite in test_suites:
            logger.info(f"Running test suite: {suite}")
            result = subprocess.run(
                ['pytest', '-v', suite],
                capture_output=True,
                text=True
            )
            
            if result.returncode != 0:
                logger.error(f"Test suite failed: {suite}")
                logger.error(result.stderr)
                return False
                
        # Verify coverage
        from scripts.verify_test_coverage import verify_coverage
        if not verify_coverage():
            logger.error("Test coverage below required threshold")
            return False
            
        logger.info("All test suites passed and coverage requirements met")
        return True
    except Exception as e:
        logger.error(f"Test verification failed: {str(e)}")
        return False

if __name__ == "__main__":
    if verify_tests():
        exit(0)
    else:
        exit(1)
import sys
import subprocess
from pathlib import Path

def verify_tests():
    """Verify all tests pass with proper configuration"""
    try:
        # Add project root to Python path
        root_dir = Path(__file__).parent.parent
        sys.path.append(str(root_dir))
        
        # Run core test suites
        test_suites = [
            'tests/models/test_relationships.py',
            'tests/version_management/test_version.py'
        ]
        
        for suite in test_suites:
            result = subprocess.run(
                ['pytest', '-v', suite],
                capture_output=True,
                text=True
            )
            
            if result.returncode != 0:
                print(f"Test suite failed: {suite}")
                print(result.stdout)
                print(result.stderr)
                return False
                
        print("All test suites passed")
        return True
    except Exception as e:
        print(f"Test verification failed: {str(e)}")
        return False

if __name__ == "__main__":
    if verify_tests():
        exit(0)
    else:
        exit(1)
