import os
import logging
from pathlib import Path
from app.models.user import User
from app import db

logger = logging.getLogger(__name__)

def verify_admin_user(check_credentials=True, verify_access=False):
    """Enhanced admin verification with detailed diagnostics"""
    try:
        # Check required environment variables
        required_vars = ['ADMIN_USERNAME', 'ADMIN_EMAIL', 'ADMIN_PASSWORD']
        missing_vars = [var for var in required_vars if not os.getenv(var)]
        if missing_vars:
            logger.error(f"Missing required admin environment variables: {', '.join(missing_vars)}")
            return False
            
        # Verify password meets complexity requirements
        admin_password = os.getenv('ADMIN_PASSWORD')
        if len(admin_password) < 12:
            logger.error("ADMIN_PASSWORD must be at least 12 characters")
            return False
            
        # Check password complexity
        complexity_checks = [
            (any(c.isupper() for c in admin_password), "uppercase letter"),
            (any(c.islower() for c in admin_password), "lowercase letter"),
            (any(c.isdigit() for c in admin_password), "digit"),
            (any(c in '!@#$%^&*()_+-=[]{};:,.<>?/' for c in admin_password), "special character")
        ]
        
        for check, requirement in complexity_checks:
            if not check:
                logger.error(f"ADMIN_PASSWORD must contain at least one {requirement}")
                return False
            
        # Check if admin exists
        admin = User.query.filter_by(is_admin=True).first()
        if not admin:
            logger.error("No admin user found in database")
            return False
            
        # Verify credentials match if requested
        if check_credentials:
            if (admin.username != os.getenv('ADMIN_USERNAME') or
                admin.email != os.getenv('ADMIN_EMAIL') or
                not admin.check_password(os.getenv('ADMIN_PASSWORD'))):
                logger.error("Admin credentials do not match environment variables")
                return False
                
        # Verify access if requested
        if verify_access:
            from flask import current_app
            with current_app.test_request_context():
                from flask_login import login_user
                if not login_user(admin):
                    logger.error("Failed to log in admin user")
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
