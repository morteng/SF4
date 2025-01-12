import os
import logging
from app.common.db_utils import validate_db_connection

logger = logging.getLogger(__name__)

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    db_uri = os.getenv('SQLALCHEMY_DATABASE_URI')
    if validate_db_connection(db_uri):
        print("Database connection verification passed")
        exit(0)
    else:
        print("Database connection verification failed")
        exit(1)
