import os
import logging
from pathlib import Path
from app.models.user import User
from app import db

logger = logging.getLogger(__name__)

def verify_admin_user():
    """Verify admin user exists and meets security requirements"""
    try:
        # Check required environment variables
        required_vars = ['ADMIN_USERNAME', 'ADMIN_EMAIL', 'ADMIN_PASSWORD']
        missing_vars = [var for var in required_vars if not os.getenv(var)]
        if missing_vars:
            logger.error(f"Missing required admin environment variables: {', '.join(missing_vars)}")
            return False
            
        # Verify password length
        admin_password = os.getenv('ADMIN_PASSWORD')
        if len(admin_password) < 12:
            logger.error("ADMIN_PASSWORD must be at least 12 characters")
            return False
            
        # Check if admin exists
        admin = User.query.filter_by(is_admin=True).first()
        if not admin:
            logger.error("No admin user found in database")
            return False
            
        # Verify credentials match
        if (admin.username != os.getenv('ADMIN_USERNAME') or
            admin.email != os.getenv('ADMIN_EMAIL') or
            not admin.check_password(os.getenv('ADMIN_PASSWORD'))):
            logger.error("Admin credentials do not match environment variables")
            return False
            
        logger.info("Admin user verification passed")
        return True
        
    except Exception as e:
        logger.error(f"Admin verification failed: {str(e)}")
        return False

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    if verify_admin_user():
        print("Admin verification successful")
        exit(0)
    else:
        print("Admin verification failed")
        exit(1)
