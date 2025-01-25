import os
import sys
import logging
from pathlib import Path

def configure_logger():
    """Configure logger for security verification"""
    logger = logging.getLogger(__name__)
    if not logger.handlers:
        handler = logging.StreamHandler()
        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        logger.setLevel(logging.INFO)
    return logger

def verify_security_patches(check_bots=False):
    """Verify recent security patches have been applied
    Args:
        check_bots (bool): Whether to verify bot security checks
    """
    logger = configure_logger()
    try:
        # Check for critical security updates
        from scripts.path_config import configure_paths
        from app.services.base_service import BaseService
        if not configure_paths():
            return False
            
        # Verify security-related packages
        import pkg_resources
        vulnerable_packages = []
        for pkg in ['flask', 'sqlalchemy', 'alembic']:
            try:
                dist = pkg_resources.get_distribution(pkg)
                if dist.has_metadata('PKG-INFO'):
                    for line in dist.get_metadata_lines('PKG-INFO'):
                        if line.startswith('Security:') and 'critical' in line.lower():
                            vulnerable_packages.append(pkg)
            except Exception:
                continue
                
        if vulnerable_packages:
            logger.error(f"Vulnerable packages found: {', '.join(vulnerable_packages)}")
            return False
            
        # Additional bot security checks
        if check_bots:
            from app.services.bot_service import TagBot, UpdateBot, ReviewBot
            for bot_class in [TagBot, UpdateBot, ReviewBot]:
                bot = bot_class()
                if not hasattr(bot, 'run'):
                    logger.error(f"Bot {bot_class.__name__} missing required run method")
                    return False
                if not hasattr(bot, 'status'):
                    logger.error(f"Bot {bot_class.__name__} missing status tracking")
                    return False
                # Initialize limiter if missing
                if 'limiter' not in BaseService.__dict__:
                    from flask_limiter import Limiter
                    from flask_limiter.util import get_remote_address
                    BaseService.limiter = Limiter(key_func=get_remote_address)
                    
        return True
    except Exception as e:
        logger.error(f"Security patch verification failed: {str(e)}")
        return False

def verify_login_attempts():
    """Check for suspicious login attempts"""
    logger = configure_logger()
    try:
        from app import create_app
        app = create_app()
        with app.app_context():
            from app.models.user import User
            from datetime import datetime, timedelta
        
        # Check for failed login attempts in last 24 hours
        recent_failures = User.query.filter(
            User.last_failed_login > datetime.utcnow() - timedelta(hours=24)
        ).count()
        
        if recent_failures > 10:
            logger.warning(f"Excessive failed logins: {recent_failures} in last 24 hours")
            return False
            
        return True
    except Exception as e:
        logger.error(f"Login attempt verification failed: {str(e)}")
        return False

