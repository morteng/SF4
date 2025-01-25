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

def verify_coverage(threshold=85, critical_paths=True, verify=False, focus_areas=['core_services', 'stipend_service']):
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

        # Run focused coverage report
        coverage_cmd = ['coverage', 'run', '-m', 'pytest', 
                       f'--cov=app.services.base_service',
                       f'--cov-report=term-missing:skip-covered',
                       f'--cov-fail-under={threshold}']
        
        if focus_areas and 'core_services' in focus_areas:
            coverage_cmd.extend(['tests/test_base_service.py'])
        if focus_areas and 'stipend_service' in focus_areas:
            coverage_cmd.extend(['tests/test_stipend_service.py'])
            
        result = subprocess.run(
            coverage_cmd,
            capture_output=True,
            text=True
        )

        # Parse coverage percentage from output
        try:
            coverage_line = [line for line in result.stdout.split('\n') 
                           if 'TOTAL' in line][0]
            parts = coverage_line.split()
            coverage_percent = float(parts[-4].replace('%', ''))  # Get coverage percentage from correct column
            
            if coverage_percent < threshold:
                logger.error(f"Coverage {coverage_percent}% below {threshold}% minimum")
                return False
                
        except (IndexError, ValueError) as e:
            logger.error(f"Failed to parse coverage results: {str(e)}")
            return False

        if result.returncode != 0:
            logger.error(f"Coverage check failed: {result.stderr}")
            return False
            
        logger.info(f"Coverage check passed at {coverage_percent}%")
        return True
    except Exception as e:
        logger.error(f"Coverage verification failed: {str(e)}")
        return False

if __name__ == "__main__":
    if verify_coverage():
        exit(0)
    else:
        exit(1)
