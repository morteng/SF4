import os
import logging
from pathlib import Path

def configure_logger():
    """Configure logging for test environment verification"""
    logger = logging.getLogger('test_env')
    if not logger.handlers:
        handler = logging.StreamHandler()
        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        logger.setLevel(logging.INFO)
    return logger

def verify_test_environment():
    """Verify test environment is properly configured"""
    logger = configure_logger()
    
    try:
        # Verify required environment variables
        required_vars = [
            'FLASK_ENV',
            'SQLALCHEMY_DATABASE_URI',
            'ADMIN_USERNAME',
            'ADMIN_EMAIL',
            'ADMIN_PASSWORD',
            'SECRET_KEY',
            'TESTING'
        ]
        
        missing_vars = [var for var in required_vars if var not in os.environ]
        if missing_vars:
            logger.error(f"Missing environment variables: {', '.join(missing_vars)}")
            return False
            
        # Verify database URI
        if not os.getenv('SQLALCHEMY_DATABASE_URI').startswith('sqlite:///'):
            logger.error("Test database must use SQLite")
            return False
            
        # Verify admin credentials
        if len(os.getenv('ADMIN_PASSWORD')) < 12:
            logger.error("Test admin password must be at least 12 characters")
            return False
            
        # Verify secret key
        if len(os.getenv('SECRET_KEY')) < 64:
            logger.error("Test secret key must be at least 64 characters")
            return False
            
        logger.info("Test environment verification passed")
        return True
        
    except Exception as e:
        logger.error(f"Test environment verification failed: {str(e)}")
        return False

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    if verify_test_environment():
        print("Test environment verification passed")
        exit(0)
    else:
        print("Test environment verification failed")
        exit(1)
