import os
import logging
from app.common.db_utils import validate_db_connection
from scripts.init_logging import configure_logging

logger = logging.getLogger(__name__)

if __name__ == "__main__":
    configure_logging()
    logging.getLogger('version_management').info("Starting database connection verification")
    db_uri = os.getenv('SQLALCHEMY_DATABASE_URI')
    if validate_db_connection(db_uri):
        print("Database connection verification passed")
        logging.getLogger('version_management').info("Database connection verification passed")
        exit(0)
    else:
        print("Database connection verification failed")
        logging.getLogger('version_management').error("Database connection verification failed")
        exit(1)
