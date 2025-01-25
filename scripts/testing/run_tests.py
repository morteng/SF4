import subprocess

def run_tests(test_type='all'):
    """Enhanced test runner with proper environment setup"""
    try:
        # Configure logging
        from scripts.init_logging import configure_logging
        configure_logging()
        
        # Setup test environment
        from scripts.setup_test_env import setup_test_paths, configure_test_environment
        if not setup_test_paths():
            raise RuntimeError("Failed to setup test paths")
        if not configure_test_environment():
            raise RuntimeError("Failed to configure test environment")
        
        # Setup test environment
        from scripts.setup_test_env import setup_test_paths, configure_test_environment
        if not setup_test_paths():
            raise RuntimeError("Failed to setup test paths")
        if not configure_test_environment():
            raise RuntimeError("Failed to configure test environment")
            
        # Determine test paths based on type
        test_paths = {
            'unit': 'tests/unit',
            'integration': 'tests/integration',
            'e2e': 'tests/e2e',
            'all': 'tests/'
        }.get(test_type, 'tests/')
        
        # Setup test environment
        from scripts.setup_test_env import setup_test_paths, configure_test_environment
        if not setup_test_paths():
            raise RuntimeError("Failed to setup test paths")
        if not configure_test_environment():
            raise RuntimeError("Failed to configure test environment")
        
        # Run enhanced test suite with verification steps
        test_cmds = [
            ['pytest', 'tests/', '--cov=app', '--cov-report=term-missing'],
            ['python', 'scripts/verification/validate_datetime_fields.py', '--all-formats'],
            ['python', 'scripts/verification/verify_audit_logs.py', '--with-notifications'],
            ['python', 'scripts/verification/verify_security.py', '--test-headers'],
            ['python', 'scripts/verification/verify_security.py', '--test-rate-limits']
        ]
        
        failures = 0
        for cmd in test_cmds:
            result = subprocess.run(cmd, check=False)
            if result.returncode != 0:
                failures += 1
        
        # Verify coverage
        from scripts.verify_test_coverage import verify_coverage
        if not verify_coverage():
            raise Exception("Test coverage below required threshold")
    except subprocess.CalledProcessError as e:
        print(f"Tests failed with error: {e}")
        return False
    return True
import sys
import unittest
import coverage
from pathlib import Path
import logging

def configure_logging():
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )

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
    parser.add_argument('--test-type', default='all')
    args = parser.parse_args()
    
    configure_logging()
    success = run_tests(args.test_type)
    sys.exit(0 if success else 1)
