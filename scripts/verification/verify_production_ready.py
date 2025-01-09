import os
import logging
from pathlib import Path

def configure_logger():
    """Configure logger for production readiness verification"""
    logger = logging.getLogger(__name__)
    if not logger.handlers:
        handler = logging.StreamHandler()
        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        logger.setLevel(logging.INFO)
    return logger

def verify_production_ready():
    """Verify production readiness with comprehensive checks"""
    try:
        # Configure and verify paths
        from scripts.path_config import configure_paths, verify_path_config
        if not configure_paths():
            raise RuntimeError("Failed to configure paths")
        if not verify_path_config():
            raise RuntimeError("Path configuration verification failed")
            
        logger = configure_logger()
        
        # Set default environment variables if missing
        default_vars = {
            'BACKUP_DIR': 'backups',
            'LOG_DIR': 'logs',
            'FLASK_ENV': 'production',
            'FLASK_DEBUG': '0'
        }
        
        for var, default in default_vars.items():
            if not os.getenv(var):
                os.environ[var] = default
                logger.info(f"Set default value for {var}: {default}")
                
        # Ensure debug mode is disabled
        if os.getenv('FLASK_DEBUG', '0').lower() in ('1', 'true', 'yes'):
            logger.error("Debug mode must be disabled in production")
            return False
        
        # Verify required environment variables
        required_vars = [
            'SQLALCHEMY_DATABASE_URI',
            'SECRET_KEY',
            'ADMIN_PASSWORD'
        ]
        
        missing_vars = [var for var in required_vars if not os.getenv(var)]
        if missing_vars:
            logger.error(f"Missing required environment variables: {', '.join(missing_vars)}")
            return False
            
        # Verify debug mode is disabled
        if os.getenv('FLASK_DEBUG', '0').lower() in ('1', 'true', 'yes'):
            logger.error("Debug mode must be disabled in production")
            return False
            
        # Verify database connection
        from scripts.verification.verify_db_connection import verify_db_connection
        if not verify_db_connection():
            logger.error("Database connection verification failed")
            return False
            
        # Verify security settings
        from scripts.verification.verify_security import verify_security_settings
        if not verify_security_settings():
            logger.error("Security verification failed")
            return False
            
        logger.info("Production environment is ready")
        return True
        
    except Exception as e:
        logger.error(f"Production readiness verification failed: {str(e)}")
        return False

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    if verify_production_ready():
        print("Production readiness verification passed")
        exit(0)
    else:
        print("Production readiness verification failed")
        exit(1)
