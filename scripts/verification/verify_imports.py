import sys
import os
import logging
from pathlib import Path

def configure_logger():
    """Configure logger for import verification"""
    logger = logging.getLogger(__name__)
    if not logger.handlers:
        handler = logging.StreamHandler()
        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        logger.setLevel(logging.INFO)
    return logger

def verify_project_paths():
    """Verify all project paths are correctly configured"""
    logger = configure_logger()
    
    try:
        # Get project root dynamically
        project_root = str(Path(__file__).resolve().parent.parent.parent)
        
        # Expected paths relative to project root
        expected_paths = [
            project_root,
            str(Path(project_root) / 'app'),
            str(Path(project_root) / 'scripts'),
            str(Path(project_root) / 'tests'),
            str(Path(project_root) / '.venv' / 'Lib' / 'site-packages'),
            str(Path(project_root) / 'automation')
        ]
        
        # Verify all paths exist and are accessible
        for path in expected_paths:
            if not Path(path).exists():
                logger.error(f"Path does not exist: {path}")
                return False
            if not os.access(path, os.R_OK):
                logger.error(f"Path not readable: {path}")
                return False
        
        # Check each path exists and is in sys.path
        missing_paths = []
        for path in expected_paths:
            if not Path(path).exists():
                missing_paths.append(f"Path does not exist: {path}")
            if path not in sys.path:
                missing_paths.append(f"Path not in sys.path: {path}")
                
        if missing_paths:
            logger.error("Path configuration issues found:")
            for msg in missing_paths:
                logger.error(msg)
            return False
            
        logger.info("All project paths verified successfully")
        return True
        
    except Exception as e:
        logger.error(f"Path verification failed: {str(e)}")
        return False

if __name__ == "__main__":
    import argparse
    logging.basicConfig(level=logging.INFO)
    
    parser = argparse.ArgumentParser()
    parser.add_argument('--full', action='store_true', help='Run full verification')
    parser.add_argument('--validate-paths', action='store_true',
                       help='Validate all project paths')
    args = parser.parse_args()
    
    if verify_project_paths():
        print("Path verification passed")
        exit(0)
    else:
        print("Path verification failed")
        exit(1)
