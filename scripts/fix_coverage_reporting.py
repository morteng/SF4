import os
import sys
import logging
from pathlib import Path

def fix_coverage():
    """Fix test coverage reporting issues"""
    try:
        # Configure logging
        logging.basicConfig(level=logging.INFO)
        logger = logging.getLogger(__name__)
        
        # Add project root to Python path
        project_root = str(Path(__file__).parent.parent)
        if project_root not in sys.path:
            sys.path.insert(0, project_root)
            
        # Verify imports
        try:
            import app
            import scripts
        except ImportError as e:
            logger.error(f"Import error: {str(e)}")
            return False
            
        # Run coverage
        import subprocess
        result = subprocess.run(
            ['coverage', 'run', '--source=app', '-m', 'pytest', 'tests/'],
            capture_output=True,
            text=True
        )
        
        if result.returncode != 0:
            logger.error("Tests failed during coverage run")
            logger.error(result.stderr)
            return False
            
        # Generate coverage report
        subprocess.run(['coverage', 'report', '-m'])
        subprocess.run(['coverage', 'html'])
        
        logger.info("Fixed coverage reporting")
        return True
    except Exception as e:
        logger.error(f"Failed to fix coverage reporting: {str(e)}")
        return False

if __name__ == "__main__":
    if fix_coverage():
        print("Coverage reporting fixed successfully")
        exit(0)
    else:
        print("Failed to fix coverage reporting")
        exit(1)
