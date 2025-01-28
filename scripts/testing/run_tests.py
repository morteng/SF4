import sys
import unittest
import coverage
from pathlib import Path
import logging

from logging_config import LoggingConfig

def configure_logging():
    """Configure basic logging for the script"""
    logger = LoggingConfig(root_path=Path(__file__).parent.parent)
    logger.configure_logging()
    return logging.getLogger('tests')

def run_tests(test_type='all'):
    """Enhanced test runner with coverage tracking"""
    try:
        # Configure paths first
        project_root = Path(__file__).parent.parent
        sys.path.insert(0, str(project_root))
        
        # Initialize coverage
        cov = coverage.Coverage(config_file=str(project_root / '.coveragerc'))
        cov.start()
        
        # Discover tests
        loader = unittest.TestLoader()
        if test_type == 'unit':
            suite = loader.discover('tests/unit')
        elif test_type == 'integration':
            suite = loader.discover('tests/integration')
        elif test_type == 'e2e':
            suite = loader.discover('tests/e2e')
        else:
            suite = loader.discover('tests')
        
        # Run tests
        runner = unittest.TextTestRunner(verbosity=2)
        result = runner.run(suite)
        
        # Generate reports
        cov.stop()
        cov.save()
        cov.xml_report(outfile=str(project_root / 'reports' / 'coverage.xml'))
        cov.html_report(directory=str(project_root / 'reports' / 'htmlcov'))
        
        return result.wasSuccessful()
        
    except Exception as e:
        logging.error(f"Test execution failed: {str(e)}")
        return False

if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--test-type', default='all', 
                      help="Test type: unit, integration, e2e, or all")
    parser.add_argument('--coverage', action='store_true',
                      help="Enable coverage tracking")
    args = parser.parse_args()
    
    configure_logging()
    success = run_tests(args.test_type)
    sys.exit(0 if success else 1)
