import sys
import os
from pathlib import Path
import logging

def verify_deployment():
    """Verify all deployment requirements are met"""
    try:
        # Check required files exist
        required_files = [
            'DEPLOYMENT_CHECKLIST.md',
            'RELEASE_NOTES.md',
            'VERSION_HISTORY.md',
            'backups/stipend_latest.db',
            'logs/archive_latest.zip'
        ]
        
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