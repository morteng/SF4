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
