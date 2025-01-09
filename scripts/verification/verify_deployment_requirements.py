import os
import logging
from pathlib import Path

logger = logging.getLogger(__name__)

def verify_requirements():
    """Verify all deployment requirements are met"""
    requirements = [
        ('SQLALCHEMY_DATABASE_URI', "Database URI not configured"),
        ('SECRET_KEY', "Secret key not configured"),
        ('ADMIN_USERNAME', "Admin username not configured"),
        ('ADMIN_PASSWORD', "Admin password not configured"),
        ('RENDER_API_KEY', "Render API key not configured")
    ]
    
    for var, error_msg in requirements:
        if not os.getenv(var):
            logger.error(error_msg)
            return False
            
    # Verify SECRET_KEY length
    if len(os.getenv('SECRET_KEY')) < 64:
        logger.error("SECRET_KEY must be at least 64 characters")
        return False
        
    # Verify ADMIN_PASSWORD length
    if len(os.getenv('ADMIN_PASSWORD')) < 12:
        logger.error("ADMIN_PASSWORD must be at least 12 characters")
        return False
        
    return True

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    if verify_requirements():
        print("Deployment requirements verified")
        exit(0)
    else:
        print("Deployment requirements verification failed")
        exit(1)
