import os
import sys
import logging
from pathlib import Path
import coverage
import pytest

def fix_coverage():
    """Fix test coverage reporting issues"""
    try:
        # Configure logging
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        logger = logging.getLogger(__name__)
        
        # Add project root to Python path
        project_root = str(Path(__file__).parent.parent)
        if project_root not in sys.path:
            sys.path.insert(0, project_root)
            
        # Verify imports
        try:
            import app
            import scripts
            logger.info("Imports verified successfully")
        except ImportError as e:
            logger.error(f"Import error: {str(e)}")
            return False
            
        # Initialize coverage with proper config
        cov = coverage.Coverage(
            source=['app'],
            omit=[
                '*/__init__.py',
                '*/tests/*',
                '*/migrations/*',
                '*/scripts/*',
                '*/templates/*'
            ],
            branch=True,
            data_file='.coverage.fixed'
        )
        cov.start()
        logger.info("Coverage started")
        
        # Run tests
        test_result = pytest.main(['tests/', '--cov=app', '--cov-report=term-missing'])
        if test_result != 0:
            logger.error("Some tests failed during coverage run")
            return False
            
        # Stop and save coverage
        cov.stop()
        cov.save()
        logger.info("Coverage data saved")
        
        # Generate reports
        cov.report(show_missing=True)
        cov.html_report(
            directory='coverage_report',
            title='Test Coverage Report',
            skip_covered=True
        )
        logger.info("Coverage reports generated")
        
        return True
    except Exception as e:
        logger.error(f"Failed to fix coverage reporting: {str(e)}", exc_info=True)
        return False

if __name__ == "__main__":
    if fix_coverage():
        print("Coverage reporting fixed successfully")
        exit(0)
    else:
        print("Failed to fix coverage reporting")
        exit(1)
