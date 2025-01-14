import coverage
import os
import sys

def verify_coverage():
    """Verify test coverage meets minimum threshold"""
    cov = coverage.Coverage()
    cov.start()
    
    # Run tests
    os.system('python -m pytest')
    
    cov.stop()
    cov.save()
    
    # Get coverage percentage
    cov.report()
    total_coverage = cov.report()
    
    # Check if coverage meets target
    target = 85.0
    if total_coverage >= target:
        print(f"✅ Test coverage meets target: {total_coverage:.1f}% >= {target}%")
        return True
    else:
        print(f"❌ Test coverage below target: {total_coverage:.1f}% < {target}%")
        return False

if __name__ == "__main__":
    if not verify_coverage():
        sys.exit(1)
