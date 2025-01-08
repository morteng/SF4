import sys
import subprocess
import logging
from pathlib import Path

def configure_coverage_logging():
    """Configure logging for coverage verification"""
    logger = logging.getLogger('coverage')
    if not logger.handlers:
        handler = logging.StreamHandler()
        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        logger.setLevel(logging.INFO)
    return logger

def verify_coverage(threshold=80):
    """Verify test coverage meets requirements with enhanced checks"""
    logger = configure_coverage_logging()
    
    # Verify minimum coverage threshold
    if threshold < 80:
        logger.error(f"Coverage threshold {threshold}% is below minimum required 80%")
        return False
    
    try:
        # Add project root to Python path
        project_root = str(Path(__file__).parent.parent)
        if project_root not in sys.path:
            sys.path.insert(0, project_root)
        
        # Run coverage report with detailed output
        result = subprocess.run(
            ['coverage', 'report', '--fail-under=80', '--show-missing', '--skip-covered'],
            capture_output=True,
            text=True
        )
        
        # Verify critical modules have 90%+ coverage
        critical_modules = {
            'app/models': 90,
            'app/services': 90,
            'app/routes': 85
        }
        
        for module, min_coverage in critical_modules.items():
            if module in result.stdout:
                coverage_line = next(line for line in result.stdout.splitlines() 
                                   if module in line)
                coverage_pct = int(coverage_line.split()[-1].rstrip('%'))
                if coverage_pct < min_coverage:
                    logger.error(f"{module} coverage {coverage_pct}% < {min_coverage}%")
                    return False
        
        # Verify minimum coverage per module
        module_coverage = {
            'app': 80,
            'scripts': 90,
            'tests': 95
        }
        
        for module, min_coverage in module_coverage.items():
            if f"{module}/" in result.stdout:
                coverage_line = next(line for line in result.stdout.splitlines() 
                                   if f"{module}/" in line)
                coverage_pct = int(coverage_line.split()[-1].rstrip('%'))
                if coverage_pct < min_coverage:
                    logger.error(f"{module} coverage {coverage_pct}% < {min_coverage}%")
                    return False
        
        if result.returncode != 0:
            logger.error(f"Coverage verification failed: {result.stderr}")
            return False
            
        logger.info("Coverage verification passed")
        logger.info(result.stdout)
        return True
        
    except Exception as e:
        logger.error(f"Coverage verification failed: {str(e)}")
        return False

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    if verify_coverage():
        exit(0)
    else:
        exit(1)
