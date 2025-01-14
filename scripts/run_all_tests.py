import subprocess
import sys

def run_tests():
    """Run all test suites"""
    test_commands = [
        "pytest --cov=scripts.version --cov-report=term-missing"
    ]
    
    for cmd in test_commands:
        result = subprocess.run(cmd, shell=True)
        if result.returncode != 0:
            print(f"Test command failed: {cmd}")
            return False
    return True

if __name__ == "__main__":
    if run_tests():
        print("All tests completed successfully")
        sys.exit(0)
    else:
        print("Some tests failed")
        sys.exit(1)
