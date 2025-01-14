import coverage
import os
import sys

def verify_coverage():
    """Verify test coverage meets minimum threshold"""
    # Initialize coverage with config
    cov = coverage.Coverage(config_file='.coveragerc')
    cov.start()
    
    try:
        # Run tests with explicit paths and coverage
        result = os.system('coverage run -m pytest tests/app/ tests/')
        if result != 0:
            raise RuntimeError("Tests failed to run successfully")
            
        # Ensure coverage data exists
        if not os.path.exists('.coverage'):
            raise RuntimeError("No coverage data collected")
            
        cov.stop()
        cov.save()
        
        # Verify coverage data was collected
        if not cov.get_data():
            raise RuntimeError("No coverage data collected - check test paths")
            
        # Generate detailed report
        cov.report()
        total_coverage = cov.get_data().lines_covered_percent()
        
        # Check if coverage meets target
        target = 85.0
        if total_coverage >= target:
            try:
                print(f"✅ Test coverage meets target: {total_coverage:.1f}% >= {target}%")
            except UnicodeEncodeError:
                print(f"Test coverage meets target: {total_coverage:.1f}% >= {target}%")
            return True
        else:
            try:
                print(f"❌ Test coverage below target: {total_coverage:.1f}% < {target}%")
            except UnicodeEncodeError:
                print(f"Test coverage below target: {total_coverage:.1f}% < {target}%")
            # Generate HTML report for detailed analysis
            cov.html_report(directory='coverage_report')
            return False
            
    except Exception as e:
        try:
            print(f"⚠️ Error verifying coverage: {str(e)}")
        except UnicodeEncodeError:
            print("Warning: Error verifying coverage")
        return False
    finally:
        # Ensure coverage is stopped
        cov.stop()
        cov.save()

if __name__ == "__main__":
    if not verify_coverage():
        sys.exit(1)
