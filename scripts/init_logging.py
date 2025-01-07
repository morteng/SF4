import logging
from pathlib import Path

def configure_logging():
    """Configure logging system with proper error handling"""
    try:
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
