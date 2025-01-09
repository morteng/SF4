import os
import logging
from pathlib import Path

def configure_logger():
    """Configure logger for security audit"""
    logger = logging.getLogger(__name__)
    if not logger.handlers:
        handler = logging.StreamHandler()
        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        logger.setLevel(logging.INFO)
    return logger

def security_audit():
    """Perform comprehensive security audit"""
    logger = configure_logger()
    
    try:
        # Verify environment variables
        from scripts.verification.verify_security import verify_security_settings
        if not verify_security_settings():
            logger.error("Security settings verification failed")
            return False
            
        # Verify file permissions
        from scripts.security.fix_security_permissions import fix_permissions
        if not fix_permissions():
            logger.error("Security permissions verification failed")
            return False
            
        # Verify database security
        from scripts.verification.verify_db_connection import verify_db_connection
        if not verify_db_connection():
            logger.error("Database security verification failed")
            return False
            
        # Verify backup system
        from scripts.verification.verify_backup import verify_backup_integrity
        backup_files = sorted(Path('backups').glob('stipend_*.db'), reverse=True)
        if not backup_files or not verify_backup_integrity(backup_files[0]):
            logger.error("Backup system verification failed")
            return False
            
        logger.info("Security audit completed successfully")
        return True
        
    except Exception as e:
        logger.error(f"Security audit failed: {str(e)}")
        return False

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    if security_audit():
        print("Security audit passed")
        exit(0)
    else:
        print("Security audit failed")
        exit(1)
