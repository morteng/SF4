import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pytest

def run_tests():
    """Run relationship tests"""
    try:
        result = pytest.main(['tests/models/test_relationships.py', '-v'])
        if result == 0:
            print("All relationship tests passed")
            return True
        else:
            print("Some relationship tests failed")
            return False
    except Exception as e:
        print(f"Error running relationship tests: {str(e)}")
        return False

if __name__ == "__main__":
    run_tests()
