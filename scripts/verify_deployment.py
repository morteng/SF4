import sys
import os
import logging
from pathlib import Path

# Configure logger at module level
logger = logging.getLogger(__name__)
handler = logging.StreamHandler()
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)
logger.setLevel(logging.INFO)

# Add project root to Python path
project_root = str(Path(__file__).parent.parent)
if project_root not in sys.path:
    sys.path.insert(0, project_root)
    
# Add scripts directory to Python path
scripts_dir = str(Path(__file__).parent)
if scripts_dir not in sys.path:
    sys.path.insert(0, scripts_dir)

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
    secret_key = os.getenv('SECRET_KEY')
    
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

def verify_deployment(*args, **kwargs):
    """Verify all deployment requirements are met"""
    global logger
    logger = logging.getLogger(__name__)
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
        logging.error(f"Missing environment variables: {', '.join(missing_vars)}")
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
