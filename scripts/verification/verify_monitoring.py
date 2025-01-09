import os
import logging
from pathlib import Path

def configure_logger():
    """Configure logger for monitoring verification"""
    logger = logging.getLogger(__name__)
    if not logger.handlers:
        handler = logging.StreamHandler()
        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        logger.setLevel(logging.INFO)
    return logger

def verify_monitoring_setup():
    """Verify production monitoring configuration"""
    logger = configure_logger()
    
    try:
        # Verify required monitoring environment variables with defaults
        required_vars = {
            'MONITORING_ENABLED': 'true',
            'METRICS_ENDPOINT': '/metrics',
            'ALERTING_ENABLED': 'true',
            'MONITORING_INTERVAL': '60',
            'ALERT_THRESHOLDS': 'cpu:90,memory:90,disk:90'
        }
        
        # Set default values if not present
        for var, default in required_vars.items():
            if not os.getenv(var):
                os.environ[var] = default
                logger.info(f"Set default value for {var}: {default}")
        
        missing_vars = [var for var in required_vars if not os.getenv(var)]
        if missing_vars:
            logger.error(f"Missing monitoring environment variables: {', '.join(missing_vars)}")
            return False
            
        # Verify monitoring directory exists
        monitoring_dir = Path('monitoring')
        if not monitoring_dir.exists():
            logger.error("Monitoring directory not found")
            return False
            
        # Verify required monitoring files
        required_files = [
            'monitoring/dashboard.json',
            'monitoring/alerts.json',
            'monitoring/metrics.py'
        ]
        
        missing_files = [f for f in required_files if not Path(f).exists()]
        if missing_files:
            logger.error(f"Missing monitoring files: {', '.join(missing_files)}")
            return False
            
        logger.info("Monitoring setup verification passed")
        return True
        
    except Exception as e:
        logger.error(f"Monitoring verification failed: {str(e)}")
        return False

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    if verify_monitoring_setup():
        print("Monitoring verification passed")
        exit(0)
    else:
        print("Monitoring verification failed")
        exit(1)