def verify_security_settings(full_audit=False, daily=True, validate_keys=False, check_stipends_security=False, check_admin_interface=True, check_rate_limits=True, verify_auth=True, monitoring=False, check_bots=False, validate_limiter=True):
    # Configure paths first
    import sys
    from pathlib import Path
    sys.path.insert(0, str(Path(__file__).parent.parent.parent))
    
    from app import create_app
    app = create_app()
    with app.app_context():
        # Configure paths first
        import sys
        from pathlib import Path
        sys.path.insert(0, str(Path(__file__).parent.parent.parent))
    
    from app import create_app
    app = create_app()
    with app.app_context():
        import secrets
        import string
        random = secrets.SystemRandom()
    """Verify security-related settings with enhanced checks
    Args:
        full_audit (bool): Perform comprehensive security audit
        daily (bool): Perform daily security checks
        admin_only (bool): Focus only on admin functionality
        check_htmx_security (bool): Verify HTMX-specific security measures
    """
    # Add project root to sys.path
    project_root = str(Path(__file__).parent.parent.parent)
    if project_root not in sys.path:
        sys.path.insert(0, project_root)
    logger = configure_logger()
    
    try:
        # Configure paths first
        from scripts.path_config import configure_paths
        if not configure_paths():
            raise RuntimeError("Failed to configure paths")
            
        # Verify imports work
        import app
        import scripts
        
        # Create application context
        from app import create_app
        app = create_app()
        with app.app_context():
            # Perform security checks
            if not configure_paths():
                raise RuntimeError("Failed to configure paths")
                
            # Configure paths first
        from scripts.path_config import configure_paths
        if not configure_paths():
            raise RuntimeError("Failed to configure paths")
            
        # Enhanced SECRET_KEY validation with secure generation if missing
        secret_key = os.getenv('SECRET_KEY') or app.config.get('SECRET_KEY')
        if not secret_key or len(secret_key) < 64 or len(set(secret_key)) < 32:
            import random
            import string
            new_secret = ''.join(random.choices(
                string.ascii_letters + string.digits + string.punctuation, 
                k=64
            ))
            os.environ['SECRET_KEY'] = new_secret
            app.config['SECRET_KEY'] = new_secret
            logger.info("Generated new secure SECRET_KEY")
            
        # Set default values for missing environment variables
        default_vars = {
            'BACKUP_DIR': 'backups',
            'LOG_DIR': 'logs',
            'ADMIN_CSRF_SECRET': ''.join(random.choices(
                string.ascii_letters + string.digits + string.punctuation, 
                k=32
            ))
        }
        
        for var, default in default_vars.items():
            if not os.getenv(var):
                os.environ[var] = default
                app.config[var] = default
                logger.info(f"Set default value for {var}")
        
        # Strict debug mode verification
        if os.getenv('FLASK_ENV') == 'production':
            if os.getenv('FLASK_DEBUG', '0').lower() in ('1', 'true', 'yes'):
                logger.error("Debug mode must be disabled in production")
                # Force disable debug mode
                os.environ['FLASK_DEBUG'] = '0'
                app.config['DEBUG'] = False
                logger.info("Debug mode has been disabled")
            
        # Check password complexity
        admin_password = os.getenv('ADMIN_PASSWORD')
        if admin_password:
            if len(admin_password) < 12:
                logger.error("ADMIN_PASSWORD must be at least 12 characters")
                return False
            # Check for password complexity
            if (not any(c.isupper() for c in admin_password) or
                not any(c.islower() for c in admin_password) or
                not any(c.isdigit() for c in admin_password)):
                logger.error("ADMIN_PASSWORD must contain uppercase, lowercase and numbers")
                return False
            
        # Verify debug mode is disabled in production
        if os.getenv('FLASK_ENV') == 'production' and os.getenv('FLASK_DEBUG') == '1':
            logger.error("Debug mode must be disabled in production")
            return False
            
        # Verify environment variables including admin interface
        required_vars = [
            'FLASK_ENV',
            'FLASK_DEBUG',
            'SQLALCHEMY_DATABASE_URI',
            'SECRET_KEY',
            'ADMIN_PASSWORD',
            'BACKUP_DIR',
            'LOG_DIR',
            'ADMIN_CSRF_SECRET'
        ]
        
        # Additional admin interface checks
        if check_admin_interface:
            if not os.getenv('ADMIN_CSRF_SECRET'):
                logger.error("Missing ADMIN_CSRF_SECRET for admin interface")
                return False
            # Verify and initialize rate limiting
            if check_rate_limits:
                from app.services.base_service import BaseService
                from flask_limiter import Limiter
                from flask_limiter.util import get_remote_address
            
                if not hasattr(BaseService, 'limiter') or not isinstance(BaseService.limiter, Limiter):
                    # Initialize limiter if missing
                    BaseService.limiter = Limiter(
                        app=app,
                        key_func=get_remote_address,
                        default_limits=["200 per day", "50 per hour"]
                    )
                    logger.info("Initialized rate limiter in BaseService")
            
                # Verify active configuration
                if not BaseService.limiter.enabled:
                    logger.error("Rate limiter not enabled")
                    return False
        
        missing_vars = [var for var in required_vars if not os.getenv(var)]
        if missing_vars:
            logger.error(f"Missing required environment variables: {', '.join(missing_vars)}")
            return False
            
        # Verify and fix file permissions
        sensitive_files = {
            '.env': 0o600,
            'instance/site.db': 0o600,
            'migrations/': 0o700,
            'logs/': 0o750,
            'scripts/': 0o750
        }
        
        for file, expected_mode in sensitive_files.items():
            path = Path(file)
            if path.exists():
                mode = path.stat().st_mode & 0o777
                if mode != expected_mode:
                    try:
                        path.chmod(expected_mode)
                        logger.info(f"Fixed permissions on {file}: {oct(mode)} -> {oct(expected_mode)}")
                    except Exception as e:
                        logger.error(f"Failed to fix permissions on {file}: {str(e)}")
                        return False
                    
        # Additional daily checks
        if daily:
            # Verify recent security patches
            if not verify_security_patches(check_bots=check_bots):
                logger.error("Security patches verification failed")
                return False
                
            # Verify recent login attempts
            if not verify_login_attempts():
                logger.error("Suspicious login attempts detected")
                return False
                
        return True
    except Exception as e:
        logger.error(f"Security verification failed: {str(e)}")
        return False

if __name__ == "__main__":
    if verify_security_settings():
        exit(0)
    else:
        exit(1)
