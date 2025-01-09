import os
import logging
from pathlib import Path
from app.models.user import User
from app.extensions import db

logger = logging.getLogger(__name__)

def verify_admin_user():
    """Verify admin user exists and credentials are valid"""
    try:
        # Check required environment variables
        required_vars = ['ADMIN_USERNAME', 'ADMIN_EMAIL', 'ADMIN_PASSWORD']
        missing_vars = [var for var in required_vars if not os.getenv(var)]
        if missing_vars:
            logger.error(f"Missing required admin credentials: {', '.join(missing_vars)}")
            return False

        # Verify admin user exists
        admin = User.query.filter_by(username=os.getenv('ADMIN_USERNAME')).first()
        if not admin:
            logger.error("Admin user not found in database")
            return False

        # Verify admin credentials
        if not admin.check_password(os.getenv('ADMIN_PASSWORD')):
            logger.error("Admin password verification failed")
            return False

        # Verify admin permissions
        if not admin.is_admin:
            logger.error("User does not have admin privileges")
            return False

        logger.info("Admin user verification successful")
        return True

    except Exception as e:
        logger.error(f"Admin user verification failed: {str(e)}")
        return False

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    if verify_admin_user():
        print("Admin user verification passed")
        exit(0)
    else:
        print("Admin user verification failed")
        exit(1)
