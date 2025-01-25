import sys
import logging
from importlib import import_module

logger = logging.getLogger(__name__)

CRITICAL_DEPS = [
    'bleach',
    'markdown',
    'flask_htmx',
    'sqlalchemy',
    'flask_wtf',
    'wtforms',
    'flask_limiter'
]

def verify_dependencies():
    """Verify presence of critical dependencies"""
    missing = []
    for dep in CRITICAL_DEPS:
        try:
            import_module(dep)
            logger.info(f"Found dependency: {dep}")
        except ImportError:
            missing.append(dep)
            logger.warning(f"Missing dependency: {dep}")
    
    if missing:
        logger.error(f"Missing critical dependencies: {', '.join(missing)}")
        print("\nERROR: Missing required packages. Install with:")
        print(f"python -m pip install {' '.join(missing)}\n")
        return False
        
    return True

if __name__ == '__main__':
    from scripts.init_logging import configure_logging
    configure_logging()
    if verify_dependencies():
        print("All critical dependencies verified")
        sys.exit(0)
    else:
        sys.exit(1)
