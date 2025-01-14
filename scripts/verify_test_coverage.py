import coverage
import os
import sys
import logging
from pathlib import Path

def verify_coverage():
    """Verify test coverage meets minimum threshold"""
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    logger = logging.getLogger(__name__)
    
    try:
        # Initialize coverage with proper config
        cov = coverage.Coverage(
            config_file='pytest.ini',
            data_file='.coverage.verified',
            branch=True,
            concurrency='multiprocessing',
            source=['app', 'scripts'],
            omit=[
                '*/__init__.py',
                '*/tests/*',
                '*/migrations/*',
                '*/extensions.py',
                '*/version.py'
            ]
        )
        cov.start()
        logger.info("Coverage started with multiprocessing support")
        
        # Run tests
        test_result = os.system('pytest tests/ --cov=app --cov-report=term-missing')
        if test_result != 0:
            logger.error("Tests failed to run successfully")
            raise RuntimeError("Test execution failed")
            
        # Ensure coverage data exists
        if not os.path.exists('.coverage.verified'):
            logger.error("No coverage data collected")
            raise RuntimeError("No coverage data collected")
            
        cov.stop()
        cov.save()
        logger.info("Coverage data saved")
        
        # Verify coverage data was collected
        if not cov.get_data():
            logger.error("No coverage data available")
            raise RuntimeError("No coverage data available")
            
        # Generate detailed report
        cov.report(show_missing=True)
        total_coverage = cov.get_data().lines_covered_percent()
        logger.info(f"Total coverage: {total_coverage:.2f}%")
        
        # Check if coverage meets target
        target = 85.0
        if total_coverage >= target:
            logger.info(f"✅ Test coverage meets target: {total_coverage:.1f}% >= {target}%")
            return True
        else:
            logger.warning(f"❌ Test coverage below target: {total_coverage:.1f}% < {target}%")
            # Generate HTML report for detailed analysis
            cov.html_report(
                directory='coverage_report',
                title='Test Coverage Report',
                skip_covered=True
            )
            logger.info("HTML coverage report generated")
            return False
            
    except Exception as e:
        logger.error(f"⚠️ Error verifying coverage: {str(e)}", exc_info=True)
        return False
    finally:
        # Ensure coverage is stopped
        cov.stop()
        cov.save()
        logger.info("Coverage verification completed")

if __name__ == "__main__":
    if not verify_coverage():
        sys.exit(1)
