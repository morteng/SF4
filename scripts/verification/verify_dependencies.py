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
    'flask_limiter',
    'croniter',  # Added missing dependency
    'scripts'    # Ensure scripts package is accessible
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
    import sys
    from pathlib import Path
    project_root = Path(__file__).parent.parent
    sys.path.insert(0, str(project_root.resolve()))  # Normalized path
    sys.path.insert(1, str(project_root / '.venv' / 'Lib' / 'site-packages'))
    
    import sys
    from pathlib import Path
    sys.path.insert(0, str(Path(__file__).parent.parent.parent))  # Add project root

    from scripts.init_logging import configure_logging
    configure_logging()
    if verify_dependencies():
        print("All critical dependencies verified")
        sys.exit(0)
    else:
        sys.exit(1)
