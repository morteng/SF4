import os
import sys
import subprocess

def generate_coverage():
    """Generate test coverage report"""
    try:
        # Run coverage
        result = subprocess.run([
            'coverage', 'run', '--source=app,scripts', 
            '-m', 'pytest', 'tests/'
        ], capture_output=True, text=True)
        
        if result.returncode != 0:
            print("Error running coverage tests")
            print(result.stderr)
            return False
            
        # Generate report
        subprocess.run(['coverage', 'report', '-m'])
        return True
        
    except Exception as e:
        print(f"Error generating coverage report: {str(e)}")
        return False

if __name__ == "__main__":
    generate_coverage()