import logging
from pathlib import Path

def configure_logging(production=False, verify=False):
    """Configure logging system with proper error handling"""
    try:
        # Add project root to path
        import sys
        from pathlib import Path
        project_root = str(Path(__file__).resolve().parent.parent.parent)
        if project_root not in sys.path:
            sys.path.insert(0, project_root)
            
        # Configure paths first
        from scripts.path_config import configure_paths
        if not configure_paths(production=production):
            raise RuntimeError("Failed to configure paths")
            
        # Create logs directory with proper permissions
        log_dir = Path('logs')
        log_dir.mkdir(exist_ok=True, mode=0o755)
            
        # Create logs directory with proper permissions
        log_dir = Path('logs')
        log_dir.mkdir(exist_ok=True, mode=0o755)
        
        # Configure root logger
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('logs/app.log'),
                logging.StreamHandler()
            ]
        )
        
        # Configure log rotation
        from logging.handlers import RotatingFileHandler
        handler = RotatingFileHandler(
            'logs/app.log',
            maxBytes=1024*1024,  # 1MB
            backupCount=5
        )
        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)
        logging.getLogger().addHandler(handler)
        
        # Verify logging setup
        logging.getLogger(__name__).info("Logging system initialized successfully")
        return True
    except Exception as e:
        print(f"Failed to initialize logging: {str(e)}")
        return False

# Initialize logging when module is imported
if not configure_logging():
    raise RuntimeError("Failed to initialize logging system")

# Create specific loggers
for logger_name in ['app', 'tests', 'bots']:
    logger = logging.getLogger(logger_name)
    logger.setLevel(logging.INFO)
    handler = logging.FileHandler(f'logs/{logger_name}.log')
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)
    logger.addHandler(handler)

# Verify logging setup
logging.getLogger(__name__).info("Logging system initialized successfully")
