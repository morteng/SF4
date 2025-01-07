import sys
import os
from pathlib import Path
import logging
from scripts.version import validate_db_connection

def verify_security_settings():
    """Verify security-related settings"""
    secret_key = os.getenv('SECRET_KEY')
    if not secret_key or len(secret_key) < 64:
        logging.error("SECRET_KEY must be at least 64 characters")
        return False
    if not any(c.isupper() for c in secret_key):
        logging.error("SECRET_KEY must contain uppercase letters")
        return False
    if not any(c.islower() for c in secret_key):
        logging.error("SECRET_KEY must contain lowercase letters")
        return False
    if not any(c.isdigit() for c in secret_key):
        logging.error("SECRET_KEY must contain numbers")
        return False
    if not any(c in '!@#$%^&*()' for c in secret_key):
        logging.error("SECRET_KEY must contain special characters")
        return False
    return True

def verify_deployment():
    """Verify all deployment requirements are met"""
    try:
        # Verify security settings first
        if not verify_security_settings():
            return False
            
        # Check required files exist
        required_files = [
            'DEPLOYMENT_CHECKLIST.md',
            'RELEASE_NOTES.md',
            'VERSION_HISTORY.md',
            'requirements.txt',
            'migrations/alembic.ini'
        ]
        
        # Check for latest backup or any timestamped backup
        backup_files = list(Path('backups').glob('stipend_*.db'))
        if not backup_files:
            logging.error("No database backups found")
            return False
            
        # Check for latest log archive or any timestamped archive
        log_files = list(Path('logs').glob('archive_*.zip'))
        if not log_files:
            logging.error("No log archives found")
            return False
            
        for file in required_files:
            if not Path(file).exists():
                logging.error(f"Required file missing: {file}")
                return False
                
        # Check environment variables
        required_vars = [
            'FLASK_ENV',
            'FLASK_DEBUG',
            'SQLALCHEMY_DATABASE_URI',
            'SECRET_KEY'
        ]
        
        missing_vars = [var for var in required_vars if var not in os.environ]
        if missing_vars:
            logging.error(f"Missing environment variables: {', '.join(missing_vars)}")
            return False
            
        return True
    except Exception as e:
        logging.error(f"Deployment verification failed: {str(e)}")
        return False

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    if verify_deployment():
        print("Deployment verification passed")
        exit(0)
    else:
        print("Deployment verification failed")
        exit(1)
