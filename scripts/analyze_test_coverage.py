import coverage
import os
from pathlib import Path

def analyze_coverage():
    """Analyze test coverage and generate report"""
    # Initialize coverage
    cov = coverage.Coverage()
    cov.start()
    
    # Run tests
    os.system('python -m pytest')
    
    # Stop coverage and generate report
    cov.stop()
    cov.save()
    
    # Generate HTML report
    cov.html_report(directory='coverage_report')
    
    # Print summary
    cov.report()
    print("\nCoverage report generated in coverage_report/ directory")

if __name__ == "__main__":
    analyze_coverage()
