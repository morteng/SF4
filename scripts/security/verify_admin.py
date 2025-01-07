import os
import re
from app.models.user import User
from app.extensions import db
import logging

# Configure logger
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
handler = logging.StreamHandler()
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)

def validate_password(password):
    """Validate password meets security requirements"""
    if len(password) < 12:
        logger.error("Password must be at least 12 characters")
        return False
    if not re.search(r'[A-Z]', password):
        logger.error("Password must contain at least one uppercase letter")
        return False
    if not re.search(r'[a-z]', password):
        logger.error("Password must contain at least one lowercase letter")
        return False
    if not re.search(r'[0-9]', password):
        logger.error("Password must contain at least one digit")
        return False
    if not re.search(r'[!@#$%^&*()_+=-]', password):
        logger.error("Password must contain at least one special character")
        return False
    return True

def verify_admin_user():
    """Ensure admin user exists, create from .env if missing"""
    try:
        # Check required environment variables
        required_vars = ['ADMIN_USERNAME', 'ADMIN_EMAIL', 'ADMIN_PASSWORD']
        missing_vars = [var for var in required_vars if not os.getenv(var)]
        if missing_vars:
            logger.error(f"Missing required environment variables: {', '.join(missing_vars)}")
            return False
            
        # Validate password
        if not validate_password(os.getenv('ADMIN_PASSWORD')):
            return False
            
        # Check if admin user exists
        admin = User.query.filter_by(is_admin=True).first()
        
        if not admin:
            # Create admin from .env variables
            admin = User(
                username=os.getenv('ADMIN_USERNAME'),
                email=os.getenv('ADMIN_EMAIL'),
                password=os.getenv('ADMIN_PASSWORD'),
                is_admin=True
            )
            db.session.add(admin)
            db.session.commit()
            logger.info("Created default admin user from .env")
        return True
    except Exception as e:
        logger.error(f"Failed to verify admin user: {str(e)}")
        return False

if __name__ == "__main__":
    if verify_admin_user():
        print("Admin user verification passed")
        exit(0)
    else:
        print("Admin user verification failed")
        exit(1)
