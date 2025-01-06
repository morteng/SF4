import sys
import os
import subprocess

def check_coverage():
    """Check test coverage meets requirements"""
    try:
        result = subprocess.run(
            ['pytest', '--cov=scripts.version', '--cov-report=term-missing'],
            capture_output=True,
            text=True
        )
        
        if result.returncode != 0:
            print("Test coverage check failed")
            print(result.stdout)
            print(result.stderr)
            return False
            
        print("Test coverage check passed")
        return True
    except Exception as e:
        print(f"Error checking coverage: {str(e)}")
        return False

if __name__ == "__main__":
    check_coverage()
