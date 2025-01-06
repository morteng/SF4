import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pytest

def run_tests():
    """Run version management tests"""
    try:
        result = pytest.main(['tests/version_management/', '-v'])
        if result == 0:
            print("All version management tests passed")
            return True
        else:
            print("Some version management tests failed")
            return False
    except Exception as e:
        print(f"Error running version management tests: {str(e)}")
        return False

if __name__ == "__main__":
    run_tests()
