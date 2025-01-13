import sys
import subprocess
import logging
from pathlib import Path

# Configure paths before importing project modules
project_root = str(Path(__file__).resolve().parent.parent.parent)
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from scripts.path_config import configure_paths
from scripts.init_logging import configure_logging

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

def verify_coverage(threshold=80, critical_paths=True, admin_only=False, verify=False):
    """Enhanced coverage verification with critical path analysis
    Args:
        threshold (int): Minimum coverage percentage
        critical_paths (bool): Verify critical paths coverage
        admin_only (bool): Focus only on admin functionality
    """
    logger = configure_coverage_logging()
    
    try:
        # Ensure paths are configured for production
        if not configure_paths(production=True):
            logger.error("Failed to configure paths.")
            return False

        # Run coverage report with detailed output
        result = subprocess.run(
            ['coverage', 'report', f'--fail-under={threshold}', '--show-missing', '--skip-covered'],
            capture_output=True,
            text=True
        )
        
        if result.returncode != 0:
            logger.error(f"Coverage check failed: {result.stderr}")
            return False
            
        logger.info("Coverage check passed")
        return True
    except Exception as e:
        logger.error(f"Coverage verification failed: {str(e)}")
        return False

if __name__ == "__main__":
    if verify_coverage():
        exit(0)
    else:
        exit(1)
