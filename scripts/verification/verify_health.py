import logging
import os
import requests
from pathlib import Path

def configure_logger():
    """Configure logger for health verification"""
    logger = logging.getLogger(__name__)
    if not logger.handlers:
        handler = logging.StreamHandler()
        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        logger.setLevel(logging.INFO)
    return logger

def verify_system_health(production=True, check_response_time=True, monitoring=False):
    """Perform comprehensive system health check with production focus and monitoring integration"""
    logger = configure_logger()
    
    try:
        # Verify database connection
        from scripts.verification.verify_db_connection import verify_db_connection
        if not verify_db_connection():
            logger.error("Database connection check failed")
            return False
            
        # Verify monitoring
        from scripts.verification.verify_monitoring import verify_monitoring_setup
        if not verify_monitoring_setup():
            logger.error("Monitoring check failed")
            return False
            
        # Verify backups
        from scripts.verification.verify_backup import verify_backup_integrity
        backup_files = sorted(Path('backups').glob('stipend_*.db'), reverse=True)
        if backup_files and not verify_backup_integrity(backup_files[0]):
            logger.error("Backup check failed")
            return False
            
        # Verify web interface
        base_url = os.getenv('BASE_URL', 'http://localhost:5000')
        try:
            response = requests.get(f"{base_url}/health")
            if response.status_code != 200:
                logger.error("Web interface health check failed")
                return False
                
            # Check response time in production
            if production and check_response_time:
                response_time = response.elapsed.total_seconds()
                if response_time > 2.0:
                    logger.warning(f"Slow response time: {response_time:.2f}s")
                
            # Check response time in production
            if production and check_response_time:
                response_time = response.elapsed.total_seconds()
                if response_time > 2.0:
                    logger.warning(f"Slow response time: {response_time:.2f}s")
        except Exception as e:
            logger.error(f"Web interface check failed: {str(e)}")
            return False
            
        logger.info("System health verification passed")
        return True
        
    except Exception as e:
        logger.error(f"Health verification failed: {str(e)}")
        return False

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    if verify_system_health():
        print("System health verification passed")
        exit(0)
    else:
        print("System health verification failed")
        exit(1)
