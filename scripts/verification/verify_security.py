import os
import logging
from pathlib import Path

def configure_logger():
    """Configure logger for security verification"""
    logger = logging.getLogger(__name__)
    if not logger.handlers:
        handler = logging.StreamHandler()
        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        logger.setLevel(logging.INFO)
    return logger

def verify_security_settings():
    """Verify security-related settings with enhanced checks"""
    logger = configure_logger()
    
    try:
        # Verify SECRET_KEY
        secret_key = os.getenv('SECRET_KEY')
        if not secret_key or len(secret_key) < 64:
            logger.error("SECRET_KEY must be at least 64 characters")
            return False
            
        # Check password complexity
        admin_password = os.getenv('ADMIN_PASSWORD')
        if admin_password and len(admin_password) < 12:
            logger.error("ADMIN_PASSWORD must be at least 12 characters")
            return False
            
        # Verify debug mode is disabled in production
        if os.getenv('FLASK_ENV') == 'production' and os.getenv('FLASK_DEBUG') == '1':
            logger.error("Debug mode must be disabled in production")
            return False
            
        # Verify environment variables
        required_vars = [
            'FLASK_ENV',
            'FLASK_DEBUG',
            'SQLALCHEMY_DATABASE_URI',
            'SECRET_KEY',
            'ADMIN_PASSWORD',
            'BACKUP_DIR',
            'LOG_DIR'
        ]
        
        missing_vars = [var for var in required_vars if not os.getenv(var)]
        if missing_vars:
            logger.error(f"Missing required environment variables: {', '.join(missing_vars)}")
            return False
            
        # Verify file permissions strictly
        sensitive_files = {
            '.env': 0o600,
            'instance/site.db': 0o600,
            'migrations/': 0o700,
            'logs/': 0o750,
            'scripts/': 0o750
        }
        
        for file, expected_mode in sensitive_files.items():
            path = Path(file)
            if path.exists():
                mode = path.stat().st_mode & 0o777
                if mode != expected_mode:
                    logger.error(f"Insecure permissions on {file}: {oct(mode)} (expected {oct(expected_mode)})")
                    return False
                    
        return True
    except Exception as e:
        logger.error(f"Security verification failed: {str(e)}")
        return False

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    if verify_security_settings():
        print("Security verification passed")
        exit(0)
    else:
        print("Security verification failed")
        exit(1)
