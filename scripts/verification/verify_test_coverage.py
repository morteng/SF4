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

def verify_coverage(threshold=85, critical_paths=True, admin_only=False):
    """Enhanced coverage verification with critical path analysis
    Args:
        threshold (int): Minimum coverage percentage
        critical_paths (bool): Verify critical paths coverage
        admin_only (bool): Focus only on admin functionality
    """
    logger = configure_coverage_logging()
    
    try:
        # Configure paths first
        from scripts.path_config import configure_paths
        if not configure_paths():
            raise RuntimeError("Failed to configure paths")
            
        # Verify imports
        import app
        import tests
    except ImportError as e:
        logger.error(f"Import error: {str(e)}")
        logger.error(f"Current sys.path: {sys.path}")
        return False
    
    try:
        # Configure paths first
        from scripts.path_config import configure_paths
        if not configure_paths():
            raise RuntimeError("Failed to configure paths")
            
        # Add project root to Python path
        project_root = str(Path(__file__).parent.parent)
        if project_root not in sys.path:
            sys.path.insert(0, project_root)
            
        # Add app directory explicitly
        app_dir = str(Path(project_root) / 'app')
        if app_dir not in sys.path:
            sys.path.insert(0, app_dir)
            
        # Verify imports
        try:
            import app
            import tests
        except ImportError as e:
            logger.error(f"Import error: {str(e)}")
            logger.error(f"Current sys.path: {sys.path}")
            return False
        
        # Run coverage report with detailed output
        result = subprocess.run(
            ['coverage', 'report', f'--fail-under={threshold}', '--show-missing', '--skip-covered'],
            capture_output=True,
            text=True
        )
        
        if result.returncode != 0:
            logger.error(f"Coverage below {threshold}%")
            logger.info(result.stdout)
            return False
            
        logger.info(f"Coverage meets {threshold}% requirement")
        logger.info(result.stdout)
        # Verify critical modules have required coverage
        critical_modules = {
            'app/models': 95,
            'app/services': 95,
            'app/routes': 90,
            'app/controllers': 90,
            'app/security': 95
        }
        
        for module, min_coverage in critical_modules.items():
            if module in result.stdout:
                coverage_line = next(line for line in result.stdout.splitlines() 
                                   if module in line)
                coverage_pct = int(coverage_line.split()[-1].rstrip('%'))
                if coverage_pct < min_coverage:
                    logger.error(f"{module} coverage {coverage_pct}% < {min_coverage}%")
                    return False
                    
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
