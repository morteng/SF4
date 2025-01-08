import os
import logging
from pathlib import Path

def verify_security_settings():
    """Verify security-related settings with enhanced checks"""
    try:
        # Verify SECRET_KEY
        secret_key = os.getenv('SECRET_KEY')
        if not secret_key or len(secret_key) < 64:
            logging.error("SECRET_KEY must be at least 64 characters")
            return False
            
        # Check password complexity
        admin_password = os.getenv('ADMIN_PASSWORD')
        if admin_password and len(admin_password) < 12:
            logging.error("ADMIN_PASSWORD must be at least 12 characters")
            return False
            
        # Verify environment variables
        required_vars = [
            'FLASK_ENV',
            'FLASK_DEBUG',
            'SQLALCHEMY_DATABASE_URI',
            'SECRET_KEY',
            'ADMIN_PASSWORD'
        ]
        
        missing_vars = [var for var in required_vars if not os.getenv(var)]
        if missing_vars:
            logging.error(f"Missing required environment variables: {', '.join(missing_vars)}")
            return False
            
        # Verify file permissions
        sensitive_files = [
            '.env',
            'instance/site.db',
            'migrations/'
        ]
        
        for file in sensitive_files:
            path = Path(file)
            if path.exists():
                mode = path.stat().st_mode
                if mode & 0o077:  # Check for world-readable/writable
                    logging.error(f"Insecure permissions on {file}: {oct(mode)}")
                    return False
                    
        return True
    except Exception as e:
        logging.error(f"Security verification failed: {str(e)}")
        return False

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    if verify_security_settings():
        print("Security verification passed")
        exit(0)
    else:
        print("Security verification failed")
        exit(1)
