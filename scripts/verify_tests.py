import sys
import subprocess
from pathlib import Path

def verify_tests():
    """Verify all tests pass with proper configuration"""
    try:
        # Add project root to Python path
        root_dir = Path(__file__).parent.parent
        sys.path.append(str(root_dir))
        
        # Run core test suites
        test_suites = [
            'tests/models/test_relationships.py',
            'tests/version_management/test_version.py'
        ]
        
        for suite in test_suites:
            result = subprocess.run(
                ['pytest', '-v', suite],
                capture_output=True,
                text=True
            )
            
            if result.returncode != 0:
                print(f"Test suite failed: {suite}")
                print(result.stdout)
                print(result.stderr)
                return False
                
        print("All test suites passed")
        return True
    except Exception as e:
        print(f"Test verification failed: {str(e)}")
        return False

if __name__ == "__main__":
    if verify_tests():
        exit(0)
    else:
        exit(1)
