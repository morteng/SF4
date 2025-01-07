import sys
import subprocess
import logging
from pathlib import Path

def configure_coverage_logging():
    """Configure logging for coverage verification"""
    logger = logging.getLogger('coverage')
    if not logger.handlers:
        handler = logging.StreamHandler()
        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        logger.setLevel(logging.INFO)
    return logger

def verify_coverage():
    """Verify test coverage meets requirements"""
    logger = configure_coverage_logging()
    
    try:
        # Add project root to Python path
        project_root = str(Path(__file__).parent.parent)
        if project_root not in sys.path:
            sys.path.insert(0, project_root)
        
        # Run coverage report
        result = subprocess.run(
            ['coverage', 'report', '--fail-under=80'],
            capture_output=True,
            text=True
        )
        
        if result.returncode != 0:
            logger.error(f"Coverage verification failed: {result.stderr}")
            return False
            
        logger.info("Coverage verification passed")
        logger.info(result.stdout)
        return True
        
    except Exception as e:
        logger.error(f"Coverage verification failed: {str(e)}")
        return False

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    if verify_coverage():
        exit(0)
    else:
        exit(1)
