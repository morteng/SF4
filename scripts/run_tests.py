import subprocess

def run_tests():
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
        
        # Run tests with coverage
        subprocess.run([
            'pytest', 
            'tests/',
            '--cov=app',
            '--cov-report=term-missing',
            '--cov-report=xml'
        ], check=True)
        
        # Verify coverage
        from scripts.verify_test_coverage import verify_coverage
        if not verify_coverage():
            raise Exception("Test coverage below required threshold")
    except subprocess.CalledProcessError as e:
        print(f"Tests failed with error: {e}")
        return False
    return True
