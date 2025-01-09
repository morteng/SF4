import sys
import os
import logging
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

# Configure logger at module level
logger = logging.getLogger(__name__)
handler = logging.StreamHandler()
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)
logger.setLevel(logging.INFO)

# Configure paths first
from scripts.path_config import configure_paths
if not configure_paths():
    logger.error("Path configuration failed")
    exit(1)

def verify_security_settings():
    """Verify security-related settings with enhanced checks"""
    try:
        secret_key = os.getenv('SECRET_KEY')
        if not secret_key or len(secret_key) < 64:
            logger.error("SECRET_KEY must be at least 64 characters")
            return False
            
        # Check for required character types
        complexity_checks = [
            (any(c.isupper() for c in secret_key), "uppercase letter"),
            (any(c.islower() for c in secret_key), "lowercase letter"),
            (any(c.isdigit() for c in secret_key), "digit"),
            (any(c in '!@#$%^&*()_+-=[]{};:,.<>?/' for c in secret_key), "special character")
        ]
        
        for check, requirement in complexity_checks:
            if not check:
                logger.error(f"SECRET_KEY must contain at least one {requirement}")
                return False
                
        return True
    except Exception as e:
        logger.error(f"Security verification failed: {str(e)}")
        return False
    
    # Verify version file
    from scripts.version import validate_version, get_version
    if not validate_version(get_version()):
        logger.error("Version validation failed")
        return False
        
    # Validate SECRET_KEY length and complexity
    if not secret_key or len(secret_key) < 64:
        logger.error("SECRET_KEY must be at least 64 characters")
        return False
        
    # Check for required character types
    complexity_checks = [
        (any(c.isupper() for c in secret_key), "uppercase letter"),
        (any(c.islower() for c in secret_key), "lowercase letter"),
        (any(c.isdigit() for c in secret_key), "digit"),
        (any(c in '!@#$%^&*()_+-=[]{};:,.<>?/' for c in secret_key), "special character")
    ]
    
    for check, requirement in complexity_checks:
        if not check:
            logging.error(f"SECRET_KEY must contain at least one {requirement}")
            return False
            
    # Check for common insecure patterns
    insecure_patterns = [
        'password', '123456', 'qwerty', 'admin',
        'secret', 'stipend', 'flask', 'render'
    ]
    
    if any(pattern.lower() in secret_key.lower() for pattern in insecure_patterns):
        logging.error("SECRET_KEY contains insecure patterns")
        return False
        
    # Verify SECRET_KEY rotation
    if os.path.exists('.secret_key_history'):
        with open('.secret_key_history') as f:
            if secret_key in f.read():
                logger.error("SECRET_KEY has not been rotated recently")
                return False
                
    return True

def verify_db_connection():
    """Verify database connection"""
    try:
        from scripts.verify_db_connection import verify_db_connection as verify_db
        return verify_db()
    except Exception as e:
        logger.error(f"Database connection verification failed: {str(e)}")
        return False

def verify_test_coverage():
    """Verify test coverage meets requirements"""
    try:
        from scripts.verify_test_coverage import verify_coverage
        return verify_coverage()
    except Exception as e:
        logger.error(f"Test coverage verification failed: {str(e)}")
        return False

def verify_deployment(*args, **kwargs):
    """Enhanced deployment verification with proper error handling"""
    try:
        # Configure logging
        logger = configure_logger()
        
        # Verify version
        from scripts.version import validate_version
        if not validate_version():
            logger.error("Version validation failed")
            return False
            
        # Verify security settings
        if not verify_security_settings():
            logger.error("Security verification failed")
            return False
            
        # Verify database connection
        if not verify_db_connection():
            logger.error("Database connection verification failed")
            return False
            
        logger.info("Deployment verification passed")
        return True
    except Exception as e:
        logger.error(f"Deployment verification failed: {str(e)}")
        return False
        
    # Verify admin user if requested
    if kwargs.get('check_type') == 'check-admin':
        from scripts.verify_admin import verify_admin_user
        return verify_admin_user()
        
    # Final deployment check
    if kwargs.get('check_type') == 'final-check':
        checks = [
            verify_security_settings(),
            verify_environment(),
            verify_version(),
            verify_db_connection(),
            verify_test_coverage()
        ]
        return all(checks)
    if not logger.handlers:
        handler = logging.StreamHandler()
        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        logger.setLevel(logging.INFO)
    if not logger.handlers:
        handler = logging.StreamHandler()
        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        logger.setLevel(logging.INFO)
        
    check_type = kwargs.get('check_type', 'full')
    
    try:
        if check_type == 'check-security':
            return verify_security_settings()
        elif check_type == 'check-env':
            return verify_environment()
        elif check_type == 'check-version':
            return verify_version()
        else:
            # Full verification
            return (verify_security_settings() and 
                    verify_environment() and 
                    verify_version())
            
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

def verify_environment():
    """Verify environment variables"""
    required_vars = [
        'FLASK_ENV',
        'FLASK_DEBUG', 
        'SQLALCHEMY_DATABASE_URI',
        'SECRET_KEY',
        'RENDER_API_KEY'
    ]
    
    missing_vars = [var for var in required_vars if var not in os.environ]
    if missing_vars:
        logger.error(f"Missing environment variables: {', '.join(missing_vars)}")
        return False
    return True

def verify_version():
    """Verify version file exists and is valid"""
    try:
        from scripts.version import validate_version, get_version
        version = get_version()
        if not validate_version(version):
            logging.error("Version validation failed")
            return False
        return True
    except Exception as e:
        logging.error(f"Version verification failed: {str(e)}")
        return False

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    if verify_deployment():
        print("Deployment verification passed")
        exit(0)
    else:
        print("Deployment verification failed")
        exit(1)
