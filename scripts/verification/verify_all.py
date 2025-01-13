import sys
import logging
import os

import psutil

# External verification imports (moved to the top for clarity)
from scripts.verification.verify_monitoring import verify_monitoring_dashboards
from scripts.verification.verify_db_connection import validate_db_connection
from scripts.verification.verify_tests import verify_tests
from scripts.verification.verify_security import verify_security_settings
from scripts.path_config import configure_paths


def configure_verification_logger() -> logging.Logger:
    """
    Configures and returns a centralized logger for verification tasks.
    """
    logger = logging.getLogger('verification')
    if not logger.handlers:
        handler = logging.StreamHandler()
        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        logger.setLevel(logging.INFO)
    return logger


def get_check_metrics() -> dict:
    """
    Collects boolean metrics for the verification checks.
    """
    # Safely get database URI (fallback to in-memory SQLite if not set)
    db_uri = os.getenv('SQLALCHEMY_DATABASE_URI', 'sqlite:///:memory:')

    checks = {
        'database': validate_db_connection(db_uri),
        'tests': verify_tests(),
        'security': verify_security_settings(),
        'monitoring': verify_monitoring_dashboards()
    }
    return checks


def get_performance_metrics() -> dict:
    """
    Collects system performance metrics.
    """
    return {
        'cpu': psutil.cpu_percent(),
        'memory': psutil.virtual_memory().percent,
        'disk': psutil.disk_usage('/').percent
    }


def verify_all(production: bool = True) -> bool:
    """
    Run all verification checks and log collected metrics.
    Returns True if all boolean checks pass; otherwise, False.
    """
    logger = configure_verification_logger()
    
    try:
        # Configure paths
        if not configure_paths(production=production, verify=True):
            logger.error("Path configuration failed.")
            return False

        # Collect metrics
        checks = get_check_metrics()
        performance = get_performance_metrics()

        # Log verification results
        logger.info("Verification checks (boolean results):")
        for name, value in checks.items():
            logger.info(f"  {name}: {value}")

        logger.info("Performance metrics:")
        for name, value in performance.items():
            logger.info(f"  {name}: {value}")

        # Only the boolean checks are used to determine overall pass/fail
        all_pass = all(checks.values())
        return all_pass

    except Exception as e:
        logger.error(f"Verification failed: {e}")
        return False


if __name__ == "__main__":
    # Decide exit code based on success or failure
    if verify_all():
        print("All verifications passed")
        sys.exit(0)
    else:
        print("Verification failed")
        sys.exit(1)
