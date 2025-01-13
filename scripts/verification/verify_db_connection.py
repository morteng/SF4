import os
import logging
from app.common.db_utils import validate_db_connection
from scripts.init_logging import configure_logging
import sys
from pathlib import Path

# Add project root to path
project_root = str(Path(__file__).resolve().parent.parent.parent)
if project_root not in sys.path:
    sys.path.insert(0, project_root)

logger = logging.getLogger(__name__)

if __name__ == "__main__":
    configure_logging()
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
