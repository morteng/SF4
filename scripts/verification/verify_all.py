import sys
import logging
from pathlib import Path
from typing import Dict, Any

def configure_verification_logger():
    """Centralized logger configuration for verification"""
    logger = logging.getLogger('verification')
    if not logger.handlers:
        handler = logging.StreamHandler()
        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        logger.setLevel(logging.INFO)
    return logger

def get_dashboard_metrics() -> Dict[str, Any]:
    """Collect metrics for monitoring dashboard"""
    from scripts.verification.verify_monitoring import verify_monitoring_dashboards
    from scripts.verification.verify_db_connection import validate_db_connection
    from scripts.verification.verify_tests import verify_tests
    from scripts.verification.verify_security import verify_security_settings
    
    metrics = {
        'database': validate_db_connection(os.getenv('SQLALCHEMY_DATABASE_URI')),
        'tests': verify_tests(),
        'security': verify_security_settings(),
        'monitoring': verify_monitoring_dashboards()
    }
    
    # Add performance metrics
    import psutil
    metrics.update({
        'cpu': psutil.cpu_percent(),
        'memory': psutil.virtual_memory().percent,
        'disk': psutil.disk_usage('/').percent
    })
    
    return metrics

def verify_all(production: bool = True) -> bool:
    """Run all verification checks and collect metrics"""
    logger = configure_verification_logger()
    
    try:
        # Configure paths first
        from scripts.path_config import configure_paths
        if not configure_paths(production=production, verify=True):
            logger.error("Path configuration failed")
            return False
            
        # Get dashboard metrics
        metrics = get_dashboard_metrics()
        
        # Log metrics
        logger.info("Verification metrics collected:")
        for name, value in metrics.items():
            logger.info(f"{name}: {value}")
            
        return all(metrics.values())
        
    except Exception as e:
        logger.error(f"Verification failed: {str(e)}")
        return False

if __name__ == "__main__":
    if verify_all():
        print("All verifications passed")
        sys.exit(0)
    else:
        print("Verification failed")
        sys.exit(1)
