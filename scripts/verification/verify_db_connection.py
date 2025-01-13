import os
import logging
import sys
from pathlib import Path

# Configure paths before importing project modules
project_root = str(Path(__file__).resolve().parent.parent.parent)
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from scripts.path_config import configure_paths
from scripts.init_logging import configure_logging

# Now import project modules
from app.common.db_utils import validate_db_connection

logger = logging.getLogger(__name__)

if __name__ == "__main__":
    configure_logging()
    
    # Ensure paths are configured for production
    if not configure_paths(production=True):
        logger.error("Failed to configure paths.")
        exit(1)

    logger.info("Starting database connection verification")
    db_uri = os.getenv('SQLALCHEMY_DATABASE_URI')
    if validate_db_connection(db_uri):
        print("Database connection verification passed")
        logger.info("Database connection verification passed")
        exit(0)
    else:
        print("Database connection verification failed")
        logger.error("Database connection verification failed")
        exit(1)
