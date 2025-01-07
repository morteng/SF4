import subprocess

def run_tests():
    try:
        # Setup test environment first
        from scripts.setup_test_env import setup_test_paths
        setup_test_paths()
        
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
