import logging
from pathlib import Path

# Create logs directory if it doesn't exist
log_dir = Path('logs')
log_dir.mkdir(exist_ok=True)

# Configure root logger
try:
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
except Exception as e:
    print(f"Failed to initialize logging: {str(e)}")
    raise

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
