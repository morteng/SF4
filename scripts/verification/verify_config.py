import os
import logging
from pathlib import Path

def configure_logger():
    """Configure logger for config verification"""
    logger = logging.getLogger(__name__)
    if not logger.handlers:
        handler = logging.StreamHandler()
        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        logger.setLevel(logging.INFO)
    return logger

def verify_config():
    """Verify critical configuration settings"""
    logger = configure_logger()
    
    try:
        from app.config import Config, ProductionConfig
        
        # Verify SECRET_KEY
        if not Config.SECRET_KEY or len(Config.SECRET_KEY) < 64:
            logger.error("SECRET_KEY must be at least 64 characters")
            return False
            
        # Verify ProductionConfig inherits properly
        if not hasattr(ProductionConfig, 'WTF_CSRF_SECRET_KEY'):
            logger.error("Missing WTF_CSRF_SECRET_KEY in ProductionConfig")
            return False
            
        # Verify database URI
        if not ProductionConfig.SQLALCHEMY_DATABASE_URI:
            logger.error("Missing SQLALCHEMY_DATABASE_URI")
            return False
            
        logger.info("Configuration verification passed")
        return True
        
    except Exception as e:
        logger.error(f"Configuration verification failed: {str(e)}")
        return False

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    if verify_config():
        print("Configuration verification passed")
        exit(0)
    else:
        print("Configuration verification failed")
        exit(1)
